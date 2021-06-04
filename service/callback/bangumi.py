import time
import queue
import logging

import redis
from bilicenter_middleware.event import SCFJobs, Sources, new_event
from bilicenter_middleware.statement4SQL import make_update_query, make_insert_query


def meta(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 元数据：mid与sid，剧集信息，评分信息
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
        # 为InteractData附加score信息
        attch_score = None
        if "rating" in callback["data"]["media"]:
            attch_score = {
                "score_people": callback["data"]["media"]["rating"]["count"],
                "score": callback["data"]["media"]["rating"]["score"]
            }
        event_interact = new_event(SCFJobs.bangumi_interact_data, dict(season_id=sid), Sources.CallbackCenter,
                                   attach=attch_score)
        eid = event_interact.push(r)
        # logger.info(f"Pushed new [InteractData] event {eid}")
        event_collective = new_event(SCFJobs.bangumi_collective_info, dict(season_id=sid), Sources.CallbackCenter)
        eid = event_collective.push(r)
        # logger.info(f"Pushed new [CollectiveInfo] event {eid}")


def interact(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 互动信息：整体播放订阅弹幕，bangumi的logs实现部分
    if callback["code"] == 200:
        sid = callback["job"]["data"]["kwargs"]["season_id"]
        interact_data = {
            "follow": callback["data"]["follow"],
            "series_follow": callback["data"]["series_follow"],
            "views": callback["data"]["views"],
            "danmakus": callback["data"]["danmakus"],
            "timestamp": int(time.time())
        }
        log_bangumi_data = {
            "sid": sid,
            "score_people": 0,
            "score": 0
        }
        log_bangumi_data.update(interact_data)
        if callback["attach"]:
            log_bangumi_data.update(callback["attach"])
        sql_queue.put(make_update_query("status_bangumi", interact_data, dict(sid=sid)))
        sql_queue.put(make_insert_query("logs_bangumi", log_bangumi_data))
        logger.info(f"Update bangumi interact at {sid}")


def collective(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 更新sid番剧映射表
    # 剧集扩展信息：开播完结状态，记录剧集信息，发起剧集链式调用
    # 根据attach传入特殊动作，关闭链式调用与剧集信息记录
    if callback["code"] == 200:
        # sid = callback["job"]["data"]["kwargs"]["season_id"]
        sid = callback["data"]["season_id"]
        sid_map_data = {
            "mid": callback["data"]["media_id"],
            "sid": sid,
            "title": callback["data"]["title"]
        }
        sql_queue.put(make_insert_query("map_media", sid_map_data, safety_mode=True))
        if not callback["attach"].get("map_update"):
            # 原路径
            collective_data = {
                "is_started": callback["data"]["publish"]["is_started"],
                "is_finish": callback["data"]["publish"]["is_finish"],
                "timestamp": int(time.time())
            }
            sql_queue.put(make_update_query("status_bangumi", collective_data, dict(sid=sid)))
            logger.info(f"Update bangumi collective at {sid}, {len(callback['data']['episodes'])} videos")
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


def rank(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 番剧排行榜
    if callback["code"] == 200:
        nowtime = int(time.time())
        logger.info(f"Update ranklist: {len(callback['data']['list'])}")
        for bangumi in callback["data"]["list"]:
            # 这里暂时不加入title，先更新logs表
            rank_data = {
                "rank": bangumi["rank"],
                "pts": bangumi["pts"],
                "sid": bangumi["season_id"],
                "danmakus": bangumi["stat"]["danmaku"],
                "follow": bangumi["stat"]["follow"],
                "series_follow": bangumi["stat"]["series_follow"],
                "views": bangumi["stat"]["view"],
                "timestamp": nowtime
            }
            sql_queue.put(make_insert_query("logs_bangumi_rank", rank_data))
            rank_data.update({
                "title": bangumi["title"]
            })
            sql_queue.put(make_insert_query("status_bangumi_rank", rank_data, safety_mode=True, update=True))
            e = new_event(SCFJobs.bangumi_collective_info, dict(season_id=bangumi["season_id"]), Sources.CallbackCenter,
                          attach=dict(map_update=True))
            e.push(r)


CALLBACK_INFO = {
    SCFJobs.bangumi_meta: meta,
    SCFJobs.bangumi_interact_data: interact,
    SCFJobs.bangumi_collective_info: collective,
    SCFJobs.bangumi_rank: rank
}
