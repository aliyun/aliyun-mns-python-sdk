# MNSCMD
mns cmd 基础使用方法介绍

# 配置

配置访问 MNS 所需要的认证信息
命令：```mnscmd config --mnsendpoint=YOUR_ENDPOINT --accesskeyid=YOUR_ACCESSKEYID --accesskeysecret=YOUR_ACCESSKEYSECRET```

# Account 相关命令

1. 获取 Account 的属性
   命令：`mnscmd getaccountattr`

# Queue 相关命令

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

# Topic 相关命令

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