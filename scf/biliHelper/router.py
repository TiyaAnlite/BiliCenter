from bilicenter_middleware.discovery import auto_register
from bilicenter_middleware.logger import Logger
from bilicenter_middleware.event2job import accept_job
from bilicenter_middleware.exceptions import CenterException
from bilibili_api.exceptions import BilibiliException, NetworkException, BilibiliApiException

LOGGER = Logger.get_logger("SCF")


def main_route(event, context):
    resdata = {
        "code": 200,
        "msg": "ok",
        "rid": context["request_id"],
        "data": None
    }
    job_map = auto_register(dict(), "job", LOGGER)
    try:
        resdata["data"] = accept_job(event, job_map)
    except NetworkException as err:
        resdata["msg"] = "请求失败"
        resdata["code"] = abs(err.code)
    except BilibiliException as err:
        resdata["msg"] = err.msg
        resdata["code"] = abs(err.code)
    except BilibiliApiException as err:
        resdata["msg"] = err.msg
        resdata["code"] = 500
    except CenterException as err:
        resdata.update(err.return_callback())

    return resdata
