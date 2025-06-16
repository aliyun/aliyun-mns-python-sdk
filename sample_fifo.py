#! /usr/bin/env python
# coding=utf8
import sys
import time
from mns.account import Account
from mns.queue import *
from mns.topic import *
from sample_config import MNSSampleConfig

# 获取配置信息
# AccessKeyId      阿里云官网获取
# AccessKeySecret  阿里云官网获取
# Endpoint         阿里云消息和通知服务官网获取, Example: http://$AccountId.mns.cn-hangzhou.aliyuncs.com
# WARNING： Please do not hard code your accessId and accessKey in next line.(more information see README)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

my_account = Account(endpoint, accessKeyId, accessKeySecret, token)

print("\n注意事项:")
print("1. FIFO队列保证同一消息组内的消息按发送顺序被消费")
print("2. 不同消息组之间的消息可以并行处理")
print("3. 消息组ID是必填参数，在FIFO队列/主题场景下使用")
print("4. FIFO队列和主题需要在控制台预先创建")

# 假设已经创建好了一个FIFO队列
queue_name = 'fifo-queue'
my_fifo_queue = my_account.get_queue(queue_name)

# 假设已经创建好了一个FIFO主题
topic_name = 'fifo-topic'
my_fifo_topic = my_account.get_topic(topic_name)

print("=== FIFO 队列消息操作示例 ===\n")

# 1. 发送带有消息组ID的单条消息到FIFO队列
print("1. 发送带有消息组ID的单条消息...")
msg_body = "FIFO消息 - 组1的第一条消息"
message = Message(msg_body)
message.set_message_group_id("group-001")  # 设置消息组ID

try:
    send_msg = my_fifo_queue.send_message(message)
    print(f"发送成功！\n消息内容: {msg_body}\n消息组ID: group-001\n消息ID: {send_msg.message_id}\nMD5: {send_msg.message_body_md5}\n")
except MNSExceptionBase as e:
    print(f"发送失败！异常: {e}\n")

# 2. 发送同一组的多条消息
print("2. 发送同一组的多条消息...")
for i in range(2, 4):
    msg_body = f"FIFO消息 - 组1的第{i}条消息"
    message = Message(msg_body)
    message.set_message_group_id("group-001")  # 同一个消息组ID
    
    try:
        send_msg = my_fifo_queue.send_message(message)
        print(f"发送成功！消息内容: {msg_body}\n消息组ID：{send_msg.message_group_id}\n消息ID: {send_msg.message_id}")
    except MNSExceptionBase as e:
        print(f"发送失败！异常: {e}")

# 3. 发送不同组的消息
print("\n3. 发送不同组的消息...")
groups = ["group-002", "group-003"]
for group_id in groups:
    msg_body = f"FIFO消息 - {group_id}的消息"
    message = Message(msg_body)
    message.set_message_group_id(group_id)
    
    try:
        send_msg = my_fifo_queue.send_message(message)
        print(f"发送成功！消息内容: {msg_body}\n消息组ID: {group_id}\n消息ID: {send_msg.message_id}")
    except MNSExceptionBase as e:
        print(f"发送失败！异常: {e}")

# 4. 批量发送带有消息组ID的消息
print("\n4. 批量发送带有消息组ID的消息...")
messages = []
for i in range(5):
    msg_body = f"批量FIFO消息 {i+1}"
    message = Message(msg_body)
    # 交替使用两个不同的消息组ID
    group_id = f"batch-group-{i % 2 + 1}"
    message.set_message_group_id(group_id)
    messages.append(message)

try:
    send_msgs = my_fifo_queue.batch_send_message(messages)
    print("批量发送成功！")
    for i, msg in enumerate(send_msgs):
        group_id = f"batch-group-{i % 2 + 1}"
        print(f"消息 {i+1}: 消息组ID: {group_id}, 消息ID: {msg.message_id}")
except MNSExceptionBase as e:
    print(f"批量发送失败！异常: {e}")

