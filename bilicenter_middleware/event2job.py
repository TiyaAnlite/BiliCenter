# 路径：从并发中心部署任务到SCF分布式容器

import os
import json

import bilibili_api


class SCFJobs(object):
    # 任务序列化帮助类
    bangumi_meta = "bangumi_meta"
    bangumi_episodes_list = "bangumi_episodes_list"
    bangumi_episode_info = "bangumi_episode_info"

    jobs = {
        "bangumi_meta": bilibili_api.bangumi.get_meta,
        "bangumi_episodes_list": bilibili_api.bangumi.get_episodes_list,
        "bangumi_episode_info": bilibili_api.bangumi.get_episode_info
    }


def get_scf_name():
    return os.getenv("BILICENTER_SCFNAME")


def get_scf_namespace():
    return os.getenv("BILICENTER_SCFNAMESPACE")


def deploy_job(jobs: str, kwargs: dict) -> dict:
    """
    生成部署任务所需参数\n
    :param jobs: 任务名(可用SCFJobs帮助类快速获取)
    :param kwargs: 传入参数
    :return: 可供scf SDK直接invoke()的任务数据
    """

    event = {
        "job_type": jobs,
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

    resp = SCFJobs.jobs[job_data["job_type"]](**job_data["kwargs"])
    return json.loads(resp)
