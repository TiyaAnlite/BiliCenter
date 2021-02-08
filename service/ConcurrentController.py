import os
import json
import queue
import threading

import redis
from tencentserverless import scf
from tencentserverless.exception import TencentServerlessSDKException
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

from logger import Logger


class ConcurrentController(object):
    """
    **并发中心(控制器)**\n
    *接收来自各个中间件的事件，并转换为SCF任务进行部署和管理*\n
    """

    def __init__(self, log_file="ConcurrentController", debug=False):
        if debug:
            self.logger = Logger.get_file_debug_logger("ConcurrentController", log_file)
        else:
            self.logger = Logger.get_file_log_logger("ConcurrentController", log_file)
        self.logger.info("Starting ConcurrentController")

        self.redis_pool = redis.ConnectionPool(**json.loads(os.getenv("BILICENTER_REDIS_KWARGS")))
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)
        self.scf_max = int(self.redis.hget("config", "ConcurrentController.max"))
        self.main_lock = threading.Lock()  # 主线程资源锁

        self.event_queue = queue.Queue()
        self.scf_client = queue.Queue(self.scf_max)
        [self.scf_client.put_nowait(scf.Client()) for i in range(self.scf_max)]  # 初始化客户端池

    def thread_event_listener(self):
        """事件接受线程"""
        pass

    def thread_event_handler(self):
        """事件处理.并发线程"""
        pass

    def main(self):
        """主线程"""
        pass