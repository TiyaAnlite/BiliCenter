import time
import queue
import logging

import redis
from bilicenter_middleware.event import SCFJobs, Sources, new_event
from bilicenter_middleware.statement4SQL import make_update_query


def meta(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    if callback["code"] == 200:
        mid = callback["data"]["media"]["media_id"]
        sid = callback["data"]["media"]["season_id"]
        query = "INSERT INTO `status_bangumi` (mid,sid) VALUES (%s,%s) ON DUPLICATE KEY UPDATE sid=%s"
        args = [mid, sid, sid]
        sql_queue.put((query, args))

        update_data = {
            "title": callback["data"]["media"]["title"],
            "s_index": callback["data"]["media"]["new_ep"]["index"],
            "index_show": callback["data"]["media"]["new_ep"]["index_show"]
        }
        if "rating" in callback["data"]["media"]:
            update_data["score_people"] = callback["data"]["media"]["rating"]["count"]
            update_data["score"] = callback["data"]["media"]["rating"]["score"]
        sql_queue.put(make_update_query("status_bangumi", update_data, dict(mid=mid)))
        logger.info(f"Update bangumi mid->sid: {mid}->{sid}")
        # 生成事件InteractData, CollectiveInfo
        event_interact = new_event(SCFJobs.bangumi_interact_data, dict(season_id=sid), Sources.CallbackCenter)
        eid = event_interact.push(r)
        logger.info(f"Pushed new [InteractData] event {eid}")
        event_collective = new_event(SCFJobs.bangumi_collective_info, dict(season_id=sid), Sources.CallbackCenter)
        eid = event_collective.push(r)
        logger.info(f"Pushed new [CollectiveInfo] event {eid}")


def interact(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    if callback["code"] == 200:
        sid = callback["job"]["data"]["kwargs"]["season_id"]
        update_data = {
            "follow": callback["data"]["follow"],
            "series_follow": callback["data"]["series_follow"],
            "views": callback["data"]["views"],
            "danmakus": callback["data"]["danmakus"],
            "timestamp": int(time.time())
        }
        sql_queue.put(make_update_query("status_bangumi", update_data, dict(sid=sid)))
        logger.info(f"Update interact at {sid}")


def collective(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    if callback["code"] == 200:
        sid = callback["job"]["data"]["kwargs"]["season_id"]
        update_data = {
            "is_started": callback["data"]["publish"]["is_started"],
            "is_finish": callback["data"]["publish"]["is_finish"],
            "timestamp": int(time.time())
        }
        sql_queue.put(make_update_query("status_bangumi", update_data, dict(sid=sid)))
        logger.info(f"Update collective at {sid}")


CALLBACK_INFO = {
    SCFJobs.bangumi_meta: meta,
    SCFJobs.bangumi_interact_data: interact,
    SCFJobs.bangumi_collective_info: collective
}

print("Reg.")
