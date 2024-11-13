
# Change log

## 1.2.1 - 2024-10-11
- 修复 Queue 模型 set_attributes 方法错误将 queue 的属性置为默认值的问题
- 新增 send_message_multi_thread 作为多线程下的最佳实践代码
- 优化 sample 目录下示例文件的命名

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
* 队列/主题支持消息包含中文
* mnscmd 支持参数指定 host、accessKey 对
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

* SDK 支持 Queue 的创建、修改、获取、删除，message 的发送、查看、消费、删除和修改下次可消费时间。