import time
import queue
import logging

import redis
from bilicenter_middleware.statement4SQL import make_insert_query

# 运行时查找
from jobs import Jobs


def simple_video(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    # 简单视频信息：包含视频数据相关纬度内容，video的logs实现部分
    if callback["code"] == 200:
        # logger.info(f"Update {callback['data']['bvid']}(av{callback['data']['aid']})")
        video_data = {
            "aid": callback["data"]["aid"],
            "bvid": callback["data"]["bvid"],
            "view": callback["data"]["view"] if callback["data"]["view"] > 0 else 0,
            "danmaku": callback["data"]["danmaku"] if callback["data"]["danmaku"] > 0 else 0,
            "reply": callback["data"]["reply"] if callback["data"]["reply"] > 0 else 0,
            "favorite": callback["data"]["favorite"] if callback["data"]["favorite"] > 0 else 0,
            "coin": callback["data"]["coin"] if callback["data"]["coin"] > 0 else 0,
            "share": callback["data"]["share"] if callback["data"]["share"] > 0 else 0,
            "liked": callback["data"]["like"] if callback["data"]["like"] > 0 else 0,
            "releaseTimestamp": callback["attach"]["pub"],
            "timestamp": int(time.time())
        }
        logs_video_data = video_data.copy()
        del logs_video_data["bvid"]
        del logs_video_data["releaseTimestamp"]
        sql_queue.put(make_insert_query("stat_video", video_data, safety_mode=True, update=True))
        sql_queue.put(make_insert_query("logs_video", logs_video_data))


CALLBACK_INFO = {
    Jobs.BiliCenter.Video.infoSimple: simple_video
}
