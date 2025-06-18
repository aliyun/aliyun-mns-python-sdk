#!/usr/bin/env python
# coding=utf-8
import unittest
import os
import sys
import time
from unittest import mock

from mns.mns_client import MNSClient
from mns.queue import Queue, Message
from mns.topic import Topic, TopicMessage
from mns.mns_exception import MNSClientParameterException


class ClientMessageGroupIdTest(unittest.TestCase):
    
    def setUp(self):
        """设置测试环境"""
        # 创建模拟的MNSClient
        self.mns_client = mock.MagicMock(spec=MNSClient)
        
        # 设置模拟响应
        self.mns_client.send_message.return_value = None
        self.mns_client.publish_message.return_value = None
        
        # 创建队列和主题
        self.queue = Queue("test_queue", self.mns_client)
        self.topic = Topic("test_topic", self.mns_client)
    
    def test_queue_client_send_message_with_group_id(self):
        """测试客户端发送带有消息组ID的队列消息"""
        message_body = "test message body"
        group_id = "client-test-group-123"
        
        # 创建消息并设置消息组ID
        message = Message(message_body, message_group_id=group_id)
        
        # 发送消息
        self.queue.send_message(message)
        
        # 验证客户端调用方法时传递了正确的消息组ID
        # 检查send_message被调用，且第一个参数中包含正确的message_group_id
        args, _ = self.mns_client.send_message.call_args
        req = args[0]
        self.assertEqual(group_id, req.message_group_id)
    
    def test_queue_client_receive_message_with_group_id(self):
        """测试客户端接收带有消息组ID的队列消息"""
        # 创建模拟的接收消息响应
        from mns.mns_request import ReceiveMessageResponse
        resp = ReceiveMessageResponse()
        resp.message_id = "test-msg-id"
        resp.message_body_md5 = "test-md5"
        resp.message_body = "test body"
        resp.receipt_handle = "test-handle"
        resp.enqueue_time = int(time.time() * 1000)
        resp.next_visible_time = int(time.time() * 1000) + 30000
        resp.first_dequeue_time = int(time.time() * 1000)
        resp.dequeue_count = 1
        resp.priority = 8
        resp.message_group_id = "received-group-456"
        
        # 模拟客户端接收消息的行为
        self.mns_client.receive_message.return_value = None
        self.mns_client.receive_message.side_effect = lambda req, resp_obj: self._copy_response_attrs(resp, resp_obj)
        
        # 接收消息
        received_msg = self.queue.receive_message()
        
        # 验证接收到的消息包含正确的消息组ID
        self.assertEqual("received-group-456", received_msg.message_group_id)
    
    def test_topic_client_publish_message_with_group_id(self):
        """测试客户端发布带有消息组ID的主题消息"""
        message_body = "test topic message body"
        group_id = "topic-test-group-789"
        
        # 创建主题消息并设置消息组ID
        topic_message = TopicMessage(message_body, message_group_id=group_id)
        
        # 发布消息
        self.topic.publish_message(topic_message)
        
        # 验证客户端调用方法时传递了正确的消息组ID
        args, _ = self.mns_client.publish_message.call_args
        req = args[0]
        self.assertEqual(group_id, req.message_group_id)
    
    def test_queue_client_batch_send_with_group_id(self):
        """测试客户端批量发送带有消息组ID的队列消息"""
        # 创建多条消息，每条都有不同的消息组ID
        messages = [
            Message("batch message 1", message_group_id="batch-group-1"), 
            Message("batch message 2", message_group_id="batch-group-2"),
            Message("batch message 3", message_group_id="batch-group-3")
        ]
        
        # 批量发送消息
        self.queue.batch_send_message(messages)
        
        # 验证客户端调用方法时传递了正确的消息组ID列表
        args, _ = self.mns_client.batch_send_message.call_args
        req = args[0]
        self.assertEqual(3, len(req.message_list))
        self.assertEqual("batch-group-1", req.message_list[0].message_group_id)
        self.assertEqual("batch-group-2", req.message_list[1].message_group_id)
        self.assertEqual("batch-group-3", req.message_list[2].message_group_id)
    
    def test_queue_client_send_message_without_group_id(self):
        """测试客户端发送不带消息组ID的队列消息（兼容性测试）"""
        message_body = "test message without group id"
        
        # 创建不带消息组ID的消息（默认为空字符串）
        message = Message(message_body)
        
        # 发送消息
        self.queue.send_message(message)
        
        # 验证客户端调用方法时消息组ID为默认值
        args, _ = self.mns_client.send_message.call_args
        req = args[0]
        # 根据实际行为，默认值可能是""或None
        self.assertTrue(req.message_group_id == "" or req.message_group_id is None)
    
    def _copy_response_attrs(self, src, dest):
        """复制响应对象的属性"""
        for attr in dir(src):
            if not attr.startswith('_') and not callable(getattr(src, attr)):
                setattr(dest, attr, getattr(src, attr))


if __name__ == '__main__':
    unittest.main()
