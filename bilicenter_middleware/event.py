import time
import json
import uuid
import random

import redis

from .event2job import deploy_job


class Channels(object):
    """各中间件频道帮助类"""
    ConcurrentController = "biliCenter_pub_Events"
    CallbackCenter = "biliCenter_pub_callbacks"


class Sources(object):
    """标志中间件来源的帮助类"""
    ApiEvent = bytes([0x1, 0x1]).hex()  # API接口
    TriggerEvent = bytes([0x1, 0x2]).hex()  # 前端触发器

    ConcurrentController = bytes([0x2, 0x1]).hex()  # 并发控制器
    CallbackCenter = bytes([0x2, 0x2]).hex()  # 回调处理中心

    sources = {
        ApiEvent: "ApiEvent",
        TriggerEvent: "TriggerEvent",
        ConcurrentController: "ConcurrentController",
        CallbackCenter: "CallbackCenter"
    }


class Event(object):
    """事件类"""

    def __init__(self, job_key: str, kwargs: dict, source: str, attach: dict = None, scf: bool = True):
        self.source = source
        self.attach = attach
        if not self.attach:
            self.attach = dict()
        self.is_scf_job = scf
        self.job = deploy_job(job_key, kwargs)

    def push(self, r: redis.StrictRedis) -> str:
        """
        推送一次该事件至并发中心\n
        **每次推送自动生成eid**\n
        :param r: Redis连接
        :return: 事件ID
        """
        eid = str(uuid.uuid5(uuid.uuid1(), "".join(random.choices("0123456789ABCDEF", k=3))))
        event_data = dict(eid=eid, source=self.source, job=self.job, attach=self.attach, scf=self.is_scf_job,
                          event_timestamp=int(time.time()))
        r.publish(Channels.ConcurrentController, json.dumps(event_data))
        return eid


def new_event(job_key: str, kwargs: dict, source: str, attach: dict = None, scf: bool = True) -> Event:
    """
    生成一个事件\n
    **不包含eid**\n
    :param job_key: 任务名(任务统一化键)
    :param kwargs: 传入参数
    :param source: 事件来源(可用Sources帮助类快速获取)
    :param attach: 事件附加信息，类型强制为dict，会原样返回给回调信息
    :param scf: 是否为发往SCF的任务
    :return: Event
    """
    return Event(job_key, kwargs, source, attach, scf)
