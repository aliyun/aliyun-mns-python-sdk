#!/usr/bin/env python
# coding=utf8

import unittest
import sys
import os
import base64
import xml.dom.minidom

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from mns.mns_xml_handler import MessageEncoder, MessagesEncoder, EncoderBase
from mns.queue import Message
from mns.message_property import (
    MessagePropertyValue, MessageSystemPropertyValue,
    PropertyType, SystemPropertyName
)


class MockSendRequest:
    """模拟发送请求对象"""
    def __init__(self, message_body, base64encode=False):
        self.message_body = message_body
        self.delay_seconds = 0
        self.priority = 8
        self.base64encode = base64encode
        self.user_properties = {}
        self.system_properties = {}
        self.message_group_id = ""


class TestMessageEncoding(unittest.TestCase):
    """测试消息编码功能"""
    
    def test_encode_message_without_properties(self):
        """测试编码不包含属性的消息"""
        req = MockSendRequest("Hello World")
        xml_result = MessageEncoder.encode(req)
        
        # 验证XML结构
        self.assertIn(b"<MessageBody>Hello World</MessageBody>", xml_result)
        self.assertIn(b"<DelaySeconds>0</DelaySeconds>", xml_result)
        self.assertIn(b"<Priority>8</Priority>", xml_result)
        self.assertNotIn(b"<UserProperties>", xml_result)
        self.assertNotIn(b"<SystemProperties>", xml_result)
    
    def test_encode_message_with_user_properties(self):
        """测试编码包含用户属性的消息"""
        req = MockSendRequest("Test message")
        
        # 添加各种类型的用户属性
        req.user_properties["string_prop"] = MessagePropertyValue.create_string("test_value")
        req.user_properties["number_prop"] = MessagePropertyValue.create_number(42)
        req.user_properties["boolean_prop"] = MessagePropertyValue.create_boolean(True)
        req.user_properties["binary_prop"] = MessagePropertyValue.create_binary(b"binary_data")
        
        xml_result = MessageEncoder.encode(req)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证XML包含属性
        self.assertIn("<UserProperties>", xml_str)
        self.assertIn("<PropertyValue>", xml_str)
        self.assertIn("<Name>string_prop</Name>", xml_str)
        self.assertIn("<Value>test_value</Value>", xml_str)
        self.assertIn("<Type>STRING</Type>", xml_str)
        
        # 验证数字属性
        self.assertIn("<Name>number_prop</Name>", xml_str)
        self.assertIn("<Value>42</Value>", xml_str)
        self.assertIn("<Type>NUMBER</Type>", xml_str)
        
        # 验证布尔属性
        self.assertIn("<Name>boolean_prop</Name>", xml_str)
        self.assertIn("<Value>true</Value>", xml_str)
        self.assertIn("<Type>BOOLEAN</Type>", xml_str)
        
        # 验证二进制属性（应该是base64编码）
        self.assertIn("<Name>binary_prop</Name>", xml_str)
        expected_binary = base64.b64encode(b"binary_data").decode('ascii')
        self.assertIn("<Value>%s</Value>" % expected_binary, xml_str)
        self.assertIn("<Type>BINARY</Type>", xml_str)
    
    def test_encode_message_with_system_properties(self):
        """测试编码包含系统属性的消息"""
        req = MockSendRequest("Test message")
        
        # 添加系统属性
        req.system_properties[SystemPropertyName.TRACEPARENT] = MessageSystemPropertyValue.create_string("00-trace-id-01")
        req.system_properties[SystemPropertyName.TRACESTATE] = MessageSystemPropertyValue.create_string("congo=t61rcWkgMzE")
        
        xml_result = MessageEncoder.encode(req)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_str
        
        # 验证XML包含系统属性
        self.assertIn("<SystemProperties>", xml_str)
        self.assertIn("<SystemPropertyValue>", xml_str)
        self.assertIn("<Name>traceparent</Name>", xml_str)
        self.assertIn("<Value>00-trace-id-01</Value>", xml_str)
        self.assertIn("<Name>tracestate</Name>", xml_str)
        self.assertIn("<Value>congo=t61rcWkgMzE</Value>", xml_str)
    
    def test_encode_message_with_base64(self):
        """测试base64编码的消息"""
        req = MockSendRequest("你好世界", base64encode=True)
        req.user_properties["test_prop"] = MessagePropertyValue.create_string("测试属性")
        
        xml_result = MessageEncoder.encode(req)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证消息体被base64编码
        expected_body = base64.b64encode("你好世界".encode('utf-8')).decode('utf-8')
        self.assertIn("<MessageBody>%s</MessageBody>" % expected_body, xml_str)
        
        # 验证属性仍然正常
        self.assertIn("<Value>测试属性</Value>", xml_str)
    
    def test_encode_batch_messages_without_properties(self):
        """测试编码不包含属性的批量消息"""
        messages = []
        for i in range(3):
            msg = MockSendRequest("Message %s" % i)
            messages.append(msg)
        
        xml_result = MessagesEncoder.encode(messages, False)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证批量消息结构
        self.assertIn("<Messages", xml_str)
        self.assertIn("<Message>", xml_str)
        self.assertIn("<MessageBody>Message 0</MessageBody>", xml_str)
        self.assertIn("<MessageBody>Message 1</MessageBody>", xml_str)
        self.assertIn("<MessageBody>Message 2</MessageBody>", xml_str)
    
    def test_encode_batch_messages_with_properties(self):
        """测试编码包含属性的批量消息"""
        messages = []
        
        # 第一条消息 - 包含用户属性
        msg1 = MockSendRequest("Message 1")
        msg1.user_properties["msg_index"] = MessagePropertyValue.create_number(1)
        msg1.user_properties["msg_type"] = MessagePropertyValue.create_string("test")
        messages.append(msg1)
        
        # 第二条消息 - 包含系统属性
        msg2 = MockSendRequest("Message 2")
        msg2.system_properties[SystemPropertyName.TRACEPARENT] = MessageSystemPropertyValue.create_string("trace-2")
        messages.append(msg2)
        
        # 第三条消息 - 包含混合属性
        msg3 = MockSendRequest("Message 3")
        msg3.user_properties["binary_data"] = MessagePropertyValue.create_binary(b"test_binary")
        msg3.system_properties[SystemPropertyName.BAGGAGE] = MessageSystemPropertyValue.create_string("userId=123")
        messages.append(msg3)
        
        xml_result = MessagesEncoder.encode(messages, False)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证第一条消息的用户属性
        self.assertIn("<Name>msg_index</Name>", xml_str)
        self.assertIn("<Value>1</Value>", xml_str)
        self.assertIn("<Type>NUMBER</Type>", xml_str)
        
        # 验证第二条消息的系统属性
        self.assertIn("<Name>traceparent</Name>", xml_str)
        self.assertIn("<Value>trace-2</Value>", xml_str)
        
        # 验证第三条消息的混合属性
        expected_binary = base64.b64encode(b"test_binary").decode('ascii')
        self.assertIn("<Value>%s</Value>" % expected_binary, xml_str)
        self.assertIn("<Name>baggage</Name>", xml_str)
        self.assertIn("<Value>userId=123</Value>", xml_str)
    
    def test_encode_empty_batch_messages(self):
        """测试编码空的批量消息"""
        xml_result = MessagesEncoder.encode([], False)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证空消息结构
        self.assertIn("<Messages", xml_str)
        self.assertNotIn("<Message>", xml_str)
    
    def test_encode_message_with_special_characters(self):
        """测试编码包含特殊字符的属性"""
        req = MockSendRequest("Test message")
        
        # 包含XML特殊字符的属性
        req.user_properties["xml_chars"] = MessagePropertyValue.create_string("<>&\"'")
        req.user_properties["unicode_chars"] = MessagePropertyValue.create_string("🌟🚀💡")
        
        xml_result = MessageEncoder.encode(req)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证XML转义正确
        self.assertIn("<UserProperties>", xml_str)
        # XML应该包含转义后的字符或CDATA
        self.assertTrue(any(char in xml_str for char in ["&lt;", "&gt;", "&amp;", "CDATA"]))
    
    def test_encode_binary_property_edge_cases(self):
        """测试二进制属性边界情况"""
        req = MockSendRequest("Test message")
        
        # 空二进制数据
        req.user_properties["empty_binary"] = MessagePropertyValue.create_binary(b"")
        
        # 包含NULL字节的二进制数据
        req.user_properties["null_binary"] = MessagePropertyValue.create_binary(b"\x00\x01\x02\x03")
        
        # 大数据量二进制
        large_binary = b"x" * 1024
        req.user_properties["large_binary"] = MessagePropertyValue.create_binary(large_binary)
        
        xml_result = MessageEncoder.encode(req)
        xml_str = xml_result.decode('utf-8') if isinstance(xml_result, bytes) else xml_result
        
        # 验证所有二进制属性都被正确编码
        self.assertIn("<Name>empty_binary</Name>", xml_str)
        self.assertIn("<Name>null_binary</Name>", xml_str)
        self.assertIn("<Name>large_binary</Name>", xml_str)
        
        # 验证二进制数据被base64编码
        expected_null_binary = base64.b64encode(b"\x00\x01\x02\x03").decode('ascii')
        self.assertIn("<Value>%s</Value>" % expected_null_binary, xml_str)


if __name__ == '__main__':
    unittest.main()