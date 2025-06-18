#!/usr/bin/env python
# coding=utf8

import unittest
import sys
import os
import base64

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from mns.mns_xml_handler import (
    RecvMessageDecoder, PeekMessageDecoder, 
    BatchRecvMessageDecoder, BatchPeekMessageDecoder,
    DecoderBase
)
from mns.message_property import PropertyType, SystemPropertyName


class TestMessageDecoding(unittest.TestCase):
    """测试消息解码功能"""
    
    def test_decode_message_without_properties(self):
        """测试解码不包含属性的消息"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>Hello World</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>1</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <NextVisibleTime>1609459320</NextVisibleTime>
            <ReceiptHandle>receipt123</ReceiptHandle>
            <Priority>8</Priority>
        </Message>"""
        
        result = RecvMessageDecoder.decode(xml_data, False)
        
        # 验证基本字段
        self.assertEqual(result["MessageId"], "12345")
        self.assertEqual(result["MessageBody"], "Hello World")
        self.assertEqual(result["Priority"], "8")
        
        # 验证没有属性
        self.assertNotIn("UserProperties", result)
        self.assertNotIn("SystemProperties", result)
    
    def test_decode_message_with_user_properties(self):
        """测试解码包含用户属性的消息"""
        binary_data = base64.b64encode(b"binary_test").decode('ascii')
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>Test Message</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>1</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <NextVisibleTime>1609459320</NextVisibleTime>
            <ReceiptHandle>receipt123</ReceiptHandle>
            <Priority>8</Priority>
            <UserProperties>
                <PropertyValue>
                    <Name>string_prop</Name>
                    <Value>test_value</Value>
                    <Type>STRING</Type>
                </PropertyValue>
                <PropertyValue>
                    <Name>number_prop</Name>
                    <Value>42</Value>
                    <Type>NUMBER</Type>
                </PropertyValue>
                <PropertyValue>
                    <Name>boolean_prop</Name>
                    <Value>true</Value>
                    <Type>BOOLEAN</Type>
                </PropertyValue>
                <PropertyValue>
                    <Name>binary_prop</Name>
                    <Value>%s</Value>
                    <Type>BINARY</Type>
                </PropertyValue>
            </UserProperties>
        </Message>""" % binary_data
        
        result = RecvMessageDecoder.decode(xml_data, False)
        
        # 验证用户属性存在
        self.assertIn("UserProperties", result)
        user_props = result["UserProperties"]
        
        # 验证属性数量和内容
        self.assertEqual(len(user_props), 4)
        
        # 验证字符串属性
        string_prop = user_props["string_prop"]
        self.assertEqual(string_prop.get_data_type(), PropertyType.STRING)
        self.assertEqual(string_prop.get_string_value_by_type(), "test_value")
        
        # 验证数字属性
        number_prop = user_props["number_prop"]
        self.assertEqual(number_prop.get_data_type(), PropertyType.NUMBER)
        self.assertEqual(number_prop.get_string_value_by_type(), "42")
        
        # 验证布尔属性
        boolean_prop = user_props["boolean_prop"]
        self.assertEqual(boolean_prop.get_data_type(), PropertyType.BOOLEAN)
        self.assertEqual(boolean_prop.get_string_value_by_type(), "true")
        
        # 验证二进制属性
        binary_prop = user_props["binary_prop"]
        self.assertEqual(binary_prop.get_data_type(), PropertyType.BINARY)
        self.assertEqual(binary_prop.get_binary_value(), b"binary_test")
    
    def test_decode_message_with_system_properties(self):
        """测试解码包含系统属性的消息"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>Test Message</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>1</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <NextVisibleTime>1609459320</NextVisibleTime>
            <ReceiptHandle>receipt123</ReceiptHandle>
            <Priority>8</Priority>
            <SystemProperties>
                <SystemPropertyValue>
                    <Name>traceparent</Name>
                    <Value>00-4bf92f3577b34da6a3ce929d0e0e4735-00f067aa0ba902b7-01</Value>
                    <Type>STRING</Type>
                </SystemPropertyValue>
                <SystemPropertyValue>
                    <Name>tracestate</Name>
                    <Value>congo=t61rcWkgMzE</Value>
                    <Type>STRING</Type>
                </SystemPropertyValue>
            </SystemProperties>
        </Message>"""
        
        result = RecvMessageDecoder.decode(xml_data, False)
        
        # 验证系统属性存在
        self.assertIn("SystemProperties", result)
        system_props = result["SystemProperties"]
        
        # 验证属性数量和内容
        self.assertEqual(len(system_props), 2)
        
        # 验证 traceparent 属性
        traceparent_prop = system_props[SystemPropertyName.TRACEPARENT]
        self.assertEqual(traceparent_prop.get_string_value_by_type(), "00-4bf92f3577b34da6a3ce929d0e0e4735-00f067aa0ba902b7-01")
        
        # 验证 tracestate 属性
        tracestate_prop = system_props[SystemPropertyName.TRACESTATE]
        self.assertEqual(tracestate_prop.get_string_value_by_type(), "congo=t61rcWkgMzE")
    
    def test_decode_message_with_base64_body(self):
        """测试解码base64编码的消息体"""
        encoded_body = base64.b64encode("你好世界".encode('utf-8')).decode('ascii')
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>%s</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>1</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <NextVisibleTime>1609459320</NextVisibleTime>
            <ReceiptHandle>receipt123</ReceiptHandle>
            <Priority>8</Priority>
        </Message>""" % encoded_body
        
        result = RecvMessageDecoder.decode(xml_data, True)  # base64decode=True
        
        # 验证消息体被正确解码
        self.assertEqual(result["MessageBody"], "你好世界".encode('utf-8'))
    
    def test_decode_peek_message_with_properties(self):
        """测试解码查看消息（peek）包含属性"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>Peek Test</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>0</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <Priority>8</Priority>
            <UserProperties>
                <PropertyValue>
                    <Name>peek_prop</Name>
                    <Value>peek_value</Value>
                    <Type>STRING</Type>
                </PropertyValue>
            </UserProperties>
        </Message>"""
        
        result = PeekMessageDecoder.decode(xml_data, False)
        
        # 验证基本字段
        self.assertEqual(result["MessageBody"], "Peek Test")
        
        # 验证属性
        self.assertIn("UserProperties", result)
        user_props = result["UserProperties"]
        self.assertEqual(len(user_props), 1)
        self.assertEqual(user_props["peek_prop"].get_string_value_by_type(), "peek_value")
    
    def test_decode_batch_messages_with_properties(self):
        """测试解码批量消息包含属性"""
        binary_data = base64.b64encode(b"batch_binary").decode('ascii')
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Messages xmlns="http://mns.aliyuncs.com/doc/v1/">
            <Message>
                <MessageId>msg1</MessageId>
                <MessageBody>Batch Message 1</MessageBody>
                <MessageBodyMD5>abc123</MessageBodyMD5>
                <DequeueCount>1</DequeueCount>
                <EnqueueTime>1609459200</EnqueueTime>
                <FirstDequeueTime>1609459260</FirstDequeueTime>
                <NextVisibleTime>1609459320</NextVisibleTime>
                <ReceiptHandle>receipt1</ReceiptHandle>
                <Priority>8</Priority>
                <UserProperties>
                    <PropertyValue>
                        <Name>batch_index</Name>
                        <Value>1</Value>
                        <Type>NUMBER</Type>
                    </PropertyValue>
                </UserProperties>
            </Message>
            <Message>
                <MessageId>msg2</MessageId>
                <MessageBody>Batch Message 2</MessageBody>
                <MessageBodyMD5>def456</MessageBodyMD5>
                <DequeueCount>1</DequeueCount>
                <EnqueueTime>1609459201</EnqueueTime>
                <FirstDequeueTime>1609459261</FirstDequeueTime>
                <NextVisibleTime>1609459321</NextVisibleTime>
                <ReceiptHandle>receipt2</ReceiptHandle>
                <Priority>8</Priority>
                <UserProperties>
                    <PropertyValue>
                        <Name>binary_data</Name>
                        <Value>%s</Value>
                        <Type>BINARY</Type>
                    </PropertyValue>
                </UserProperties>
                <SystemProperties>
                    <SystemPropertyValue>
                        <Name>traceparent</Name>
                        <Value>trace-value-2</Value>
                        <Type>STRING</Type>
                    </SystemPropertyValue>
                </SystemProperties>
            </Message>
        </Messages>""" % binary_data
        
        result = BatchRecvMessageDecoder.decode(xml_data, False)
        
        # 验证消息数量
        self.assertEqual(len(result), 2)
        
        # 验证第一条消息
        msg1 = result[0]
        self.assertEqual(msg1.message_id, "msg1")
        self.assertEqual(msg1.message_body, "Batch Message 1")
        self.assertEqual(len(msg1.user_properties), 1)
        self.assertEqual(msg1.user_properties["batch_index"].get_string_value_by_type(), "1")
        
        # 验证第二条消息
        msg2 = result[1]
        self.assertEqual(msg2.message_id, "msg2")
        self.assertEqual(len(msg2.user_properties), 1)
        self.assertEqual(len(msg2.system_properties), 1)
        self.assertEqual(msg2.user_properties["binary_data"].get_binary_value(), b"batch_binary")
        self.assertEqual(msg2.system_properties[SystemPropertyName.TRACEPARENT].get_string_value_by_type(), "trace-value-2")
    
    def test_decode_invalid_binary_property_xml(self):
        """测试解码无效二进制属性XML时抛出异常"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Message xmlns="http://mns.aliyuncs.com/doc/v1/">
            <MessageId>12345</MessageId>
            <MessageBody>Test Message</MessageBody>
            <MessageBodyMD5>abc123</MessageBodyMD5>
            <DequeueCount>1</DequeueCount>
            <EnqueueTime>1609459200</EnqueueTime>
            <FirstDequeueTime>1609459260</FirstDequeueTime>
            <NextVisibleTime>1609459320</NextVisibleTime>
            <ReceiptHandle>receipt123</ReceiptHandle>
            <Priority>8</Priority>
            <UserProperties>
                <PropertyValue>
                    <Name>invalid_binary</Name>
                    <Value>invalid_base64_!@#$%</Value>
                    <Type>BINARY</Type>
                </PropertyValue>
            </UserProperties>
        </Message>"""
        
        # 期望抛出异常
        with self.assertRaises(Exception):
            RecvMessageDecoder.decode(xml_data, False)
    
    def test_decode_empty_batch_messages(self):
        """测试解码空的批量消息"""
        xml_data = """<?xml version="1.0" encoding="UTF-8"?>
        <Messages xmlns="http://mns.aliyuncs.com/doc/v1/">
        </Messages>"""
        
        result = BatchRecvMessageDecoder.decode(xml_data, False)
        self.assertEqual(len(result), 0)


class TestDecoderBasePropertyParsing(unittest.TestCase):
    """测试解码器基类的属性解析功能"""
    
    def test_parse_user_properties_from_dict(self):
        """测试从字典解析用户属性"""
        data_dic = {
            "UserProperties": {
                "PropertyValue": [
                    {"Name": "str_prop", "Value": "test", "Type": "STRING"},
                    {"Name": "num_prop", "Value": "42", "Type": "NUMBER"},
                    {"Name": "bool_prop", "Value": "false", "Type": "BOOLEAN"},
                    {"Name": "bin_prop", "Value": base64.b64encode(b"binary").decode('ascii'), "Type": "BINARY"}
                ]
            }
        }
        
        result = DecoderBase.parse_user_properties_from_dict(data_dic)
        
        self.assertEqual(len(result), 4)
        self.assertEqual(result["str_prop"].get_string_value_by_type(), "test")
        self.assertEqual(result["num_prop"].get_string_value_by_type(), "42")
        self.assertEqual(result["bool_prop"].get_string_value_by_type(), "false")
        self.assertEqual(result["bin_prop"].get_binary_value(), b"binary")
    
    def test_parse_system_properties_from_dict(self):
        """测试从字典解析系统属性"""
        data_dic = {
            "SystemProperties": {
                "SystemPropertyValue": [
                    {"Name": "traceparent", "Value": "trace-value", "Type": "STRING"}
                ]
            }
        }
        
        result = DecoderBase.parse_system_properties_from_dict(data_dic)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result["traceparent"].get_string_value_by_type(), "trace-value")
    
    def test_parse_properties_with_single_property(self):
        """测试解析单个属性（非列表格式）"""
        data_dic = {
            "UserProperties": {
                "PropertyValue": {"Name": "single_prop", "Value": "single_value", "Type": "STRING"}
            }
        }
        
        result = DecoderBase.parse_user_properties_from_dict(data_dic)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result["single_prop"].get_string_value_by_type(), "single_value")
    
    def test_parse_properties_empty_dict(self):
        """测试解析空属性字典"""
        data_dic = {}
        
        user_result = DecoderBase.parse_user_properties_from_dict(data_dic)
        system_result = DecoderBase.parse_system_properties_from_dict(data_dic)
        
        self.assertEqual(len(user_result), 0)
        self.assertEqual(len(system_result), 0)


if __name__ == '__main__':
    unittest.main()