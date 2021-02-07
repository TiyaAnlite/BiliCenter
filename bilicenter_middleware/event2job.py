# 路径：从并发中心部署任务到SCF分布式容器

import os
import json
import base64
from functools import partial

import bilibili_api


class SCFJobs(object):
    # 任务序列化帮助类
    bangumi_meta = bytes([0x1, 0x1])
    bangumi_interact_data = bytes([0x1, 0x2])
    bangumi_episodes_list = bytes([0x1, 0x3])
    bangumi_episode_info = bytes([0x1, 0x4])
    video_info = bytes([0x2, 0x1])
    video_info_simple = bytes([0x2, 0x2])

    jobs = {
        bangumi_meta: bilibili_api.bangumi.get_meta,
        bangumi_interact_data: bilibili_api.bangumi.get_interact_data,
        bangumi_episodes_list: bilibili_api.bangumi.get_episodes_list,
        bangumi_episode_info: bilibili_api.bangumi.get_episode_info,
        video_info: bilibili_api.video.get_video_info,
        video_info_simple: partial(bilibili_api.video.get_video_info, is_simple=True)
    }


def get_scf_name():
    return os.getenv("BILICENTER_SCFNAME")


def get_scf_namespace():
    return os.getenv("BILICENTER_SCFNAMESPACE")


def deploy_job(jobs: bytes, kwargs: dict) -> dict:
    """
    生成部署任务所需参数\n
    :param jobs: 任务名(可用SCFJobs帮助类快速获取)
    :param kwargs: 传入参数
    :return: 可供scf SDK直接invoke()的任务数据
    """

    event = {
        "job_codec": base64.b64encode(jobs).decode(),
        "kwargs": kwargs
    }
    return {
        "function_name": get_scf_name(),
        "namespace": get_scf_namespace(),
        "data": event
    }


def accept_job(job_data: dict) -> dict:
    """
    调用请求接口获得数据\n
    :param job_data: 任务请求和数据
    :return: 请求返回的数据
    """

    job_type = base64.b64decode(job_data["job_codec"])
    resp = SCFJobs.jobs[job_type](**job_data["kwargs"])
    return json.loads(resp)
