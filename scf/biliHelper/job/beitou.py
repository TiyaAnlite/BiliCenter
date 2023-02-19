import json

import requests
from bilibili_api.utils import DEFAULT_HEADERS

from bilicenter_middleware.exceptions import CenterException

# 运行时查找
from jobs import Jobs


def elec_query(room_id: int):
    resp = requests.post("http://card.beitoucloud.com/zhujiang_elec/v1/cgElec/elec/query", data=dict(room_id=room_id),
                         headers=DEFAULT_HEADERS.copy())
    if resp.ok:
        try:
            data = resp.json()
        except json.JSONDecodeError:
            raise CenterException(f"Not json data: {resp.text}", 500)
        for except_key, except_code in zip(("retCode", "resultCode", "code"), (200, 0, 200)):
            if data[except_key] != except_code:
                raise CenterException(f"Unexpected {except_key}[{except_code}]:{data}")
        return data["data"]
    else:
        raise CenterException(f"Network exception: {resp.status_code}", resp.status_code)


JOB_INFO = {
    Jobs.Beitou.Elec.query: elec_query
}
