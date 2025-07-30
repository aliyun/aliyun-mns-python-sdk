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

# 准备批量发送的消息
messages = []
msg_count = 5

print("%sBatch Send Messages With Properties To Queue%s\nQueueName: %s\nMessageCount: %s\n" % (10 * "=", 10 * "=", queue_name, msg_count))

for i in range(msg_count):
    msg_body = u"I am batch test message %s with properties." % i
    msg = Message(msg_body)
    
    # 添加用户自定义属性
    msg.add_user_property("batch_index", MessagePropertyValue.create_number(i))
    msg.add_user_property("sender", MessagePropertyValue.create_string("batch_sender"))
    msg.add_user_property("is_batch", MessagePropertyValue.create_boolean(True))
    msg.add_user_property("category", MessagePropertyValue.create_string("batch_test"))
    msg.add_user_property("priority_level", MessagePropertyValue.create_string("normal"))
    
    # 添加不同的二进制属性
    binary_data = ("batch_binary_data_%s" % i).encode('utf-8')
    msg.add_user_property("binary_info", MessagePropertyValue.create_binary(binary_data))
    
    # 添加系统属性
    trace_id = "00-4bf92f3577b34da6a3ce929d0e0e475%s-00f067aa0ba902b7-01" % i
    msg.add_system_property(SystemPropertyName.TRACEPARENT, 
                           MessageSystemPropertyValue.create_string(trace_id))
    
    # 为不同的消息添加不同的系统属性
    if i % 2 == 0:
        msg.add_system_property(SystemPropertyName.TRACESTATE, 
                               MessageSystemPropertyValue.create_string("congo=t61rcWkgMzE"))
    else:
        msg.add_system_property(SystemPropertyName.BAGGAGE, 
                               MessageSystemPropertyValue.create_string("userId=12345,sessionId=abcdef"))
    
    messages.append(msg)
    
    print("Prepared Message %d:" % i)
    print("  MessageBody: %s" % msg_body)
    print("  User Properties Count: %d" % len(msg.get_user_properties()))
    print("  System Properties Count: %d" % len(msg.get_system_properties()))

try:
    # 批量发送消息
    re_msg_list = my_queue.batch_send_message(messages)
    
    print("\nBatch Send Messages Succeed!")
    for i, re_msg in enumerate(re_msg_list):
        print("Message %d - MessageID: %s" % (i, re_msg.message_id))
        
        # 打印原始消息的属性信息
        original_msg = messages[i]
        print("  User Properties:")
        for name, prop_value in original_msg.get_user_properties().items():
            print("    %s: %s (type: %s)" % (name, prop_value.get_string_value_by_type(), prop_value.get_data_type()))
        
        print("  System Properties:")
        for name, prop_value in original_msg.get_system_properties().items():
            print("    %s: %s" % (name, prop_value.get_string_value_by_type()))
        print("")
        
except MNSExceptionBase as e:
    if e.type == "QueueNotExist":
        print("Queue not exist, please create queue before send message.")
        sys.exit(0)
    print("Batch Send Messages Fail! Exception: %s\n" % e)