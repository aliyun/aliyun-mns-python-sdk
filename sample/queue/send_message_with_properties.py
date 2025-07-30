#!/usr/bin/env python
# coding=utf8

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from sample_config import MNSSampleConfig
from mns.account import Account
from mns.queue import *
from mns.message_property import (MessagePropertyValue, PropertyType, 
                                MessageSystemPropertyValue, SystemPropertyName)

# 从sample.cfg中读取基本配置信息
# WARNING： Please do not hard code your accessId and accesskey in next line.(more information: https://yq.aliyun.com/articles/55947)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

# 初始化 my_account, my_queue
my_account = Account(endpoint, accessKeyId, accessKeySecret, token)
queue_name = sys.argv[1] if len(sys.argv) > 1 else "MySampleQueue"
my_queue = my_account.get_queue(queue_name)

# 循环发送多条带属性的消息
msg_count = 3

print("%sSend Message With Properties To Queue%s\nQueueName: %s\nMessageCount: %s\n" % (10 * "=", 10 * "=", queue_name, msg_count))
for i in range(msg_count):
    try:
        msg_body = u"I am test message %s with properties." % i
        msg = Message(msg_body)
        
        # 添加用户自定义属性
        msg.add_user_property("message_index", MessagePropertyValue.create_number(i))
        msg.add_user_property("sender", MessagePropertyValue.create_string("test_sender"))
        msg.add_user_property("is_test", MessagePropertyValue.create_boolean(True))
        msg.add_user_property("priority_level", MessagePropertyValue.create_string("high"))
        
        # 添加二进制属性示例
        binary_data = ("binary_data_%s" % i).encode('utf-8')
        msg.add_user_property("binary_info", MessagePropertyValue.create_binary(binary_data))
        
        # 添加系统属性
        trace_id = "00-4bf92f3577b34da6a3ce929d0e0e473%s-00f067aa0ba902b7-01" % i
        msg.add_system_property(SystemPropertyName.TRACEPARENT, 
                               MessageSystemPropertyValue.create_string(trace_id))
        msg.add_system_property(SystemPropertyName.TRACESTATE, 
                               MessageSystemPropertyValue.create_string("congo=t61rcWkgMzE"))
        
        # 发送消息
        re_msg = my_queue.send_message(msg)
        
        print("Send Message Succeed!")
        print("  MessageBody: %s" % msg_body)
        print("  MessageID: %s" % re_msg.message_id)
        print("  User Properties Count: %d" % len(msg.get_user_properties()))
        print("  System Properties Count: %d" % len(msg.get_system_properties()))
        
        # 打印用户自定义属性
        for name, prop_value in msg.get_user_properties().items():
            print("    User Property - %s: %s (type: %s)" % (name, prop_value.get_string_value_by_type(), prop_value.get_data_type()))
        
        # 打印系统属性
        for name, prop_value in msg.get_system_properties().items():
            print("    System Property - %s: %s" % (name, prop_value.get_string_value_by_type()))
        
        print("")
        
    except MNSExceptionBase as e:
        if e.type == "QueueNotExist":
            print("Queue not exist, please create queue before send message.")
            sys.exit(0)
        print("Send Message Fail! Exception: %s\n" % e)