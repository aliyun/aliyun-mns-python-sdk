#!/usr/bin/env python
# coding=utf8
# Copyright (C) 2015, Alibaba Cloud Computing
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys
import time

from mns.account import Account
from mns.queue import *
from mns.topic import *
from sample_config import MNSSampleConfig

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser as ConfigParser

# 获取配置信息
# AccessKeyId      阿里云官网获取
# AccessKeySecret  阿里云官网获取
# Endpoint         阿里云消息和通知服务官网获取, Example: http://$AccountId.mns.cn-hangzhou.aliyuncs.com
# WARNING： Please do not hard code your accessId and accessKey in next line.(more information see README)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

# 初始化my_account
my_account = Account(endpoint, accessKeyId, accessKeySecret, token)

# FIFO Queue 相关操作
my_queue = my_account.get_queue("MNS-Sample-MyFifoQueue-%s" % time.strftime("%y%m%d-%H%M%S", time.localtime()))

# 创建FIFO队列
# message被receive后，持续不可消费的时间   100秒
# message body的最大长度                   10240Byte
# message最长存活时间                      3600秒
# 新message可消费的默认延迟时间            10秒
# receive message时，长轮询时间            20秒
# messageType设置为1表示FIFO类型
queue_meta = QueueMeta()
queue_meta.set_visibilitytimeout(100)
queue_meta.set_maximum_message_size(10240)
queue_meta.set_message_retention_period(3600)
queue_meta.set_polling_wait_seconds(20)
queue_meta.set_logging_enabled(True)
queue_meta.set_message_type(1)  # 设置为FIFO类型
try:
    queue_url = my_queue.create(queue_meta)
    sys.stdout.write("Create FIFO Queue Succeed!\nQueueURL:%s\n\n" % queue_url)
