import os
import json
import queue
import importlib
import collections

import redis
import pymysql

import logger


class CallbackCenter(object):
    """
    **回调/处理中心**\n
    *接受并发中心的回调事件，并传递至绑定的处理函数完成数据处理与持久化*
    """

    def __init__(self, log_file="BiliCenter.log", debug=False):
        if debug:
            self.logger = logger.Logger.get_file_debug_logger("CallbackCenter", log_file)
        else:
            self.logger = logger.Logger.get_file_log_logger("CallbackCenter", log_file)
        self.logger.info("Starting CallbackCenter")
        self.callback_func = collections.defaultdict(lambda: self.__default_callback)
        self.callback_discovery()

        redis_config = json.loads(os.getenv("BILICENTER_REDIS_KWARGS"))
        redis_config.update({"decode_responses": True})
        self.redis_pool = redis.ConnectionPool(**redis_config)
        self.logger.info("Connect to redis")
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)

        self.logger.info("Connect to MySQL")
        self.sql = pymysql.connect(**json.loads(os.getenv("BILICENTER_MYSQL_KWARGS")))

    def get_sql_cursor(self):
        """获得SQL游标对象用于执行语句(带自动重连)"""
        try:
            self.sql.ping()
            return self.sql.cursor()
        except pymysql.err.Error:
            self.logger.info("Reconnect to MySQL")
            self.sql = pymysql.connect(**json.loads(os.getenv("BILICENTER_MYSQL_KWARGS")))
            return self.sql.cursor()

    def callback_discovery(self):
        """回调函数发现与注册"""
        module = []
        for file in os.listdir("callback"):
            s = os.path.splitext(file)
            if s[1] == ".py":
                module.append(s[0])
        for m in module:
            loaded_module = importlib.import_module(f"callback.{m}")
            self.logger.info(f"discovery: {m}")
            for k, v in loaded_module.CALLBACK_INFO.items():
                self.logger.info(f"register {v} to {k}")
                self.callback_func[k] = v

    @staticmethod
    def __default_callback(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logger.logging.Logger):
        """
        默认回调函数\n
        :param callback: 回调事件信息
        :param r: Redis连接
        :param sql_queue: SQL执行队列(不支持查询)
        :param logger: 日志记录对象
        """
        logger.warning(f"Unknown jobs: {callback}")


if __name__ == '__main__':
    o = CallbackCenter()