# 5. 接收消息（包含消息组ID信息）
print("\n5. 接收消息...")
try:
    recv_msg = my_fifo_queue.receive_message_with_str_body(10)
    print(f"接收成功！\n消息ID: {recv_msg.message_id}")
    print(f"消息内容: {recv_msg.message_body}")
    print(f"消息组ID: {getattr(recv_msg, 'message_group_id', '未设置')}")
    print(f"接收句柄: {recv_msg.receipt_handle}")
    
    # 删除消息
    my_fifo_queue.delete_message(recv_msg.receipt_handle)
    print("消息删除成功！\n")
except MNSExceptionBase as e:
    print(f"接收消息失败！异常: {e}\n")

# 6. 批量接收消息
print("6. 批量接收消息...")
try:
    recv_msgs = my_fifo_queue.batch_receive_message_with_str_body(3, 10)
    print(f"批量接收成功！共接收到 {len(recv_msgs)} 条消息")
    
    receipt_handles = []
    for i, msg in enumerate(recv_msgs):
        print(f"消息 {i+1}:")
        print(f"  消息ID: {msg.message_id}")
        print(f"  消息内容: {msg.message_body}")
        print(f"  消息组ID: {getattr(msg, 'message_group_id', '未设置')}")
        receipt_handles.append(msg.receipt_handle)
    
    # 批量删除消息
    if receipt_handles:
        my_fifo_queue.batch_delete_message(receipt_handles)
        print("批量删除消息成功！\n")
        
except MNSExceptionBase as e:
    print(f"批量接收消息失败！异常: {e}\n")

print("=== FIFO 主题消息操作示例 ===\n")

# 7. 发布带有消息组ID的主题消息
print("7. 发布带有消息组ID的主题消息...")
msg_body = "FIFO主题消息 - 测试消息组功能"
msg_tag = "normal_fifo"
message_group_id = "topic-group-001"

# 使用普通主题消息
topic_message = TopicMessage(msg_body, msg_tag, message_group_id=message_group_id)
try:
    pub_msg = my_fifo_topic.publish_message(topic_message)
    print(f"发布成功！\n消息内容: {msg_body}")
    print(f"消息组ID: {message_group_id}")
    print(f"消息标签: {msg_tag}")
    print(f"消息ID: {pub_msg.message_id}")
    print(f"MD5: {pub_msg.message_body_md5}\n")
except MNSExceptionBase as e:
    print(f"发布失败！异常: {e}\n")

# 9. 发布Base64编码的主题消息
print("9. 发布Base64编码的主题消息...")
msg_body = "Base64编码的FIFO主题消息"
msg_tag = "base64_fifo"
message_group_id = "topic-group-002"

base64_message = Base64TopicMessage(msg_body, msg_tag, message_group_id=message_group_id)
try:
    pub_msg = my_fifo_topic.publish_message(base64_message)
    print(f"发布Base64消息成功！\n消息内容: {msg_body}")
    print(f"消息标签: {msg_tag}")
    print(f"消息组ID: {message_group_id}")
    print(f"消息ID: {pub_msg.message_id}")
    print(f"MD5: {pub_msg.message_body_md5}\n")
except MNSExceptionBase as e:
    print(f"发布Base64消息失败！异常: {e}\n")

# 10. 发布多条不同组的主题消息
print("10. 发布多条不同组的主题消息...")
for i in range(3):
    msg_body = f"多组FIFO主题消息 {i+1}"
    msg_tag = f"multi_group_{i+1}"
    group_id = f"topic-group-{i+1:03d}"
    
    topic_message = TopicMessage(msg_body, msg_tag, message_group_id=group_id)
    try:
        pub_msg = my_fifo_topic.publish_message(topic_message)
        print(f"发布消息 {i+1} 成功！组ID: {group_id}, 消息ID: {pub_msg.message_id}")
    except MNSExceptionBase as e:
        print(f"发布消息 {i+1} 失败！异常: {e}")

print("\n=== FIFO 功能演示完成 ===")