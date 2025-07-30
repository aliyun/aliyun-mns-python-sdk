#!/usr/bin/env python
# coding=utf8

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from mns.queue import Message
from mns.message_property import (
    MessagePropertyValue, MessageSystemPropertyValue,
    PropertyType, SystemPropertyName
)


class TestMessageWithProperties(unittest.TestCase):
    """测试带属性的消息类"""
    
    def setUp(self):
        """设置测试数据"""
        self.message = Message("Test message body")
    
    def test_add_user_property(self):
        """测试添加用户自定义属性"""
        # 添加字符串属性
        self.message.add_user_property("string_key", MessagePropertyValue.create_string("string_value"))
        
        # 添加数字属性
        self.message.add_user_property("number_key", MessagePropertyValue.create_number(42))
        
        # 添加布尔属性
        self.message.add_user_property("boolean_key", MessagePropertyValue.create_boolean(True))
        
        # 添加二进制属性
        self.message.add_user_property("binary_key", MessagePropertyValue.create_binary(b"binary_data"))
        
        # 验证属性数量
        properties = self.message.get_user_properties()
        self.assertEqual(len(properties), 4)
        
        # 验证属性值
        self.assertEqual(properties["string_key"].get_string_value_by_type(), "string_value")
        self.assertEqual(properties["number_key"].get_string_value_by_type(), "42")
        self.assertEqual(properties["boolean_key"].get_string_value_by_type(), "true")
        self.assertEqual(properties["binary_key"].get_binary_value(), b"binary_data")
    
    def test_add_system_property(self):
        """测试添加系统属性"""
        # 添加 traceparent 属性
        self.message.add_system_property(
            SystemPropertyName.TRACEPARENT,
            MessageSystemPropertyValue.create_string("00-trace-id-01")
        )
        
        # 添加 tracestate 属性
        self.message.add_system_property(
            SystemPropertyName.TRACESTATE,
            MessageSystemPropertyValue.create_string("congo=t61rcWkgMzE")
        )
        
        # 验证属性数量
        properties = self.message.get_system_properties()
        self.assertEqual(len(properties), 2)
        
        # 验证属性值
        self.assertEqual(properties[SystemPropertyName.TRACEPARENT].get_string_value_by_type(), "00-trace-id-01")
        self.assertEqual(properties[SystemPropertyName.TRACESTATE].get_string_value_by_type(), "congo=t61rcWkgMzE")
    
    def test_overwrite_property(self):
        """测试覆盖已存在的属性"""
        # 添加属性
        self.message.add_user_property("test_key", MessagePropertyValue.create_string("old_value"))
        self.assertEqual(self.message.get_user_properties()["test_key"].get_string_value_by_type(), "old_value")
        
        # 覆盖属性
        self.message.add_user_property("test_key", MessagePropertyValue.create_string("new_value"))
        self.assertEqual(self.message.get_user_properties()["test_key"].get_string_value_by_type(), "new_value")
        self.assertEqual(len(self.message.get_user_properties()), 1)
    
    def test_property_type_change(self):
        """测试属性类型变更"""
        # 先添加字符串类型
        self.message.add_user_property("test_key", MessagePropertyValue.create_string("string_value"))
        self.assertEqual(self.message.get_user_properties()["test_key"].get_data_type(), PropertyType.STRING)
        
        # 覆盖为数字类型
        self.message.add_user_property("test_key", MessagePropertyValue.create_number(42))
        self.assertEqual(self.message.get_user_properties()["test_key"].get_data_type(), PropertyType.NUMBER)
        self.assertEqual(self.message.get_user_properties()["test_key"].get_string_value_by_type(), "42")
    
    def test_empty_property_operations(self):
        """测试空属性操作"""
        # 获取空属性字典
        user_props = self.message.get_user_properties()
        system_props = self.message.get_system_properties()
        self.assertEqual(len(user_props), 0)
        self.assertEqual(len(system_props), 0)
        self.assertIsInstance(user_props, dict)
        self.assertIsInstance(system_props, dict)
    
    def test_mixed_properties(self):
        """测试混合属性操作"""
        # 添加各种类型的用户属性
        self.message.add_user_property("str_prop", MessagePropertyValue.create_string("test"))
        self.message.add_user_property("num_prop", MessagePropertyValue.create_number(3.14))
        self.message.add_user_property("bool_prop", MessagePropertyValue.create_boolean(False))
        self.message.add_user_property("bin_prop", MessagePropertyValue.create_binary("binary test"))
        
        # 添加系统属性
        self.message.add_system_property(
            SystemPropertyName.TRACEPARENT,
            MessageSystemPropertyValue.create_string("trace_value")
        )
        
        # 验证总数
        self.assertEqual(len(self.message.get_user_properties()), 4)
        self.assertEqual(len(self.message.get_system_properties()), 1)
        
        # 部分清理
        user_props = self.message.get_user_properties()
        del user_props["num_prop"]
        self.assertEqual(len(self.message.get_user_properties()), 3)
        
        # 验证剩余属性
        remaining_props = self.message.get_user_properties()
        self.assertIn("str_prop", remaining_props)
        self.assertIn("bool_prop", remaining_props)
        self.assertIn("bin_prop", remaining_props)
        self.assertNotIn("num_prop", remaining_props)


if __name__ == '__main__':
    unittest.main()