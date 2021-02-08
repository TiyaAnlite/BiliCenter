import json
import uuid
import random

import redis

from event2job import deploy_job


class Channels(object):
    """各中间件频道帮助类"""
    ConcurrentController = "pub_biliCenter_Events"
    CallbackCenter = "pub_biliCenter_callbacks"


class Sources(object):
    """标志中间件来源的帮助类"""
    ApiEvent = bytes([0x1, 0x1]).hex()  # API接口
    TriggerEvent = bytes([0x1, 0x2]).hex()  # 前端触发器

    ConcurrentController = bytes([0x2, 0x1]).hex()  # 并发控制器
    CallbackCenter = bytes([0x2, 0x2]).hex()  # 回调处理中心


def new_event(jobs: str, kwargs: dict, source: str) -> dict:
    """
    生成一个事件\n
    **不包含eid**\n
    :param jobs: 任务名(可用SCFJobs帮助类快速获取)
    :param kwargs: 传入参数
    :param source: 事件来源(可用Sources帮助类快速获取)
    :return:
    """
    return {
        "source": source,
        "job": deploy_job(jobs, kwargs)
    }


def push_event(r: redis.StrictRedis, event: dict) -> str:
    """
    推送一个事件至并发中心\n
    **自动生成edi**\n
    :param r: Redis连接
    :param event: 需要推送的事件
    :return: 事件ID
    """

    eid = str(uuid.uuid5(uuid.uuid1(), "".join(random.choices("0123456789ABCDEF", k=3))))
    event_data = dict(eid=eid, **event)
    r.publish(Channels.ConcurrentController, json.dumps(event_data))
    return eid
