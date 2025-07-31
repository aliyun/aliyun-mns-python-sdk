#!/usr/bin/env python
# coding=utf-8
import unittest
import base64

from mns.mns_xml_handler import *
from mns.queue import *
from mns.mns_request import *


class MessageGroupIdTest(unittest.TestCase):

    def test_send_message_with_group_id(self):
        """测试发送消息时携带消息组ID"""
        message_body = u"I am test message with group id."
        queue_name = "test_queue"
        message_group_id = "test-group-123"
        
        req = SendMessageRequest(queue_name, message_body, message_group_id=message_group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(message_group_id, req.message_group_id)
        
        # 生成发送请求的请求体
        xml_data = MessageEncoder.encode(req)
        
        # 解析请求体，转换为字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        
        # 验证XML中包含消息组ID
        self.assertEqual(message_group_id, data_dic["MessageGroupId"])

    def test_batch_send_message_with_group_id(self):
        """测试批量发送消息时携带消息组ID"""
        queue_name = "test_queue"
        req = BatchSendMessageRequest(queue_name, True)
        
        # 添加带有消息组ID的消息
        message_body_1 = "Message 1"
        message_group_id_1 = "group-1"
        req.add_message(message_body_1, message_group_id=message_group_id_1)
        
        message_body_2 = "Message 2"
        message_group_id_2 = "group-2"
        req.add_message(message_body_2, message_group_id=message_group_id_2)
        
        # 验证消息组ID被正确设置
        self.assertEqual(2, len(req.message_list))
        self.assertEqual(message_group_id_1, req.message_list[0].message_group_id)
        self.assertEqual(message_group_id_2, req.message_list[1].message_group_id)

    def test_receive_message_with_group_id(self):
        """测试接收消息时解析消息组ID"""
        xml_data = u"""<?xml version="1.0" ?>
                    <Message xmlns="http://mns.aliyuncs.com/doc/v1">
                      <MessageId>test-message-id</MessageId>
                      <MessageBodyMD5>test-md5</MessageBodyMD5>
                      <MessageBody>SSBhbSDmtYvor5XlrZfnrKbkuLIu</MessageBody>
                      <ReceiptHandle>test-receipt-handle</ReceiptHandle>
                      <EnqueueTime>1716809362651</EnqueueTime>
                      <FirstDequeueTime>1716809369536</FirstDequeueTime>
                      <NextVisibleTime>1716809419536</NextVisibleTime>
                      <DequeueCount>1</DequeueCount>
                      <Priority>10</Priority>
                      <MessageGroupId>test-group-456</MessageGroupId>
                    </Message>
                    """
        
        queue_name = "test_queue"
        req = ReceiveMessageRequest(queue_name, True)
        resp = ReceiveMessageResponse()
        
        # 解码响应数据
        data = RecvMessageDecoder.decode(xml_data, req.base64decode)
        MNSClient.make_recvresp(MNSClient("http://test.com", "access_id", "access_key"), data, resp)
        
        # 验证消息组ID被正确解析
        self.assertEqual("test-group-456", resp.message_group_id)

    def test_batch_receive_message_with_group_id(self):
        """测试批量接收消息时解析消息组ID"""
        xml_data = u"""<?xml version="1.0" ?>
                    <Messages xmlns="http://mns.aliyuncs.com/doc/v1">
                      <Message>
                        <MessageId>msg-1</MessageId>
                        <MessageBodyMD5>md5-1</MessageBodyMD5>
                        <MessageBody>body-1</MessageBody>
                        <ReceiptHandle>handle-1</ReceiptHandle>
                        <EnqueueTime>1716809362651</EnqueueTime>
                        <FirstDequeueTime>1716809369536</FirstDequeueTime>
                        <NextVisibleTime>1716809419536</NextVisibleTime>
                        <DequeueCount>1</DequeueCount>
                        <Priority>5</Priority>
                        <MessageGroupId>group-1</MessageGroupId>
                      </Message>
                      <Message>
                        <MessageId>msg-2</MessageId>
                        <MessageBodyMD5>md5-2</MessageBodyMD5>
                        <MessageBody>body-2</MessageBody>
                        <ReceiptHandle>handle-2</ReceiptHandle>
                        <EnqueueTime>1716809362652</EnqueueTime>
                        <FirstDequeueTime>1716809369537</FirstDequeueTime>
                        <NextVisibleTime>1716809419537</NextVisibleTime>
                        <DequeueCount>1</DequeueCount>
                        <Priority>8</Priority>
                        <MessageGroupId>group-2</MessageGroupId>
                      </Message>
                    </Messages>
                    """
        
        # 解码批量接收响应
        message_list = BatchRecvMessageDecoder.decode(xml_data, False)
        
        # 验证消息组ID被正确解析
        self.assertEqual(2, len(message_list))
        self.assertEqual("group-1", message_list[0].message_group_id)
        self.assertEqual("group-2", message_list[1].message_group_id)

    def test_message_set_group_id(self):
        """测试Message对象设置消息组ID"""
        message = Message("test message body")
        group_id = "test-group-789"
        
        # 设置消息组ID
        message.set_message_group_id(group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(group_id, message.message_group_id)

    def test_message_group_id_default_value(self):
        """测试消息组ID的默认值"""
        message = Message("test message body")
        
        # 验证默认消息组ID为空字符串
        self.assertEqual("", message.message_group_id)

    def test_send_message_request_entry_with_group_id(self):
        """测试SendMessageRequestEntry中的消息组ID"""
        message_body = "test message"
        group_id = "entry-group-123"
        
        entry = SendMessageRequestEntry(message_body, message_group_id=group_id)
        
        # 验证消息组ID被正确设置
        self.assertEqual(group_id, entry.message_group_id)

    def test_send_message_response_entry_group_id(self):
        """测试SendMessageResponseEntry中的消息组ID"""
        entry = SendMessageResponseEntry()
        
        # 验证默认消息组ID为空字符串
        self.assertEqual("", entry.message_group_id)

    def test_receive_message_response_entry_group_id(self):
        """测试ReceiveMessageResponseEntry中的消息组ID"""
        entry = ReceiveMessageResponseEntry()
        
        # 验证默认消息组ID为空字符串
        self.assertEqual("", entry.message_group_id)


if __name__ == '__main__':
    unittest.main()