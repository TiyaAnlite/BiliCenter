# 环境变量

部署和测试服务时，需要为运行环境配置变量

| 变量名                  | 值                                          |
| ----------------------- | ------------------------------------------- |
| TENCENTCLOUD_REGION     | 腾讯云访问地域                              |
| TENCENTCLOUD_SECRETID   | 腾讯云鉴权SecretId                          |
| TENCENTCLOUD_SECRETKEY  | 腾讯云鉴权SecretKey                         |
| BILICENTER_SCFNAMESPACE | 数据中心使用SCF的命名空间                   |
| BILICENTER_SCFNAME      | 数据中心并发部署使用的SCF名                 |
| BILICENTER_SCFQUALIFIER | (可选)并发中心部署SCF使用的目标版本         |
| BILICENTER_REDIS_KWARGS | 用于连接Redis消息与配置中心的JSON参数字符串 |
| BILICENTER_MYSQL_KWARGS | 用于连接MySQL核心数据库的JSON参数字符串     |

JSON参数字符串举例

*BILICENTER_REDIS_KWARGS:*

```json
{"host": "127.0.0.1", "port": 6379, "db": 0, "password": null}
```

***如果在腾讯云内网服务器进行部署，可以添加以下变量内容经由内网SCF提高速度***

**请勿**在外网测试环境使用这些变量，这会导致请求异常

| 变量名              | 值   |
| ------------------- | ---- |
| TENCENTCLOUD_RUNENV | SCF  |

