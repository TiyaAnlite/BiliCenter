import os
import sys
import time
import json
import queue
import threading
import collections
from queue import Empty as queue_Empty

import redis
import pymysql

if "../" not in sys.path:
    sys.path.append("../")
from bilicenter_middleware.event import Channels
from bilicenter_middleware.discovery import auto_register
import logger


class CallbackCenter(object):
    """
    **回调/处理中心**\n
    *接受并发中心的回调事件，并传递至绑定的处理函数完成数据处理与持久化*
    """

    def __init__(self, log_file="BiliCenter_callbackCenter.log", debug=False):
        threading.current_thread().setName("Main")
        if debug:
            self.logger = logger.Logger.get_file_debug_logger("CallbackCenter", log_file)
        else:
            self.logger = logger.Logger.get_file_log_logger("CallbackCenter", log_file)
        self.logger.info("Starting CallbackCenter")
        self.callback_func = auto_register(collections.defaultdict(lambda: self.__default_callback), "callback",
                                           self.logger)
        self.callback_queue = queue.Queue()  # 回调信息队列
        self.sql_queue = queue.Queue()  # SQL异步执行队列(不支持查询) | (SQL, args,)
        self.main_lock = threading.Lock()  # 公共变量锁

        redis_config = json.loads(os.getenv("BILICENTER_REDIS_KWARGS"))
        redis_config.update({"decode_responses": True})
        self.redis_pool = redis.ConnectionPool(**redis_config)
        self.logger.info("Connect to redis")
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)

        sql_config = json.loads(os.getenv("BILICENTER_MYSQL_KWARGS"))
        sql_config.update({"read_timeout": 10, "write_timeout": 10})
        self.logger.info("Connect to MySQL")
        self.sql = pymysql.connect(**sql_config)

        # 初始化相关子线程
        self.thr_accept = threading.Thread(target=self.thread_callback_accept)
        self.thr_accept.setDaemon(True)
        self.thr_accept.setName("Listener")

        self.thr_callback = threading.Thread(target=self.thread_callback_handler)
        self.thr_callback.setDaemon(True)
        self.thr_callback.setName("Callback")

        self.thr_sync = threading.Thread(target=self.thread_sql_sync)
        self.thr_sync.setDaemon(True)
        self.thr_sync.setName("SQL Sync")

    def get_sql_cursor(self):
        """获得SQL游标对象用于执行语句(带自动重连)"""
        with self.main_lock:
            try:
                self.sql.ping()
            except pymysql.err.Error:
                self.logger.info("Reconnect to MySQL")
                self.sql = pymysql.connect(**json.loads(os.getenv("BILICENTER_MYSQL_KWARGS")))
        return self.sql.cursor()

    @staticmethod
    def __default_callback(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, log: logger.logging.Logger):
        """
        默认回调函数\n
        :param callback: 回调事件信息
        :param r: Redis连接
        :param sql_queue: SQL执行队列(不支持查询)
        :param log: 日志记录对象
        """
        log.warning(f"Unknown jobs: {callback}")

    def thread_callback_accept(self):
        """回调接受线程"""
        r = redis.StrictRedis(connection_pool=self.redis_pool)
        redis_pub = r.pubsub()
        self.logger.info("Subscribe callback channels")
        redis_pub.subscribe(Channels.CallbackCenter)
        for callback in redis_pub.listen():
            if callback["type"] == "message":
                try:
                    callback_data = json.loads(callback["data"])
                except json.JSONDecodeError:
                    self.logger.error(f"Unexpect data: {callback['data']}")
                else:
                    if callback_data["code"] == 200:
                        self.callback_queue.put(callback_data)
                    else:
                        self.logger.warning(
                            f"Received an error callback: [{callback_data['code']}]{callback_data['msg']}")
                        self.logger.info(f"Callback: {callback_data}")

    def thread_callback_handler(self):
        """回调处理线程"""
        self.logger.info("Callback handler started")
        while True:
            callback = self.callback_queue.get()
            with redis.StrictRedis(connection_pool=self.redis_pool) as call_r:
                # 调用回调处理函数
                try:
                    self.callback_func[callback["job"]["data"]["job_codec"]](callback, call_r, self.sql_queue,
                                                                             self.logger)
                except Exception as err:
                    self.logger.error("Callback func error:")
                    self.logger.exception(err)

    def thread_sql_sync(self):
        """SQL执行队列同步线程"""
        while True:
            sql = [self.sql_queue.get()]  # 等待第一个SQL语句
            try:
                while True:
                    sql.append(self.sql_queue.get(True, 5))  # 等待后续语句5秒窗口期
            except queue_Empty:
                # 窗口期过，开始同步
                self.logger.info(f"SQL sync begin: {len(sql)}")
                start = time.perf_counter()
                with self.get_sql_cursor() as cursor:
                    self.sql.begin()
                    for query, args in sql:
                        try:
                            cursor.execute(query, args)
                        except pymysql.err.DatabaseError as err:
                            self.logger.error(f"Execute error: {query} -> {args}")
                            self.logger.error(err)
                    self.sql.commit()
                self.logger.info(f"Sync done.({round(time.perf_counter() - start, 3)}s)")
            except Exception as err:
                self.logger.error("Some error at thread_sql_sync")
                self.logger.exception(err)
                self.sql_queue.put(sql)

    def main(self):
        """主线程"""
        self.thr_accept.start()
        self.thr_callback.start()
        self.thr_sync.start()
        self.logger.info("Ready to accept callback")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            self.logger.info("User exit.")


if __name__ == '__main__':
    center = CallbackCenter()
    center.main()