except MNSExceptionBase as e:
    sys.stderr.write("Create FIFO Queue Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 发送FIFO消息，包含messageGroupId
# set_delayseconds     设置消息的延迟时间，单位：秒
# set_priority         设置消息的优先级
# set_message_group_id 设置消息组ID（FIFO队列特有）
# 返回如下属性：
# MessageId            消息编号
# MessageBodyMd5       消息正文的MD5值
msg_body = "I am test FIFO Message."
message = Message(msg_body)
message.set_delayseconds(0)
message.set_message_group_id("test-group-id")  # 设置消息组ID
try:
    send_msg = my_queue.send_message(message)
    sys.stdout.write("Send FIFO Message Succeed.\nMessageBody:%s\nMessageId:%s\nMessageBodyMd5:%s\nMessageGroupId:%s\n\n" % (
        msg_body, send_msg.message_id, send_msg.message_body_md5, "test-group-id"))
except MNSExceptionBase as e:
    sys.stderr.write("Send FIFO Message Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 消费FIFO消息
# wait_seconds 指定长轮询时间，单位：秒
# 返回属性和查看消息基本相同，增加NextVisibleTime和ReceiptHandle
# NextVisibleTime      消息下次可被消费的时间，单位：毫秒
# ReceiptHandle        本次消费消息产生的临时句柄，用于删除或修改处于Inactive的消息，NextVisibleTime之前有效
recv_msg = None
try:
    wait_seconds = 10
    recv_msg = my_queue.receive_message_with_str_body(wait_seconds)
    sys.stdout.write("Receive FIFO Message Succeed! \
                      \nMessageId: %s\nMessageBodyMD5: %s \
                      \nMessageBody: %s\nDequeueCount: %s \
                      \nEnqueueTime: %s\nFirstDequeueTime: %s \
                      \nPriority: %s\nNextVisibleTime: %s \
                      \nReceiptHandle: %s\nMessageGroupId: %s\n\n" %
                     (recv_msg.message_id, recv_msg.message_body_md5,
                      recv_msg.message_body, recv_msg.dequeue_count,
                      recv_msg.enqueue_time, recv_msg.first_dequeue_time,
                      recv_msg.priority, recv_msg.next_visible_time,
                      recv_msg.receipt_handle, getattr(recv_msg, 'message_group_id', 'N/A')))
except MNSExceptionBase as e:
    sys.stderr.write("Receive FIFO Message Fail!\nException:%s\n\n" % e)

# 删除FIFO消息
if recv_msg is not None:
    try:
        my_queue.delete_message(recv_msg.receipt_handle)
        sys.stdout.write("Delete FIFO Message Succeed.\n\n")
    except MNSExceptionBase as e:
        sys.stderr.write("Delete FIFO Message Fail!\nException:%s\n\n" % e)
        sys.exit(1)

# 批量发送FIFO消息
messages = []
msg_cnt = 5
for i in range(msg_cnt):
    msg = Message("I am test FIFO Message %s." % i)
    msg.set_message_group_id("test-group-id-batch")  # 设置消息组ID
    messages.append(msg)

try:
    send_msgs = my_queue.batch_send_message(messages)
    sys.stdout.write("Batch Send FIFO Message Succeed.\n")
    for msg in send_msgs:
        sys.stdout.write("MessageId:%s\nMessageBodyMd5:%s\nMessageGroupId:%s\n\n" % (msg.message_id, msg.message_body_md5, msg.message_group_id))
except MNSExceptionBase as e:
    sys.stderr.write("Batch Send FIFO Message Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 批量消费FIFO消息
recv_msgs = []
try:
    batch_size = 10
    wait_seconds = 10
    recv_msgs = my_queue.batch_receive_message_with_str_body(batch_size, wait_seconds)
    sys.stdout.write("Batch Receive FIFO Message Succeed.\n")
    for msg in recv_msgs:
        sys.stdout.write("MessageId: %s\nMessageBodyMD5: %s \
                          \nMessageBody: %s\nDequeueCount: %s \
                          \nEnqueueTime: %s\nFirstDequeueTime: %s \
                          \nPriority: %s\nNextVisibleTime: %s \
                          \nReceiptHandle: %s\nMessageGroupId: %s\n\n" %
                         (msg.message_id, msg.message_body_md5,
                          msg.message_body, msg.dequeue_count,
                          msg.enqueue_time, msg.first_dequeue_time,
                          msg.priority, msg.next_visible_time,
                          msg.receipt_handle, getattr(msg, 'message_group_id', 'N/A')))
except MNSExceptionBase as e:
    sys.stderr.write("Batch Receive FIFO Message Fail!\nException:%s\n\n" % e)

# 批量删除FIFO消息
try:
    receipt_handle_list = [msg.receipt_handle for msg in recv_msgs]
    my_queue.batch_delete_message(receipt_handle_list)
    sys.stdout.write("Batch Delete FIFO Message Succeed.\n")
except MNSExceptionBase as e:
    sys.stderr.write("Batch Delete FIFO Message Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# FIFO Topic 相关操作
my_fifo_topic = my_account.get_topic("MyFifoTopic-%s" % time.strftime("%y%m%d-%H%M%S", time.localtime()))

# 创建FIFO主题
# maximum_message_size 消息的最大长度      10240Byte
# messageType设置为1表示FIFO类型
topic_meta = TopicMeta()
topic_meta.set_maximum_message_size(10240)
topic_meta.set_message_type(1)
try:
    topic_url = my_fifo_topic.create(topic_meta)
    sys.stdout.write("Create FIFO Topic Succeed!\nTopicURL:%s\n\n" % topic_url)
except MNSExceptionBase as e:
    sys.stderr.write("Create FIFO Topic Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 创建订阅，订阅到FIFO队列
# endpoint                 接收端地址（FIFO队列的endpoint）
# filter_tag               消息过滤的标签，不能超过16个字符
# notify_strategy          向Endpoint推送消息错误时的重试策略
# notify_content_format    向Endpoint推送的消息内容格式
account_id = endpoint.split("/")[2].split(".")[0]
region = endpoint.split(".")[2]
fifo_queue_endpoint = "acs:mns:%s:%s:queues/%s" % (region, account_id, my_queue.queue_name)
filter_tag = "important"
sub_meta = SubscriptionMeta(fifo_queue_endpoint, SubscriptionNotifyStrategy.BACKOFF, SubscriptionNotifyContentFormat.SIMPLIFIED,
                            filter_tag)
my_fifo_sub = my_fifo_topic.get_subscription("MyFifoSubscription-%s" % time.strftime("%y%m%d-%H%M%S", time.localtime()))
try:
    sub_url = my_fifo_sub.subscribe(sub_meta)
    sys.stdout.write("Subscribe FIFO Topic to FIFO Queue Succeed!\nSubscriptionURL:%s\n\n" % sub_url)
except MNSExceptionBase as e:
    sys.stderr.write("Subscribe FIFO Topic to FIFO Queue Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 发送FIFO Topic消息，包含messageGroupId
# msg_body                 发布消息的正文
# msg_tag                  消息标签（用户消息过滤），不能超过16个字符
# message_group_id         消息组ID（FIFO主题特有）
# 返回如下属性：
# MessageId                消息编号
# MessageBodyMd5           消息正文的MD5值
msg_body = u"I am test FIFO topic message."
msg_tag = "important"
message = Base64TopicMessage(msg_body, msg_tag)
message.set_message_group_id("fifo-topic-group-id")  # 设置消息组ID
try:
    re_msg = my_fifo_topic.publish_message(message)
    sys.stdout.write(
        "Publish FIFO Topic Message Succeed.\nMessageBody:%s\nMessageTag:%s\nMessageId:%s\nMessageBodyMd5:%s\nMessageGroupId:%s\n\n"
        % (msg_body, msg_tag, re_msg.message_id, re_msg.message_body_md5, "fifo-topic-group-id"))
except MNSExceptionBase as e:
    sys.stderr.write("Publish FIFO Topic Message Fail!\nException:%s\n\n" % e)
    sys.exit(1)

# 从FIFO队列接收Topic推送的消息
try:
    wait_seconds = 10
    topic_recv_msg = my_queue.receive_message_with_str_body(wait_seconds)
    sys.stdout.write("Receive FIFO Topic Message from Queue Succeed! \
                      \nMessageId: %s\nMessageBodyMD5: %s \
                      \nMessageBody: %s\nDequeueCount: %s \
                      \nEnqueueTime: %s\nFirstDequeueTime: %s \
                      \nPriority: %s\nNextVisibleTime: %s \
                      \nReceiptHandle: %s\nMessageGroupId: %s\n\n" %
                     (topic_recv_msg.message_id, topic_recv_msg.message_body_md5,
                      topic_recv_msg.message_body, topic_recv_msg.dequeue_count,
                      topic_recv_msg.enqueue_time, topic_recv_msg.first_dequeue_time,
                      topic_recv_msg.priority, topic_recv_msg.next_visible_time,
                      topic_recv_msg.receipt_handle, getattr(topic_recv_msg, 'message_group_id', 'N/A')))
except MNSExceptionBase as e:
    sys.stderr.write("Receive FIFO Topic Message from Queue Fail!\nException:%s\n\n" % e)

# 删除从Topic推送的消息
if 'topic_recv_msg' in locals() and topic_recv_msg is not None:
    try:
        my_queue.delete_message(topic_recv_msg.receipt_handle)
        sys.stdout.write("Delete FIFO Topic Message from Queue Succeed.\n\n")
    except MNSExceptionBase as e:
        sys.stderr.write("Delete FIFO Topic Message from Queue Fail!\nException:%s\n\n" % e)

# 删除FIFO订阅
try:
    my_fifo_sub.unsubscribe()
    sys.stdout.write("Delete FIFO Subscription Succeed!\n\n")
except MNSExceptionBase as e:
    sys.stderr.write("Delete FIFO Subscription Fail!\nException:%s\n\n" % e)

# 删除FIFO主题
try:
    my_fifo_topic.delete()
    sys.stdout.write("Delete FIFO Topic Succeed!\n\n")
except MNSExceptionBase as e:
    sys.stderr.write("Delete FIFO Topic Fail!\nException:%s\n\n" % e)

# 删除FIFO队列
try:
    my_queue.delete()
    sys.stdout.write("Delete FIFO Queue Succeed!\n\n")
except MNSExceptionBase as e:
    sys.stderr.write("Delete FIFO Queue Fail!\nException:%s\n\n" % e)
    sys.exit(1)

sys.stdout.write("FIFO PASS ALL!!\n\n")