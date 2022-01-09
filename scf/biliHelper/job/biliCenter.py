from functools import partial

import bilibili_api
import bilibili_api_extend

# 运行时查找
from jobs import Jobs

JOB_INFO = {
    Jobs.BiliCenter.recommend: bilibili_api_extend.common.get_recommend,
    Jobs.BiliCenter.Bangumi.meta: bilibili_api.bangumi.get_meta,
    Jobs.BiliCenter.Bangumi.collective: bilibili_api.bangumi.get_collective_info,
    Jobs.BiliCenter.Bangumi.interact: bilibili_api.bangumi.get_interact_data,
    Jobs.BiliCenter.Bangumi.episodesList: bilibili_api.bangumi.get_episodes_list,
    Jobs.BiliCenter.Bangumi.episode: bilibili_api.bangumi.get_episode_info,
    Jobs.BiliCenter.Bangumi.pgcRank: bilibili_api_extend.bangumi.get_rank_pgc,
    Jobs.BiliCenter.Video.info: bilibili_api.video.get_video_info,
    Jobs.BiliCenter.Video.infoSimple: partial(bilibili_api.video.get_video_info, is_simple=True)
}
