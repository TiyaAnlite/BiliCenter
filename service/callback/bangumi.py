import queue
import logging

import redis
from bilicenter_middleware.event import SCFJobs


def episodes_list(callback: dict, r: redis.StrictRedis, sql_queue: queue.Queue, logger: logging.Logger):
    episodes = callback["data"]["main_section"]["episodes"]
    sid = callback["job"]["data"]["kwargs"]["season_id"]
    for ep in episodes:
        query = "INSERT INTO `episodes` (`sid`, `aid`, `id`, `title`, `long_title`) VALUES (%s, %s, %s, %s, %s)"
        args = [sid, ep["aid"], ep["id"], ep["title"], ep["long_title"]]
        sql_queue.put((query, args))
    logger.info(f"Updated {sid} -> {len(episodes)} videos")


CALLBACK_INFO = {
    SCFJobs.bangumi_episodes_list: episodes_list
}

print("Reg.")
