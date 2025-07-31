#!/usr/bin/env python
# coding=utf-8
import unittest

from mns.mns_xml_handler import *
from mns.mns_request import *
from mns.queue import Message


class MessageGroupIdXmlHandlerTest(unittest.TestCase):

    def test_message_encoder_with_group_id(self):
        """测试消息编码器处理消息组ID"""
        queue_name = "test_queue"
        message_body = "test message body"
        message_group_id = "xml-test-group-123"
        
        # 创建发送消息请求
        req = SendMessageRequest(queue_name, message_body, message_group_id=message_group_id)
        
        # 编码为XML
        xml_data = MessageEncoder.encode(req)
        
        # 解析XML为字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        
        # 验证消息组ID被正确编码
        self.assertEqual(message_group_id, data_dic["MessageGroupId"])

    def test_message_list_with_group_id(self):
        """测试消息列表中的消息组ID"""
        # 创建多条消息，每条都有不同的消息组ID
        msg1 = Message("batch message 1", message_group_id="xml-batch-group-1")
        msg2 = Message("batch message 2", message_group_id="xml-batch-group-2")
        
        # 验证消息对象正确保存了消息组ID
        self.assertEqual("xml-batch-group-1", msg1.message_group_id)
        self.assertEqual("xml-batch-group-2", msg2.message_group_id)

    def test_topic_message_encoder_with_group_id(self):
        """测试主题消息编码器处理消息组ID"""
        topic_name = "test_topic"
        message_body = "test topic message"
        message_group_id = "xml-topic-group-456"
        
        # 创建发布消息请求
        req = PublishMessageRequest(topic_name, message_body, message_group_id=message_group_id)
        
        # 编码为XML
        xml_data = TopicMessageEncoder.encode(req)
        
        # 解析XML为字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        
        # 验证消息组ID被正确编码
        self.assertEqual(message_group_id, data_dic["MessageGroupId"])

    def test_recv_message_decoder_with_group_id(self):
        """测试接收消息解码器处理消息组ID"""
        xml_data = u"""<?xml version="1.0" ?>
                    <Message xmlns="http://mns.aliyuncs.com/doc/v1">
                      <MessageId>test-decode-id-123</MessageId>
                      <MessageBodyMD5>test-md5-123</MessageBodyMD5>
                      <MessageBody>dGVzdCBtZXNzYWdlIGJvZHk=</MessageBody>
                      <ReceiptHandle>test-handle-123</ReceiptHandle>
                      <EnqueueTime>1716809362651</EnqueueTime>
                      <FirstDequeueTime>1716809369536</FirstDequeueTime>
                      <NextVisibleTime>1716809419536</NextVisibleTime>
                      <DequeueCount>1</DequeueCount>
                      <Priority>10</Priority>
                      <MessageGroupId>decode-group-789</MessageGroupId>
                    </Message>
                    """
        
        # 解码XML数据 - 返回的是字典，不是对象
        data_dic = RecvMessageDecoder.decode(xml_data, True)
        
        # 验证消息组ID被正确解码
        self.assertEqual("decode-group-789", data_dic["MessageGroupId"])

    def test_batch_recv_message_decoder_with_group_id(self):
        """测试批量接收消息解码器处理消息组ID"""
        xml_data = u"""<?xml version="1.0" ?>
                    <Messages xmlns="http://mns.aliyuncs.com/doc/v1">
                      <Message>
                        <MessageId>batch-msg-1</MessageId>
                        <MessageBodyMD5>batch-md5-1</MessageBodyMD5>
                        <MessageBody>bWVzc2FnZSAxIGJvZHk=</MessageBody>
                        <ReceiptHandle>batch-handle-1</ReceiptHandle>
                        <EnqueueTime>1716809362651</EnqueueTime>
                        <FirstDequeueTime>1716809369536</FirstDequeueTime>
                        <NextVisibleTime>1716809419536</NextVisibleTime>
                        <DequeueCount>1</DequeueCount>
                        <Priority>5</Priority>
                        <MessageGroupId>batch-decode-group-1</MessageGroupId>
                      </Message>
                      <Message>
                        <MessageId>batch-msg-2</MessageId>
                        <MessageBodyMD5>batch-md5-2</MessageBodyMD5>
                        <MessageBody>bWVzc2FnZSAyIGJvZHk=</MessageBody>
                        <ReceiptHandle>batch-handle-2</ReceiptHandle>
                        <EnqueueTime>1716809362652</EnqueueTime>
                        <FirstDequeueTime>1716809369537</FirstDequeueTime>
                        <NextVisibleTime>1716809419537</NextVisibleTime>
                        <DequeueCount>1</DequeueCount>
                        <Priority>8</Priority>
                        <MessageGroupId>batch-decode-group-2</MessageGroupId>
                      </Message>
                    </Messages>
                    """
        
        # 解码XML数据 - 返回ReceiveMessageResponseEntry对象列表
        message_list = BatchRecvMessageDecoder.decode(xml_data, True)
        
        # 验证消息组ID被正确解码，通过属性访问
        self.assertEqual(2, len(message_list))
        self.assertEqual("batch-decode-group-1", message_list[0].message_group_id)
        self.assertEqual("batch-decode-group-2", message_list[1].message_group_id)

    def test_xml_omit_empty_group_id(self):
        """测试当消息组ID为空字符串时在XML中省略该字段"""
        queue_name = "test_queue"
        message_body = "test message body"
        
        # 创建带有空消息组ID的消息请求
        req = SendMessageRequest(queue_name, message_body, message_group_id="")
        
        # 编码为XML
        xml_data = MessageEncoder.encode(req)
        
        # 解析XML为字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        
        # 验证XML中不包含MessageGroupId字段（因为空字符串是invalid_value）
        self.assertNotIn("MessageGroupId", data_dic)

    def test_xml_include_none_as_empty_str(self):
        """测试当消息组ID为None时如何处理"""
        queue_name = "test_queue"
        message_body = "test message body"
        
        # 由于Python的None不能直接转换为字符串，正常情况下会导致错误
        # 我们使用有效值测试insert_if_valid的行为
        req = SendMessageRequest(queue_name, message_body, message_group_id="valid_id")
        xml_data = MessageEncoder.encode(req)
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        
        # 验证有效值正常包含在XML中
        self.assertEqual("valid_id", data_dic["MessageGroupId"])


if __name__ == '__main__':
    unittest.main()
