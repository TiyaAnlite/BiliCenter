import os
import logging
import importlib


def discoverer(area: str, logger: logging.Logger):
    """
    模块服务发现\n
    **模块必须放在同级目录中指定文件夹下**\n
    :param area: 指定模块区域文件夹
    :param logger: 日志对象
    :return: [生成器](k, v)
    """

    module = []
    for file in os.listdir(area):
        s = os.path.splitext(file)
        if s[1] == ".py":
            module.append(s[0])
    for m in module:
        loaded_module = importlib.import_module(f"{area}.{m}")
        logger.info(f"Discovery: {m}")
        for k, v in getattr(loaded_module, f"{area.upper()}_INFO", dict()).items():
            yield k, v


def auto_register(d: dict, area: str, logger: logging.Logger):
    """
    模块服务自动注册\n
    **模块必须放在同级目录中指定文件夹下**\n
    :param d: 服务表
    :param area: 指定模块区域文件夹
    :param logger: 日志对象
    :return: 已注册的服务表
    """

    for k, v in discoverer(area, logger):
        logger.info(f"Register {v} to {k}")
        d[k] = v
    return d
