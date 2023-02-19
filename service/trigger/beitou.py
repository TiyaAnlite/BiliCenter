import logging

import redis

from bilicenter_middleware.event import new_event, Sources

# 运行时查找
from jobs import Jobs


def on_elec_query(rules_data: list, r: redis.StrictRedis, logger: logging.Logger):
    # rules per rows: [id, balance]
    data = rules_data[0]
    logger.info(f"Updating {len(data)} rooms")
    for row in data:
        room_id, last_balance = row
        e = new_event(Jobs.Beitou.Elec.query, dict(room_id=room_id), Sources.TriggerEvent,
                      dict(last_balance=last_balance))
        e.push(r)


TRIGGER_INFO = {
    "beitou_elec": on_elec_query
}
