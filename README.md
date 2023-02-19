# BiliCenter
番剧数据中心

一个以事件驱动的数据挖掘框架

## 部署

### 需求

Python 3.6+

参照如下命令安装依赖
```
pip install -r requirements.txt
```

或者

```
python -m pip install -r requirements.txt
```

如果你运行在Linux环境，请视情况将`pip`和`python`替换为`pip3`和`python3`

### 环境与配置

- 请确保拥有腾讯云SCF使用权限，并将`scf/biliHelper`下的SCF函数部署至腾讯云
- 参照[环境变量文档](docs/env.md)进行环境变量的配置，其中包括数据库相关配置
- 根据提供的[SQL](docs/mod_biliCenter.sql)来创建相关的表

### 首次运行

- 定位至`service`下，运行`ConcurrentController.py`，第一次运行会往Redis中写入初始配置并退出

- 可以参照[配置说明](docs/config.md)按需修改运行时配置

### 正式运行

中间件主体在`service`下的三个程序

- `FrontEndTrigger.py`为前端触发器
- `ConcurrentController.py`并发中心
- `CallbackCenter.py`为回调/数据处理中心

启动这三个中间件(无顺序要求)，三个中间件无需在同个节点上，只需向同一个数据库连接即可完成通讯

*执行时的目录为`service/`，不正确的目录会导致错误*

### 任务负载

`service/trigger`和`service/callback`下分别为触发器和回调，可自行新增，中间件启动时会自动进行发现

**本文档还有待进一步完善，关于任务负载的定义、触发规则等细节，移步[协议说明](docs/protocol.md)文档**

## 系统设计

![BiliCenter](docs/BiliCenter.svg)

