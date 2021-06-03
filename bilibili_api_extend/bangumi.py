import json
from . import utils

import bilibili_api


def get_rank_pgc(verify: bilibili_api.utils.Verify = None):
    """
    获得番剧排行榜 - 匹配排行榜中番剧区数据,day=3
    :param verify:
    :return:
    """

    if verify is None:
        verify = bilibili_api.utils.Verify()
    api = "https://api.bilibili.com/pgc/web/rank/list"
    params = {
        "season_type": 1,
        "day": 3
    }
    resp = bilibili_api.utils.get(api, params=params, cookies=verify.get_cookies(), headers=utils.DEFAULT_HEADERS)
    return resp


def get_rank_region(verify: bilibili_api.utils.Verify = None):
    """
        获得番剧排行榜 - 匹配番剧区中热门排行榜数据,day=7
        :param verify:
        :return:
        """

    if verify is None:
        verify = bilibili_api.utils.Verify()
    api = "https://api.bilibili.com/x/web-interface/ranking/region"
    params = {
        "rid": 33,
        "day": 7,
        "original": 0
    }
    resp = bilibili_api.utils.get(api, params=params, cookies=verify.get_cookies())
    return resp


EXTEND_MODULE = [
    get_rank_pgc
]
