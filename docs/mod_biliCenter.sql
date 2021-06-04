/*
SQLyog Ultimate v13.1.1 (64 bit)
MySQL - 8.0.23 : Database - biliCenter
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
/*Table structure for table `logs_bangumi` */

CREATE TABLE `logs_bangumi` (
  `sid` int unsigned NOT NULL COMMENT '番剧season id',
  `score` float unsigned NOT NULL COMMENT '评分',
  `score_people` int unsigned NOT NULL COMMENT '点评人数',
  `follow` int unsigned NOT NULL COMMENT '追番',
  `series_follow` int unsigned NOT NULL COMMENT '系列追番',
  `views` int unsigned NOT NULL COMMENT '播放',
  `danmakus` int unsigned NOT NULL COMMENT '弹幕',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int unsigned NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`sid`,`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='番剧信息历史数据';

/*Table structure for table `logs_bangumi_rank` */

CREATE TABLE `logs_bangumi_rank` (
  `rank` tinyint unsigned NOT NULL COMMENT '排名',
  `pts` int unsigned NOT NULL COMMENT '综合分数',
  `sid` int unsigned NOT NULL COMMENT '番剧season id',
  `danmakus` int unsigned NOT NULL COMMENT '弹幕',
  `follow` int unsigned NOT NULL COMMENT '追番',
  `series_follow` int unsigned NOT NULL COMMENT '系列追番',
  `views` int unsigned NOT NULL COMMENT '播放',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int unsigned NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`rank`,`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `logs_video` */

CREATE TABLE `logs_video` (
  `aid` int unsigned NOT NULL COMMENT '视频av号链接',
  `view` int unsigned NOT NULL COMMENT '单集播放',
  `danmaku` int unsigned NOT NULL COMMENT '单集弹幕',
  `reply` int unsigned NOT NULL COMMENT '单集评论',
  `favorite` int unsigned NOT NULL COMMENT '单集收藏',
  `coin` int unsigned NOT NULL COMMENT '单集投币',
  `share` int unsigned NOT NULL COMMENT '单集分享',
  `liked` int unsigned NOT NULL COMMENT '单集收藏',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int unsigned NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`aid`,`timestamp`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='视频信息历史数据';

/*Table structure for table `map_episodes` */

CREATE TABLE `map_episodes` (
  `aid` int unsigned NOT NULL COMMENT '视频av号',
  `sid` int unsigned NOT NULL COMMENT '番剧season id链接',
  `s_index` varchar(10) NOT NULL COMMENT '剧集',
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='番剧单集-av号映射表';

/*Table structure for table `map_media` */

CREATE TABLE `map_media` (
  `mid` int unsigned NOT NULL COMMENT '番剧页面media id',
  `sid` int unsigned NOT NULL COMMENT '番剧season id',
  `title` text NOT NULL COMMENT '标题',
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Table structure for table `stat_video` */

CREATE TABLE `stat_video` (
  `aid` int NOT NULL COMMENT '视频av号',
  `bvid` char(12) NOT NULL COMMENT '视频BV号',
  `view` int NOT NULL COMMENT '播放',
  `danmaku` int NOT NULL COMMENT '弹幕',
  `reply` int NOT NULL COMMENT '评论',
  `favorite` int NOT NULL COMMENT '收藏',
  `coin` int NOT NULL COMMENT '投币',
  `share` int NOT NULL COMMENT '分享',
  `liked` int NOT NULL COMMENT '点赞',
  `releaseTimestamp` int NOT NULL COMMENT '发布时间',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`aid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='视频信息表';

/*Table structure for table `status_bangumi` */

CREATE TABLE `status_bangumi` (
  `mid` int unsigned NOT NULL COMMENT '番剧页面media id',
  `sid` int unsigned DEFAULT NULL COMMENT '番剧season id',
  `title` text COMMENT '标题',
  `score` float unsigned DEFAULT NULL COMMENT '评分',
  `score_people` int unsigned DEFAULT NULL COMMENT '点评人数',
  `follow` int unsigned DEFAULT NULL COMMENT '追番',
  `series_follow` int unsigned DEFAULT NULL COMMENT '系列追番',
  `views` int unsigned DEFAULT NULL COMMENT '播放',
  `danmakus` int unsigned DEFAULT NULL COMMENT '弹幕',
  `s_index` varchar(10) DEFAULT NULL COMMENT '集数',
  `index_show` text COMMENT '页面更新状态展示',
  `is_started` tinyint unsigned DEFAULT NULL COMMENT '开播状态',
  `is_finish` tinyint unsigned DEFAULT NULL COMMENT '完结状态',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int unsigned NOT NULL COMMENT '更新时间戳',
  `watch` tinyint unsigned NOT NULL DEFAULT '1' COMMENT '系统监视标志',
  PRIMARY KEY (`mid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='番剧信息表';

/*Table structure for table `status_bangumi_rank` */

CREATE TABLE `status_bangumi_rank` (
  `rank` tinyint unsigned NOT NULL COMMENT '排名',
  `pts` int unsigned NOT NULL COMMENT '综合分数',
  `sid` int unsigned NOT NULL COMMENT '番剧season id',
  `title` text NOT NULL COMMENT '番剧标题',
  `danmakus` int unsigned NOT NULL COMMENT '弹幕',
  `follow` int unsigned NOT NULL COMMENT '追番',
  `series_follow` int unsigned NOT NULL COMMENT '系列追番',
  `views` int unsigned NOT NULL COMMENT '播放',
  `timestamp_view` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间戳(观察用)',
  `timestamp` int unsigned NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`rank`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='番剧排行榜信息表';

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
