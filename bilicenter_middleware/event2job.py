# 路径：从并发中心部署任务到SCF分布式容器

import os
from functools import partial

import bilibili_api
import bilibili_api_extend


class SCFJobs(object):
    # 任务序列化帮助类
    main_recommend = bytes([0x0, 0x1]).hex()
    bangumi_meta = bytes([0x1, 0x1]).hex()
    bangumi_collective_info = bytes([0x1, 0x2]).hex()
    bangumi_interact_data = bytes([0x1, 0x3]).hex()
    bangumi_episodes_list = bytes([0x1, 0x4]).hex()
    bangumi_episode_info = bytes([0x1, 0x5]).hex()
    bangumi_rank = bytes([0x1, 0x6]).hex()
    video_info = bytes([0x2, 0x1]).hex()
    video_info_simple = bytes([0x2, 0x2]).hex()

    jobs = {
        main_recommend: bilibili_api_extend.common.get_recommend,
        bangumi_meta: bilibili_api.bangumi.get_meta,
        bangumi_collective_info: bilibili_api.bangumi.get_collective_info,
        bangumi_interact_data: bilibili_api.bangumi.get_interact_data,
        bangumi_episodes_list: bilibili_api.bangumi.get_episodes_list,
        bangumi_episode_info: bilibili_api.bangumi.get_episode_info,
        bangumi_rank: bilibili_api_extend.bangumi.get_rank_pgc,
        video_info: bilibili_api.video.get_video_info,
        video_info_simple: partial(bilibili_api.video.get_video_info, is_simple=True)
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
        "job_codec": jobs,
        "kwargs": kwargs
    }
    return {
        "function_name": get_scf_name(),
        "namespace": get_scf_namespace(),
        "qualifier": os.getenv("BILICENTER_SCFQUALIFIER") if os.getenv("BILICENTER_SCFQUALIFIER") else "$LATEST",
        "data": event
    }


def accept_job(job_data: dict) -> dict:
    """
    调用请求接口获得数据\n
    需要注意处理相关异常\n
    :param job_data: 任务请求和数据
    :return: 请求返回的数据
    """

    job_type = job_data["job_codec"]
    resp = SCFJobs.jobs[job_type](**job_data["kwargs"])
    return resp
