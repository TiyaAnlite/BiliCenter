import os
import sys
import time
import json
import queue
import threading

import redis
from tencentserverless import scf
from tencentserverless.exception import TencentServerlessSDKException
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

if "../" not in sys.path:
    sys.path.append("../")
from bilicenter_middleware.event import Channels, Sources
from logger import Logger


class ConcurrentController(object):
    """
    **并发中心(控制器)**\n
    *接收来自各个中间件的事件，并转换为SCF任务进行部署和管理*\n
    """

    def __init__(self, log_file="ConcurrentController.log", debug=False):
        threading.current_thread().setName("Main")
        if debug:
            self.logger = Logger.get_file_debug_logger("ConcurrentController", log_file)
        else:
            self.logger = Logger.get_file_log_logger("ConcurrentController", log_file)
        self.logger.info("Starting ConcurrentController")

        redis_config = json.loads(os.getenv("BILICENTER_REDIS_KWARGS"))
        redis_config.update({"decode_responses": True})
        self.redis_pool = redis.ConnectionPool(**redis_config)
        self.logger.info("Connect to redis")
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)  # 这是给主线程用的Redis连接对象
        self.init_redis()
        self.scf_max = int(self.redis.hget("config", "ConcurrentController.max"))
        self.logger.info(f"SCF Concurrent max is {self.scf_max}")

        self.event_queue = queue.Queue()  # 主事件队列(try_count, event)
        self.event_callback_queue = queue.Queue()  # 事件回调队列
        self.scf_client = queue.Queue(self.scf_max)
        [self.scf_client.put((i, scf.Client())) for i in range(self.scf_max)]  # 初始化客户端池

        # 初始化子线程
        self.thr_listen = threading.Thread(target=self.thread_event_listener)
        self.thr_listen.setName("Listener")
        self.thr_listen.setDaemon(True)

        self.thr_controller = threading.Thread(target=self.thread_event_controller)
        self.thr_controller.setName("Controller")
        self.thr_controller.setDaemon(True)

        self.thr_callback = threading.Thread(target=self.thread_event_callback)
        self.thr_callback.setName("Callback")
        self.thr_callback.setDaemon(True)

    def init_redis(self):
        """初始化Redis配置"""
        if not self.redis.exists("config") or self.redis.type("config") != "hash":
            self.logger.info("Initialize redis config")
            pipe = self.redis.pipeline()
            pipe.delete("config")
            with open("redisConfig.json") as fp:
                config = json.load(fp)
            for k, v in config.items():
                pipe.hset("config", k, v)
            pipe.execute()
            self.logger.critical("Initialized default config, confirm and restart manual.")
            exit(0)

    def thread_event_listener(self):
        """事件接受线程"""
        r = redis.StrictRedis(connection_pool=self.redis_pool)
        redis_pub = r.pubsub()
        self.logger.info(f"Subscribe event channels")
        redis_pub.subscribe(Channels.ConcurrentController)  # 订阅事件
        for event in redis_pub.listen():
            if event["type"] == "message":
                event_data = json.loads(event["data"])
                self.logger.debug(f"Recv event {event_data['eid']} from {Sources.sources[event_data['source']]}")
                self.event_queue.put((0, event_data))

    def thread_event_controller(self):
        """事件调度线程，代替主线程并发行为避免阻塞"""
        self.logger.info("Controller started")
        while True:
            client = self.scf_client.get()
            try_count, event = self.event_queue.get()
            handler = threading.Thread(target=self.thread_event_handler,
                                       kwargs=dict(client_id=client[0], client=client[1], event=event,
                                                   try_count=try_count))
            handler.setName(f"EventHandler({client[0]})")
            handler.start()

    def thread_event_handler(self, client_id: int, client: scf.Client, event: dict, try_count: int):
        """事件处理.并发线程"""
        self.logger.info(f"SCF job{f'(try {try_count})' if try_count else ''}:{event['eid']}")
        try:
            callback = json.loads(client.invoke(**event['job']))
            callback.update(event)
            # print(callback)
            if callback["code"] == 412 or callback["code"] == 500:  # 访问封禁或请求错误
                self.logger.error(f"SCF {callback['code']}: {callback['msg']}")
                self.__event_try(try_count, event, callback)
            else:  # 以下直接回调
                self.event_callback_queue.put(callback)  # 回调事件
                if callback["code"] != 200:  # 其他非正常返回
                    self.logger.error(f"SCF {callback['code']}: {callback['msg']}")
                    with redis.StrictRedis(connection_pool=self.redis_pool) as r:
                        self.to_logs(r, f"SCF {callback['code']}", callback)
        except TencentServerlessSDKException as err:  # SCF执行错误
            self.logger.error("SDK invoke error")
            self.logger.exception(err)
            callback = {
                "code": 500,
                "msg": "TencentServerlessSDKException",
                "rid": err.get_request_id(),
                "data": {
                    "code": err.get_code(),
                    "msg": err.get_message(),
                    "stack_trace": err.get_stack_trace()
                }
            }
            callback.update(event)
            self.__event_try(try_count, event, callback)
        except TencentCloudSDKException as err:  # SDK请求错误
            self.logger.error("SDK error")
            self.logger.exception(err)
            log = {
                "code": err.get_code(),
                "msg": err.get_message(),
                "rid": err.get_request_id()
            }
            log.update(event)
            with redis.StrictRedis(connection_pool=self.redis_pool) as r:
                self.to_logs(r, "SCF SDK error", log)
            self.event_queue.put((try_count, event))  # 重试
        self.scf_client.put((client_id, client))  # 回收客户端

    def __event_try(self, try_count: int, event: dict, callback: dict):
        """事件异常重试相关组件，控制进行重试或者直接回调"""
        if try_count >= 3:  # 超过重试，回调
            self.event_callback_queue.put(callback)
            with redis.StrictRedis(connection_pool=self.redis_pool) as r:
                r.lpush("dead_letter", json.dumps(callback))  # 死信队列
        else:
            self.event_queue.put((try_count + 1, event))  # 发起有限重试

    def thread_event_callback(self):
        """事件结果回调线程"""
        r = redis.StrictRedis(connection_pool=self.redis_pool)
        self.logger.info("Ready to callback event")
        while True:
            callback = self.event_callback_queue.get()
            r.publish(Channels.CallbackCenter, json.dumps(callback))

    def to_logs(self, r: redis.StrictRedis, msg_type: str, content: dict):
        """记录警告日志"""
        log = {
            "timestamp": int(time.time()),
            "msg_type": msg_type,
            "content": content
        }
        self.logger.warning(f"[{msg_type}] -> {content}")
        r.lpush("logs", json.dumps(log, ensure_ascii=False))

    def main(self):
        """主线程"""
        self.thr_listen.start()
        self.thr_controller.start()
        self.thr_callback.start()
        self.logger.info("Ready to accept event")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("Quit by user.")
            exit(0)


if __name__ == '__main__':
    controller = ConcurrentController()
    controller.main()
