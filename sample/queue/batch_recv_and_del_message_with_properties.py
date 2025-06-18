#!/usr/bin/env python
# coding=utf8

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from sample_config import MNSSampleConfig
from mns.account import Account

# 从sample.cfg中读取基本配置信息
# WARNING： Please do not hard code your accessId and accesskey in next line.(more information: https://yq.aliyun.com/articles/55947)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

# 初始化 my_account, my_queue
my_account = Account(endpoint, accessKeyId, accessKeySecret, token)
queue_name = sys.argv[1] if len(sys.argv) > 1 else "MySampleQueue"
base64 = False if len(sys.argv) > 2 and sys.argv[2].lower() == "false" else True
my_queue = my_account.get_queue(queue_name)
my_queue.set_encoding(base64)

# 批量读取删除消息
wait_seconds = 3
batch_size = 16  # 每次最多读取16条消息

print("%sBatch Receive And Delete Messages With Properties From Queue%s\nQueueName: %s\nWaitSeconds: %s\nBatchSize: %s\n"
      % (10 * "=", 10 * "=", queue_name, wait_seconds, batch_size))

while True:
    # 批量读取消息
    try:
        # batch_receive_message 返回字节串列表，batch_receive_message_with_str_body 返回字符串列表
        # recv_msg_list = my_queue.batch_receive_message(batch_size, wait_seconds)
        recv_msg_list = my_queue.batch_receive_message_with_str_body(batch_size, wait_seconds)
        
        if not recv_msg_list:
            print("No messages received.")
            break
            
        print("Batch Receive %d Messages Succeed!" % len(recv_msg_list))
        
        receipt_handles = []
        for i, recv_msg in enumerate(recv_msg_list):
            print("Message %d:" % i)
            print("  ReceiptHandle: %s" % recv_msg.receipt_handle)
            print("  MessageBody: %s" % recv_msg.message_body)
            print("  MessageID: %s" % recv_msg.message_id)
            print("  User Properties Count: %d" % len(recv_msg.get_user_properties()))
            print("  System Properties Count: %d" % len(recv_msg.get_system_properties()))
            
            # 打印用户自定义属性
            if recv_msg.get_user_properties():
                print("  User Properties:")
                for name, prop_value in recv_msg.get_user_properties().items():
                    print("    %s: %s (type: %s)" % (name, prop_value.get_string_value_by_type(), prop_value.get_data_type()))
            
            # 打印系统属性
            if recv_msg.get_system_properties():
                print("  System Properties:")
                for name, prop_value in recv_msg.get_system_properties().items():
                    print("    %s: %s" % (name, prop_value.get_string_value_by_type()))
            
            print("")
            receipt_handles.append(recv_msg.receipt_handle)
        
        # 批量删除消息
        try:
            my_queue.batch_delete_message(receipt_handles)
            print("Batch Delete %d Messages Succeed!" % len(receipt_handles))
            print("")
        except Exception as e:
            print("Batch Delete Messages Fail! Exception: %s\n" % e)
            
    except Exception as e:
        if hasattr(e, 'type'):
            if e.type == u"QueueNotExist":
                print("Queue not exist, please create queue before receive message.")
                sys.exit(0)
            elif e.type == u"MessageNotExist":
                print("Queue is empty!")
                sys.exit(0)
        print("Batch Receive Messages Fail! Exception: %s\n" % e)
        break