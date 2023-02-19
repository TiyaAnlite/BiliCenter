import time
import queue
import logging

import redis
from bilicenter_middleware.statement4SQL import make_update_query, make_insert_query

# 运行时查找
from jobs import Jobs


def elec_query(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 电费信息
    if callback["code"] == 200:
        nowtime = int(time.time())
        # 按分计算，将获得数据转换为分
        balance = int("".join(callback["data"]["balance"].split(".")))
        balance_diff = callback["attach"]["last_balance"] - balance
        sql_queue.put(make_update_query("zj_elec_room", dict(balance=balance, timestamp=nowtime),
                                        dict(id=callback["job"]["data"]["kwargs"]["room_id"])))
        if callback["attach"]["last_balance"] != 0:  # 0为初始化时采用值
            sql_queue.put(make_insert_query("zj_elec_room_log", dict(id=callback["job"]["data"]["kwargs"]["room_id"],
                                                                     balance_diff=balance_diff, timestamp=nowtime)))
        logger.info(
            f"Room {callback['job']['data']['kwargs']['room_id']}: {callback['data']['balance']}, diff {balance_diff}")
    else:
        logger.error(f"Elec query failed: {callback}")


CALLBACK_INFO = {
    Jobs.Beitou.Elec.query: elec_query
}
