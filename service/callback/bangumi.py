import time
import queue
import logging

import redis
from bilicenter_middleware.event import SCFJobs, Sources, new_event
from bilicenter_middleware.statement4SQL import make_update_query, make_insert_query


def meta(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    if callback["code"] == 200:
        mid = callback["data"]["media"]["media_id"]
        sid = callback["data"]["media"]["season_id"]
        bangumi_meta = {
            "mid": mid,
            "sid": sid
        }
        sql_queue.put(make_insert_query("status_bangumi", bangumi_meta, safety_mode=True, update=True))

        bangumi_data = {
            "title": callback["data"]["media"]["title"],
            "s_index": callback["data"]["media"]["new_ep"]["index"],
            "index_show": callback["data"]["media"]["new_ep"]["index_show"]
        }
        if "rating" in callback["data"]["media"]:
            bangumi_data["score_people"] = callback["data"]["media"]["rating"]["count"]
            bangumi_data["score"] = callback["data"]["media"]["rating"]["score"]
        sql_queue.put(make_update_query("status_bangumi", bangumi_data, dict(mid=mid)))
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
        interact_data = {
            "follow": callback["data"]["follow"],
            "series_follow": callback["data"]["series_follow"],
            "views": callback["data"]["views"],
            "danmakus": callback["data"]["danmakus"],
            "timestamp": int(time.time())
        }
        sql_queue.put(make_update_query("status_bangumi", interact_data, dict(sid=sid)))
        logger.info(f"Update interact at {sid}")


def collective(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    if callback["code"] == 200:
        sid = callback["job"]["data"]["kwargs"]["season_id"]
        collective_data = {
            "is_started": callback["data"]["publish"]["is_started"],
            "is_finish": callback["data"]["publish"]["is_finish"],
            "timestamp": int(time.time())
        }
        sql_queue.put(make_update_query("status_bangumi", collective_data, dict(sid=sid)))
        logger.info(f"Update collective at {sid}, {len(callback['data']['episodes'])} videos")
        for ep in callback["data"]["episodes"]:
            ep_map = {
                "aid": ep["aid"],
                "sid": sid,
                "s_index": ep["title"]
            }
            sql_queue.put(make_insert_query("map_episodes", ep_map, safety_mode=True))
            event_aid = new_event(SCFJobs.video_info_simple, dict(bvid=ep["bvid"]), Sources.CallbackCenter,
                                  attach=dict(pub=ep["pub_time"]))
            event_aid.push(r)


CALLBACK_INFO = {
    SCFJobs.bangumi_meta: meta,
    SCFJobs.bangumi_interact_data: interact,
    SCFJobs.bangumi_collective_info: collective,
}
