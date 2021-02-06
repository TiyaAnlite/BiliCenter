# 环境变量

部署和测试服务时，需要为运行环境配置变量

| 变量名                  | 值                          |
| ----------------------- | --------------------------- |
| TENCENTCLOUD_REGION     | 腾讯云访问地域              |
| TENCENTCLOUD_SECRETID   | 腾讯云鉴权SecretId          |
| TENCENTCLOUD_SECRETKEY  | 腾讯云鉴权SecretKey         |
| BILICENTER_SCFNAMESPACE | 数据中心使用SCF的命名空间   |
| BILICENTER_SCFNAME      | 数据中心并发部署使用的SCF名 |

***如果在腾讯云内网服务器进行部署，可以添加以下变量内容经由内网SCF提高速度***

**请勿在外网测试环境使用这些变量，这会导致请求异常**

| 变量名              | 值   |
| ------------------- | ---- |
| TENCENTCLOUD_RUNENV | SCF  |

