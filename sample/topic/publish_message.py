#!/usr/bin/env python
# coding=utf8

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from sample_config import MNSSampleConfig
from mns.account import Account
from mns.topic import *

# 从sample.cfg中读取基本配置信息
# WARNING： Please do not hard code your accessId and accesskey in next line.(more information: https://yq.aliyun.com/articles/55947)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

# 初始化 my_account, my_topic
my_account = Account(endpoint, accessKeyId, accessKeySecret, token)
topic_name = sys.argv[1] if len(sys.argv) > 1 else "MySampleTopic"
my_topic = my_account.get_topic(topic_name)

# 循环发布多条消息
msg_count = 3
print("%sPublish Message To Topic%s\nTopicName: %s\nMessageCount: %s\n" % (10 * "=", 10 * "=", topic_name, msg_count))

for i in range(msg_count):
    try:
        msg_body = u"I am test message %s." % i
        msg = TopicMessage(msg_body)
        re_msg = my_topic.publish_message(msg)
        print("Publish Raw Message Succeed. MessageBody: %s MessageID: %s" % (msg_body, re_msg.message_id))
    except MNSExceptionBase as e:
        if e.type == "TopicNotExist":
            print("Topic not exist, please create it.")
            sys.exit(1)
        print("Publish Raw Message Fail. Exception: %s" % e)

for i in range(msg_count):
    try:
        msg_body = u"I am test message %s." % i
        msg = Base64TopicMessage(msg_body)
        re_msg = my_topic.publish_message(msg)
        print("Publish Base64 Encoded Message Succeed. MessageBody: %s MessageID: %s" % (msg_body, re_msg.message_id))
    except MNSExceptionBase as e:
        if e.type == "TopicNotExist":
            print("Topic not exist, please create it.")
            sys.exit(1)
        print("Publish Base64 Encoded Message Fail. Exception: %s" % e)
