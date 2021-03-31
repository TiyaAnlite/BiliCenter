import time
import queue
import logging

import redis
from bilicenter_middleware.event import SCFJobs
from bilicenter_middleware.statement4SQL import make_insert_query


def simple_video(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 简单视频信息：包含视频数据相关纬度内容，video的logs实现部分
    if callback["code"] == 200:
        # logger.info(f"Update {callback['data']['bvid']}(av{callback['data']['aid']})")
        video_data = {
            "aid": callback["data"]["aid"],
            "bvid": callback["data"]["bvid"],
            "view": callback["data"]["view"],
            "danmaku": callback["data"]["danmaku"],
            "reply": callback["data"]["reply"],
            "favorite": callback["data"]["favorite"],
            "coin": callback["data"]["coin"],
            "share": callback["data"]["share"],
            "liked": callback["data"]["like"],
            "releaseTimestamp": callback["attach"]["pub"],
            "timestamp": int(time.time())
        }
        logs_video_data = video_data.copy()
        del logs_video_data["bvid"]
        del logs_video_data["releaseTimestamp"]
        sql_queue.put(make_insert_query("stat_video", video_data, safety_mode=True, update=True))
        sql_queue.put(make_insert_query("logs_video", logs_video_data))


CALLBACK_INFO = {
    SCFJobs.video_info_simple: simple_video
}
