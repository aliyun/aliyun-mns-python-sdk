# Aliyun MNS Python SDK

[![Github version](https://badgen.net/badge/color/1.2.0/green?label=version)](https://badgen.net/badge/color/1.2.0/green?label=version)

# 关于

- 此 Python SDK 基于 [阿里云消息服务 MNS](https://www.aliyun.com/product/mns/) 官方 API 构建。
- 阿里云消息服务（Message Service，简称 MNS）是一种高效、可靠、安全、便捷、可弹性扩展的分布式消息服务。
- MNS 能够帮助应用开发者在他们应用的分布式组件上自由的传递数据、通知消息，构建松耦合系统。
- 使用此 SDK，用户可以快速构建高可靠、高并发的一对一消费模型和一对多的发布订阅模型。

# 简介

- 这篇文档主要介绍如何使用 Python 来进行 Message Service API 调用，并且介绍 mnscmd 的简单使用方法。
- 这篇文档假设您已经熟悉 Python，熟悉 Message Service 的相关概念，并且已经注册阿里云账号、开通阿里云的消息服务，且获得了相应的
  AccessKeyId、
  AccessKeySecret 和 AccountId。
- 如果您还没有开通或者还不了解 Message Service，请移步 [阿里云消息服务官方网站](https://www.aliyun.com/product/mns/)。

# 环境要求

Python SDK 需要：安装 Python 2.5 及以上的版本。
可以在 Windows 平台和 Linux 平台使用。

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

### 运行 sample.py

1. 下载最新版 Python SDK，进入 SDK 根目录。
2. 修改 sample.cfg 文件 Endpoint 为您自己的接入点，可登录 [MNS 控制台](https://mns.console.aliyun.com/) 查看，
   具体操作，请参考 [获取接入点](https://help.aliyun.com/zh/mns/user-guide/manage-queues-in-the-console?spm=a2c4g.11186623.0.i25#section-yhc-ix5-300)。
3. 在环境变量中设置您的 `ALIBABA_CLOUD_ACCESS_KEY_ID` 和 `ALIBABA_CLOUD_ACCESS_KEY_SECRET`
   ，阿里云身份验证信息在 [RAM 控制台](https://ram.console.aliyun.com/)
   创建。获取方式请参考 [获取 AccessKey](https://help.aliyun.com/document_detail/53045.html?spm=a2c4g.11186623.0.i29#task-354412)。
4. 根据阿里云规范，您应该将 AK/SK
   信息设置为环境变量使用，请参考 [设置环境变量](https://help.aliyun.com/zh/sdk/developer-reference/configure-the-alibaba-cloud-accesskey-environment-variable-on-linux-macos-and-windows-systems)。
5. linux 平台运行 `python sample.py`，Windows 平台运行 `python.exe sample.py`。

### 运行 simple_notify_endpoint.py

1. 下载最新版 Python SDK，进入 sample 目录。
2. 下载并安装 [pycryptodome](https://pypi.org/project/pycryptodome/)。
3. linux 平台 `python simple_http_notify_endpoint.py 127.0.0.1 [port]`，
   Windows 平台运行 `python.exe simple_http_notify_endpoint.py 127.0.0.1 [port]`,
   端口号默认为 8080。
4. 启动 simple_http_notify_endpoint.py 后会输出监听的地址：`http://127.0.0.1:port`。
5. 接收消息需要 Endpoint 公网可达，将该地址的 127.0.0.1 换为节点的公网 ip 后作为 Subscription 的 Endpoint 属性即可接收推送到该
   Subscription 的消息。

### 单元测试

1. 下载最新版 Python SDK，进入 SDK 根目录。
2. 运行 ```python -m unittest discover -s test``` 即可运行所有测试。

## mnscmd

> 注意：在 Windows 平台 cmd 中 mnscmd 不能直接运行，需要进入 bin 目录，用 `python.exe mnscmd` 替换使用帮助中的 `mnscmd`。  
> 在 SDK 主目录下，修改了 mnscmd 逻辑后，请使用修改后的 mnscmd 路径替换使用帮助中的 `mnscmd`，如 `bin/mnscmd YOUR_COMMAND`。

### 配置

配置访问 MNS 所需要的认证信息
命令：```mnscmd config --mnsendpoint=YOUR_ENDPOINT --accesskeyid=YOUR_ACCESSKEYID --accesskeysecret=YOUR_ACCESSKEYSECRET```

### Account 相关命令

1. 获取 Account 的属性
   命令：`mnscmd getaccountattr`

### Queue 相关命令

1. 列出创建的 queue:
    - 命令：`mnscmd listqueue`
    - 如果是刚刚使用 MNS 的用户因为没有创建 queue，输出是空

2. 创建 queue:
    - 命令：`mnscmd createqueue --queuename=myqueue`
    - 帮助：`mnscmd createqueue --info`
    - "myqueue" 可以根据需求修改为符合规则的 queue name, queue name 的详细规则请移步阿里云消息服务官方网站
    - 更多属性指定，运行帮助命令

3. 获取 queue:
    - 命令：`mnscmd getqueueattr --queuename=myqueue`
    - 命令返回 queue 的各项属性

4. 设置 queue 属性:
    - 命令：`mnscmd setqueueattr --queuename=myqueue --delaysec=5`
    - 帮助：`mnscmd setqueueattr --info`
    - 设置 queue 的 delayseconds 为 5 秒
    - 更多属性设置，运行帮助命令

5. 发送 message:
    - 命令：`mnscmd sendmessage --queuename=myqueue --body="I am a test message."`
    - 帮助：`mnscmd sendmessage --info`
    - 发送一条消息到队列 myqueue 中
    - 更多属性指定，运行帮助命令

6. 查看 message:
    - 命令：`mnscmd peekmessage --queuename=myqueue`
    - 查看 myqueue 中的第一条消息

7. 消费 message:
    - 命令：`mnscmd receivemessage --queuename=myqueue`
    - 消费 myqueue 中的第一条消息
    - 命令返回消息基本信息和临时句柄 (ReceiptHandle)

8. 修改 message 下次可消费时间:
    - 命令：`mnscmd changevisibility --queuename=myqueue --handle=YOUR_RECEIPTHANDLE --vistimeout=10`
    - YOUR_RECEIPTHANDLE 是 receivemessage 返回的 ReceiptHandle
    - 消息 10 秒后可再次被消费，命令返回新的 ReceiptHandle

9. 删除 message:
    - 命令：`mnscmd deletemessage --queuename=myqueue --handle=YOUR_RECEIPTHANDLE`
    - YOUR_RECEIPTHANDLE 是最近一次操作返回的 ReceiptHandle，即第 9 步返回的 ReceiptHandle

10. 删除 queue:
    - 命令：`mnscmd deletequeue --queuename=myqueue`
    - 注意，如果 queue 中有 message，所有 message 都会被删除

### Topic 相关命令

1. 列出创建的 topic:
    - 命令：`mnscmd listtopic`
    - 帮助：`mnscmd listtopic --info`
    - 命令返回 topic 的 URL 列表，--prefix 指定 topic 名称的前缀，--retnum 指定返回的 topic 个数，--marker 指定 topic 的起始位置

2. 创建 topic:
    - 命令：`mnscmd createtopic --topicname=mytopic`
    - 帮助：`mnscmd createtopic --info`
    - 创建名称为 "my topic" 的主题，"my topic" 可以根据需要修改为符合规则的 topic name，topic name 的详细规则请移步阿里云消息服务官方网站

3. 获取 topic 属性:
    - 命令：`mnscmd gettopicattr --topicname=mytopic`
    - 帮助：`mnscmd gettopicattr --info`
    - 命令获取 topic 的各项属性

4. 设置 topic 属性:
    - 命令：`mnscmd settopicattr --topicname=mytopic --maxmsgsize=1024`
    - 帮助：`mnscmd settopicattr --info`
    - 设置 topic 的最大消息长度 1024 Byte

5. 发布消息:
    - 命令：`mnscmd publishmessage --topicname=mytopic --body="I am a test message."`
    - 帮助：`mnscmd publishmessage --info`
    - 发送一条消息到主题 mytopic 中

6. 列出 topic 的 subscription:
    - 命令：`mnscmd listsub --topicname=mytopic`
    - 帮助：`mnscmd listsub --info`
    - 命令返回订阅 mytopic 的 subscription URL 列表，--prefix 指定 subscription 名称的前缀，--retnum 指定返回的
      subscription 个数，--marker 指定起始位置

7. 创建 subscription:
    - 命令：`mnscmd subscribe --topicname=mytopic --subname=mysub --endpoint=http://test-endpoint`
    - 帮助：`mnscmd subscribe --info`
    - 创建一个名叫 mysub 的 subscription，订阅 mytopic，指定 endpoint 为：http://test-endpoint

8. 获取 subscription 属性:
    - 命令：`mnscmd getsubattr --topicname=mytopic --subname=mysub`
    - 帮助：`mnscmd getsubattr --info`
    - 获取 mysub 的各项属性

9. 设置 subscription 属性:
    - 命令：`mnscmd setsubattr --topicname=mytopic --subname=mysub --notifystrategy=BACKOFF_RETRY`
    - 帮助：`mnscmd setsubattr --info`
    - 设置 mysub 的重传策略为 BACKOFF_RETRY

10. 删除 subscription:
    - 命令：`mnscmd unsubscribe --topicname=mytopic --subname=mysub`
    - 帮助：`mnscmd unsubscribe --info`
    - 删除 mysub

11. 删除 topic:
    - 命令：`mnscmd deletetopic --topicname=mytopic`
    - 帮助：`mnscmd deletetopic --info`
    - 删除 mytopic，注意：该操作会删除 mytopic 的所有消息和订阅该 topic 的 subscription
    - 帮助：`mnscmd deletetopic --info`

# ChangeHistory

## 1.2.0 - 2024-07-26

* 支持 Topic/Queue 模型 生产和消费，base 64 编解码可选
* 新增 receive_message_with_str_body 等方法，支持接收消息的消息体是字符串类型。
* 支持 [阿里云规范（AK/SK）](https://help.aliyun.com/zh/sdk/developer-reference/configure-the-alibaba-cloud-accesskey-environment-variable-on-linux-macos-and-windows-systems) 基于 env 获取
* 修复 peek_message 时队列的 base64 编解码设置失效，始终进行 base64 解码的问题
* 修复 python 版本兼容性问题 
* 规范客户端版本上报规范

## 1.1.6 - 2020-11-19

* 增加发送消息返回值的 ReceiptHandle 解析
* 修复 Python 3 兼容性问题

## 1.1.5 - 2019-04-26

* 兼容 Python 3 版本。

## 1.1.4 - 2017-03-14

* 主题模型支持短信推送
* 队列 / 主题支持消息包含中文
* mnscmd 支持参数指定 host、accesskey 对
* mnscmd 支持指定是否对队列消息做 base64 编码和解码

## 1.1.3 - 2016-09-13

* 支持透传 RequestID 到 MNS 端
* Topic 推送支持 QueueEndpoint 和 MailEndpoint
* 主题消息推送支持 json 格式
* mnscmd 支持 --config_file 指定配置文件

## 1.1.2 - 2016-04-25

* Topic 推送支持消息过滤
* 增加 sample 目录，包含更详细的示例代码

## 1.1.1 - 2016-03-25

* 支持 Https 访问
* Queue 和 Topic 支持 LoggingEnabled 属性设置和查询
* 支持设置和获取 Account 的属性

## 1.1.0 - 2016-01-05

* 支持 Topic 相关接口
* 提供 simple_http_notify_endpoint.py 和 simple_https_notify_endpoint.py
* 支持 STS 访问

## 1.0.2 - 2015-06-01

* 支持 SDK 安装
* 提供 mnscmd 命令

## 1.0.1 - 2015-02-03

* 统一队列非字符串属性为 int 类型；
* 修正 SetQueueAttr 的 http 状态码为 204。

## 1.0.0 - 2014-08-01

* SDK 支持 queue 的创建、修改、获取、删除，message 的发送、查看、消费、删除和修改下次可消费时间。