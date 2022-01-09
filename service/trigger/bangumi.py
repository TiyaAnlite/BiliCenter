import logging

import redis

from bilicenter_middleware.event import new_event, Sources

# 运行时查找
from jobs import Jobs


def on_meta(rules_data: list, r: redis.StrictRedis, logger: logging.Logger):
    # rules per rows: [mid]
    data = rules_data[0]
    logger.info(f"[Bangumi]Updating {len(data)} bangumi")
    for row in data:
        e = new_event(Jobs.BiliCenter.Bangumi.meta, dict(media_id=row[0]), Sources.TriggerEvent)
        e.push(r)


def on_rank(rules_data: list, r: redis.StrictRedis, logger: logging.Logger):
    logger.info("[Bangumi]Updating bangumi rank")
    e = new_event(Jobs.BiliCenter.Bangumi.pgcRank, dict(), Sources.TriggerEvent)
    e.push(r)


TRIGGER_INFO = {
    "bangumi": on_meta,
    "bangumi_rank": on_rank
}
