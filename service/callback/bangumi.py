import queue
import logging

import redis
from bilicenter_middleware.event2job import SCFJobs


def episodes_list(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    pass


CALLBACK_INFO = {
    SCFJobs.bangumi_episodes_list: episodes_list
}

print("Reg.")
