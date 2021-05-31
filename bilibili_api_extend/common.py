import re
import json
from . import utils

import bilibili_api

import requests


def get_index_inital_state(verify: bilibili_api.utils.Verify = None) -> dict:
    """
    拉取主站主页初始化信息(总成)
    :param verify:
    :return:
    """

    if verify is None:
        verify = bilibili_api.utils.Verify()
    resp = requests.get("https://www.bilibili.com/", cookies=verify.get_cookies(), headers=utils.DEFAULT_HEADERS)
    if resp.status_code != 200:
        raise bilibili_api.exceptions.NetworkException(resp.status_code)
    pattern = re.compile(r"window.__INITIAL_STATE__=(\{.*?\});")
    match = re.search(pattern, resp.content.decode())
    if match is None:
        raise bilibili_api.exceptions.BilibiliApiException("未找到番剧信息")
    try:
        content = json.loads(match.group(1))
    except json.JSONDecodeError:
        raise bilibili_api.exceptions.BilibiliApiException("信息解析错误")
    return content


def get_recommend(verify: bilibili_api.utils.Verify = None) -> list:
    """
    获取首页推荐
    :param verify:
    :return:
    """
    if verify is None:
        verify = bilibili_api.utils.Verify()
    inital_state = get_index_inital_state(verify)
    return inital_state["recommendData"]["item"]


EXTEND_MODULE = [
    get_index_inital_state,
    get_recommend
]
