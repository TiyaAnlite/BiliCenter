class Jobs:
    """任务统一键描述类"""

    class BiliCenter:
        """BiliCenter主要数据挖掘任务"""
        recommend = "biliCenter.recommend"

        class Bangumi:
            """番剧信息类任务"""
            meta = "biliCenter.bangumi.meta"
            collective = "biliCenter.bangumi.collective"
            interact = "biliCenter.bangumi.interact"
            episodesList = "biliCenter.bangumi.episodesList"
            episode = "biliCenter.bangumi.episode"
            pgcRank = "biliCenter.bangumi.pgcRank"

        class Video:
            """视频信息类任务"""
            info = "biliCenter.video.info"
            infoSimple = "biliCenter.video.infoSimple"
