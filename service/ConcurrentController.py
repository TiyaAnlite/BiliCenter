import os
import json
import queue
import threading

import redis
from tencentserverless import scf
from tencentserverless.exception import TencentServerlessSDKException
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

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
        self.main_lock = threading.Lock()  # 主线程资源锁

        self.event_queue = queue.Queue()  # 主事件队列
        self.scf_client = queue.Queue(self.scf_max)
        [self.scf_client.put((i, scf.Client())) for i in range(self.scf_max)]  # 初始化客户端池

        self.listener = threading.Thread(target=self.thread_event_listener)
        self.listener.setName("Listener")
        self.listener.setDaemon(True)

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
        redis_pub.subscribe(Channels.ConcurrentController)  # 订阅事件
        for event in redis_pub.listen():
            if event["type"] == "message":
                event_data = json.loads(event["data"])
                self.logger.debug(f"Recv event {event_data['eid']} from {Sources.sources[event_data['source']]}")
                self.event_queue.put(event_data)

    def thread_event_handler(self, client_id: int, client: scf.Client, event: dict):
        """事件处理.并发线程"""
        self.logger.info(f"SCF job:{event['eid']}")
        resp_data = client.invoke(**event['job'])
        print(resp_data)
        self.scf_client.put((client_id, client))  # 回收客户端

    def thread_event_callback(self):
        """事件结果回调线程"""
        pass

    def main(self):
        """主线程"""
        self.listener.start()
        self.logger.info("Ready to accept event")
        try:
            while True:
                event = self.event_queue.get()
                client = self.scf_client.get()
                handler = threading.Thread(target=self.thread_event_handler,
                                           kwargs=dict(client_id=client[0], client=client[1], event=event))
                handler.setName(f"EventHandler({client[0]})")
                handler.start()
        except KeyboardInterrupt:
            self.logger.info("Quit by user.")
            exit(0)


if __name__ == '__main__':
    controller = ConcurrentController()
    controller.main()
