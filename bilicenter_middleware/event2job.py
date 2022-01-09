# 路径：从并发中心部署任务到SCF分布式容器

import os
from .exceptions import CenterException


def get_scf_name():
    return os.getenv("BILICENTER_SCFNAME")


def get_scf_namespace():
    return os.getenv("BILICENTER_SCFNAMESPACE")


def deploy_job(job_key: str, kwargs: dict) -> dict:
    """
    生成部署任务所需参数\n
    :param job_key: 任务名(任务统一化键)
    :param kwargs: 传入参数
    :return: 可供scf SDK直接invoke()的任务数据
    """

    event = {
        "job_key": job_key,
        "kwargs": kwargs
    }
    return {
        "function_name": get_scf_name(),
        "namespace": get_scf_namespace(),
        "qualifier": os.getenv("BILICENTER_SCFQUALIFIER") if os.getenv("BILICENTER_SCFQUALIFIER") else "$LATEST",
        "data": event
    }


def accept_job(job_data: dict, job_map: dict) -> dict:
    """
    接收SCF事件，调用请求接口获得数据\n
    需要注意处理相关异常\n
    :param job_data: 任务请求和数据
    :param job_map: 任务注册表
    :return: 请求返回的数据
    """

    job_type = job_data["job_key"]
    if job_type in job_map:
        resp = job_map[job_type](**job_data["kwargs"])
        return resp
    else:
        raise CenterException(f"Unknown job:{job_type}", 500)
