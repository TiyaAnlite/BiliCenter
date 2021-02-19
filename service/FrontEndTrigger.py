import os
import sys
import time
import json
import hashlib
import collections

import redis
import pymysql
from croniter import croniter

if "../" not in sys.path:
    sys.path.append("../")
import logger
from bilicenter_middleware.event import new_event, Channels, Sources
from bilicenter_middleware.discovery import auto_register


class FrontEndTrigger(object):
    """
    **前端触发器**\n
    *根据任务列表中时间和规则引擎相关信息，触发查询动作并将参数送至目标触发函数，并生成事件*
    """

    def __init__(self, log_file="BiliCenter_frontEndTrigger.log", debug=False):
        if debug:
            self.logger = logger.Logger.get_file_debug_logger("CallbackCenter", log_file)
        else:
            self.logger = logger.Logger.get_file_log_logger("CallbackCenter", log_file)

        self.trigger_func = auto_register(collections.defaultdict(lambda: self.__default_trigger_func), "trigger",
                                          self.logger)
        self.trigger = collections.defaultdict(self.__default_trigger)

        redis_config = json.loads(os.getenv("BILICENTER_REDIS_KWARGS"))
        redis_config.update({"decode_responses": True})
        self.redis_pool = redis.ConnectionPool(**redis_config)
        self.logger.info("Connect to redis")
        self.redis = redis.StrictRedis(connection_pool=self.redis_pool)

        sql_config = json.loads(os.getenv("BILICENTER_MYSQL_KWARGS"))
        sql_config.update({"read_timeout": 10, "write_timeout": 10})
        self.logger.info("Connect to MySQL")
        self.sql = pymysql.connect(**sql_config)

    def get_sql_cursor(self) -> pymysql.cursors.Cursor:
        """获得SQL游标对象用于执行语句(带自动重连)"""
        try:
            self.sql.ping()
        except pymysql.err.Error:
            self.logger.info("Reconnect to MySQL")
            self.sql = pymysql.connect(**json.loads(os.getenv("BILICENTER_MYSQL_KWARGS")))
        return self.sql.cursor()

    @staticmethod
    def __default_trigger_func(rules_data: list, r: redis.StrictRedis, log: logger.logging.Logger):
        """
        默认触发函数\n
        :param rules_data: 规则引擎执行数据
        :param r: Redis连接
        :param log: 日志对象
        """

        log.error(f"Unknown trigger, rules data: {rules_data}")

    @staticmethod
    def __default_trigger():
        """生成触发器列表"""
        return {
            "hash": None,
            "cron": None,
            "trigger": None,
            "rules": None
        }

    def read_trigger(self):
        """从Redis中读取一次触发器列表"""
        for n, t in self.redis.hscan_iter("FrontEndTrigger.trigger"):
            md5 = hashlib.md5(t.encode('utf-8')).hexdigest()
            # 验证任务是否新增或被修改
            if self.trigger[n]["hash"] != md5:
                self.logger.info(f"Updating trigger: {n}")
                try:
                    data = json.loads(t)
                    self.trigger[n] = {
                        "hash": md5,
                        "cron": croniter(data["cron"]),
                        "trigger": data["trigger"],
                        "rules": data["rules"]
                    }
                except Exception as err:
                    self.logger.error(f"Error reading trigger: {n}")
                    self.logger.exception(err)
                else:
                    self.trigger[n]["cron"].next()
                    self.logger.info(
                        f"[{n} -> {self.trigger[n]['trigger']}]Next at: {time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(self.trigger[n]['cron'].get_current()))}")

    def prev_rules(self, triggers: list, rules: list):
        """
        前置SQL规则生成器\n
        :param triggers: 触发器列表
        :param rules: SQL语句列表
        :return: (触发器, 触发器单位执行结果)
        """

        if triggers:
            self.logger.info(f"Query sql rules: {sum([len(l) for l in rules])}")
        query_rules = []  # [triggers, rules[]]
        with self.get_sql_cursor() as cursor:
            for r, t in zip(rules, triggers):
                # one trigger
                self.sql.begin()
                try:
                    single_trigger_rules = []
                    for single_rule in r:
                        # one rule
                        cursor.execute(single_rule)
                        single_trigger_rules.append(cursor.fetchall())
                except pymysql.err.DatabaseError as err:
                    self.logger.error(f"Execute error: {single_rule}")
                    self.logger.exception(err)
                    cursor.fetchall()
                    self.sql.rollback()
                else:
                    query_rules.append((t, single_trigger_rules))
                    self.sql.commit()
        for trigger, rule in query_rules:
            yield trigger, rule

    def run_trigger(self):
        """触发已经登记并满足条件的触发器"""
        active_trigger = []
        active_trigger_rules = []
        # Check trigger
        for name, t in self.trigger.items():
            if t["cron"].get_current() <= time.time():
                t["cron"].next()
                self.logger.info(f"Trigger: {name} -> {t['trigger']}")
                active_trigger.append(t["trigger"])
                active_trigger_rules.append(t["rules"])
        # 前置规则SQL触发
        for trigger, rules in self.prev_rules(active_trigger, active_trigger_rules):
            self.logger.info(f"Active trigger: {trigger}")
            with redis.StrictRedis(connection_pool=self.redis_pool) as r:
                # 调用触发器处理函数
                try:
                    self.trigger_func[trigger](rules, r, self.logger)
                except Exception as err:
                    self.logger.error("Trigger func error:")
                    self.logger.error(err)

    def main(self):
        """主循环"""
        self.logger.info("Start to trigger event")
        while True:
            now = int(time.time())
            self.read_trigger()
            while int(time.time()) <= now + 10:  # 10秒检查一次任务信息
                self.run_trigger()
                time.sleep(1)


if __name__ == '__main__':
    trigger = FrontEndTrigger()
    trigger.main()
