# Aliyun MNS Python SDK

[![Github version](https://badgen.net/badge/color/1.2.1/green?label=version)](https://badgen.net/badge/color/1.2.1/green?label=version)

Aliyun MNS Python SDK 是 MNS 在 Python 编译语言的官方 SDK

## [Change Log](CHANGELOG.md)

# 关于

- 此 Python SDK 基于 [阿里云轻量消息队列（原MNS）](https://www.aliyun.com/product/mns/) 官方 API 构建。
- 阿里云消息服务（Message Service，简称 MNS）是一种高效、可靠、安全、便捷、可弹性扩展的分布式消息服务。
- MNS 能够帮助应用开发者在他们应用的分布式组件上自由的传递数据、通知消息，构建松耦合系统。
- 使用此 SDK，用户可以快速构建高可靠、高并发的一对一消费模型和一对多的发布订阅模型。

# 简介

- 这篇文档主要介绍如何使用 Python 来进行 Message Service API 调用，并且介绍 mnscmd 的简单使用方法。
- 这篇文档假设您已经熟悉 Python，熟悉 Message Service 的相关概念，并且已经注册阿里云账号、开通阿里云的消息服务，且获得了相应的
  AccessKeyId、
  AccessKeySecret 和 AccountId。
- 如果您还没有开通或者还不了解 Simple Message Queue (formerly MNS)，请移步 [阿里云轻量消息队列（原MNS）官方网站](https://www.aliyun.com/product/mns/) 。

# 运行环境

- Python 2.5 及以上

# 安装方法

## pip 安装依赖

```pip install aliyun-mns-sdk```

## 下载 SDK 的方式安装

下载 SDK 并解压，安装 SDK 和 mnscmd

1. linux 平台
   ```sudo python setup.py install```

2. Windows 平台
   ```python.exe setup.py install```

# 快速使用

## SDK

> 注意事项：Account, Queue, Topic, Subscription 均不是线程安全的，多线程场景下请独立构造对象。

## 运行 常规sample

1. 下载最新版 Python SDK，进入 sample 目录。
2. 修改 sample.cfg 文件 Endpoint 为您自己的接入点，可登录 [MNS 控制台](https://mns.console.aliyun.com/) 查看，
   具体操作，请参考 [获取接入点](https://help.aliyun.com/zh/mns/user-guide/manage-queues-in-the-console?spm=a2c4g.11186623.0.i25#section-yhc-ix5-300)。
3. 在环境变量中设置您的 `ALIBABA_CLOUD_ACCESS_KEY_ID` 和 `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
   ，阿里云身份验证信息在 [RAM 控制台](https://ram.console.aliyun.com/)
   创建。获取方式请参考 [获取 AccessKey](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.0.i29#task-354412)。
4. 根据阿里云规范，您应该将 AK/SK
   信息设置为环境变量使用，请参考 [设置环境变量](https://help.aliyun.com/zh/sdk/developer-reference/configure-the-alibaba-cloud-accesskey-environment-variable-on-linux-macos-and-windows-systems)。
5. linux 平台运行 `python sample_all.py`，Windows 平台运行 `python.exe sample_all.py`。

## 运行 topic Http 订阅者 Sample

1. 下载最新版 Python SDK，进入 sample/topic 目录。
2. 下载并安装 [pycryptodome](https://pypi.org/project/pycryptodome/)。
3. linux 平台 `python simple_http_notify_endpoint.py 127.0.0.1 [port]`，
   Windows 平台运行 `python.exe simple_http_notify_endpoint.py 127.0.0.1 [port]`,
   端口号默认为 8080。
4. 启动 simple_http_notify_endpoint.py 后会输出监听的地址：`http://127.0.0.1:port`。
5. 接收消息需要 Endpoint 公网可达，将该地址的 127.0.0.1 换为节点的公网 ip 后作为 Subscription 的 Endpoint 属性即可接收推送到该
   Subscription 的消息。

## 单元测试

1. 下载最新版 Python SDK，进入 SDK 根目录。
2. 运行 ```python -m unittest discover -s test``` 即可运行所有测试。

# mnscmd
有关 `mnscmd` 工具的详细使用信息，请参阅 [mnscmd_usage.md](bin/mnscmd_usage.md)。
> 注意：在 Windows 平台 cmd 中 mnscmd 不能直接运行，需要进入 bin 目录，用 `python.exe mnscmd` 替换使用帮助中的 `mnscmd`。  
> 在 SDK 主目录下，修改了 mnscmd 逻辑后，请使用修改后的 mnscmd 路径替换使用帮助中的 `mnscmd`，如 `bin/mnscmd YOUR_COMMAND`。
