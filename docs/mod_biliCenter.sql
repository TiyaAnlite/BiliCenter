create table if not exists logs_bangumi
(
    sid            int unsigned                       not null comment '番剧season id',
    score          float unsigned                     not null comment '评分',
    score_people   int unsigned                       not null comment '点评人数',
    follow         int unsigned                       not null comment '追番',
    series_follow  int unsigned                       not null comment '系列追番',
    views          int unsigned                       not null comment '播放',
    danmakus       int unsigned                       not null comment '弹幕',
    timestamp_view datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp      int unsigned                       not null comment '更新时间戳',
    primary key (sid, timestamp)
)
    comment '番剧信息历史数据';

create table if not exists logs_bangumi_rank
(
    `rank`         tinyint(1) unsigned                not null comment '排名',
    pts            int unsigned                       not null comment '综合分数',
    sid            int unsigned                       not null comment '番剧season id',
    danmakus       int unsigned                       not null comment '弹幕',
    follow         int unsigned                       not null comment '追番',
    series_follow  int unsigned                       not null comment '系列追番',
    views          int unsigned                       not null comment '播放',
    timestamp_view datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp      int unsigned                       not null comment '更新时间戳',
    primary key (`rank`, timestamp)
);

create table if not exists logs_video
(
    aid            int unsigned                       not null comment '视频av号链接',
    view           int unsigned                       not null comment '播放',
    danmaku        int unsigned                       not null comment '弹幕',
    reply          int unsigned                       not null comment '评论',
    favorite       int unsigned                       not null comment '收藏',
    coin           int unsigned                       not null comment '投币',
    share          int unsigned                       not null comment '分享',
    liked          int unsigned                       not null comment '收藏',
    timestamp_view datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp      int unsigned                       not null comment '更新时间戳',
    primary key (aid, timestamp)
)
    comment '视频信息历史数据';

create table if not exists map_episodes
(
    aid     int unsigned not null comment '视频av号',
    sid     int unsigned not null comment '番剧season id链接',
    s_index varchar(10)  not null comment '剧集',
    primary key (aid, sid)
)
    comment '番剧单集-av号映射表';

create table if not exists map_media
(
    mid   int unsigned not null comment '番剧页面media id',
    sid   int unsigned not null comment '番剧season id',
    title varchar(128) not null comment '标题',
    primary key (mid, sid)
);

create table if not exists stat_video
(
    aid              int(11) unsigned                   not null comment '视频av号'
        primary key,
    bvid             char(12)                           not null comment '视频BV号',
    view             int(11) unsigned                   not null comment '播放',
    danmaku          int(11) unsigned                   not null comment '弹幕',
    reply            int(11) unsigned                   not null comment '评论',
    favorite         int(11) unsigned                   not null comment '收藏',
    coin             int(11) unsigned                   not null comment '投币',
    share            int(11) unsigned                   not null comment '分享',
    liked            int(11) unsigned                   not null comment '点赞',
    releaseTimestamp int(11) unsigned                   not null comment '发布时间',
    timestamp_view   datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp        int(11) unsigned                   not null comment '更新时间戳'
)
    comment '视频信息表';

create table if not exists status_bangumi
(
    mid            int unsigned                               not null comment '番剧页面media id'
        primary key,
    sid            int unsigned                               null comment '番剧season id',
    title          varchar(128)                               null comment '标题',
    score          float unsigned                             null comment '评分',
    score_people   int unsigned                               null comment '点评人数',
    follow         int unsigned                               null comment '追番',
    series_follow  int unsigned                               null comment '系列追番',
    views          int unsigned                               null comment '播放',
    danmakus       int unsigned                               null comment '弹幕',
    s_index        varchar(10)                                null comment '集数',
    index_show     text                                       null comment '页面更新状态展示',
    is_started     tinyint unsigned                           null comment '开播状态',
    is_finish      tinyint unsigned                           null comment '完结状态',
    timestamp_view datetime         default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp      int unsigned                               null comment '更新时间戳',
    watch          tinyint unsigned default 1                 not null comment '系统监视标志'
)
    comment '番剧信息表';

create table if not exists status_bangumi_rank
(
    `rank`         tinyint(1) unsigned                not null comment '排名'
        primary key,
    pts            int unsigned                       not null comment '综合分数',
    sid            int unsigned                       not null comment '番剧season id',
    title          varchar(128)                       not null comment '番剧标题',
    danmakus       int unsigned                       not null comment '弹幕',
    follow         int unsigned                       not null comment '追番',
    series_follow  int unsigned                       not null comment '系列追番',
    views          int unsigned                       not null comment '播放',
    timestamp_view datetime default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间戳(观察用)',
    timestamp      int unsigned                       not null comment '更新时间戳'
)
    comment '番剧排行榜信息表';

create table if not exists zones
(
    tid        smallint unsigned not null comment '分区ID'
        primary key,
    parent_tid smallint          not null comment '父分区ID',
    tname      varchar(16)       not null comment '代号',
    tname_cn   varchar(16)       not null comment '名称',
    desp       varchar(64)       null comment '简介',
    url        varchar(32)       not null comment 'URL路由'
)
    comment '视频分区元数据';

