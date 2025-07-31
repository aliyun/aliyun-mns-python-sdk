#!/usr/bin/env python
# coding=utf-8
import unittest

from mns.topic import TopicMessage, Base64TopicMessage
from mns.mns_request import PublishMessageRequest


class TestTopicMessageGroupId(unittest.TestCase):

    def test_topic_message_with_group_id(self):
        """测试TopicMessage设置消息组ID"""
        message_body = u"test topic message"
        message_tag = u"test_tag"
        message_group_id = u"topic-group-123"
        
        # 创建带有消息组ID的主题消息
        topic_message = TopicMessage(message_body, message_tag, message_group_id=message_group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(message_group_id, topic_message.message_group_id)

    def test_base64_topic_message_with_group_id(self):
        """测试Base64TopicMessage设置消息组ID"""
        message_body = u"test base64 topic message"
        message_tag = u"test_tag"
        message_group_id = u"base64-topic-group-456"
        
        # 创建带有消息组ID的Base64主题消息
        base64_message = Base64TopicMessage(message_body, message_tag, message_group_id=message_group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(message_group_id, base64_message.message_group_id)

    def test_topic_message_set_group_id(self):
        """测试TopicMessage设置消息组ID方法"""
        message_body = u"test topic message"
        topic_message = TopicMessage(message_body)
        group_id = u"set-group-789"
        
        # 设置消息组ID
        topic_message.set_message_group_id(group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(group_id, topic_message.message_group_id)

    def test_topic_message_default_group_id(self):
        """测试TopicMessage默认消息组ID"""
        message_body = u"test topic message"
        topic_message = TopicMessage(message_body)
        
        # 验证默认消息组ID为空字符串
        self.assertEqual(u"", topic_message.message_group_id)

    def test_publish_message_request_with_group_id(self):
        """测试PublishMessageRequest中的消息组ID"""
        topic_name = "test_topic"
        message_body = "test message body"
        message_tag = "test_tag"
        message_group_id = "publish-group-123"
        
        # 创建发布消息请求
        req = PublishMessageRequest(topic_name, message_body, message_tag, message_group_id=message_group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(message_group_id, req.message_group_id)

    def test_publish_message_request_default_group_id(self):
        """测试PublishMessageRequest默认消息组ID"""
        topic_name = "test_topic"
        message_body = "test message body"
        
        # 创建发布消息请求（不指定消息组ID）
        req = PublishMessageRequest(topic_name, message_body)
        
        # 验证默认消息组ID为None
        self.assertIsNone(req.message_group_id)


if __name__ == '__main__':
    unittest.main()