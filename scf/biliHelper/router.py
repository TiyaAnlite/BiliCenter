from bilicenter_middleware.event2job import accept_job
from bilibili_api.exceptions import BilibiliException, NetworkException, BilibiliApiException


def main_route(event, context):
    resdata = {
        "code": 200,
        "msg": "ok",
        "rid": context["request_id"],
        "data": None
    }
    try:
        resdata["data"] = accept_job(event)
    except NetworkException as err:
        resdata["msg"] = "请求失败"
        resdata["code"] = abs(err.code)
    except BilibiliException as err:
        resdata["msg"] = err.msg
        resdata["code"] = abs(err.code)
    except BilibiliApiException as err:
        resdata["msg"] = err.msg
        resdata["code"] = 500

    return resdata
