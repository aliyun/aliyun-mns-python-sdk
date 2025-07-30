#!/usr/bin/env python
# coding=utf8

import unittest
import sys
import os
import base64

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

from mns.message_property import (
    MessagePropertyValue, MessageSystemPropertyValue,
    PropertyType, SystemPropertyType, SystemPropertyName
)


class TestMessagePropertyValue(unittest.TestCase):
    """测试用户自定义属性值类"""
    
    def test_create_string_property(self):
        """测试创建字符串类型属性"""
        # 正常字符串
        prop = MessagePropertyValue.create_string("test_value")
        self.assertEqual(prop.get_data_type(), PropertyType.STRING)
        self.assertEqual(prop.get_string_value_by_type(), "test_value")
        self.assertEqual(prop.get_raw_value(), "test_value")
        
        # 空字符串
        prop_empty = MessagePropertyValue.create_string("")
        self.assertEqual(prop_empty.get_string_value_by_type(), "")
        
        # 中文字符串
        prop_chinese = MessagePropertyValue.create_string("你好世界")
        self.assertEqual(prop_chinese.get_string_value_by_type(), "你好世界")
        
        # Unicode 字符串
        prop_unicode = MessagePropertyValue.create_string(u"Unicode测试")
        self.assertEqual(prop_unicode.get_string_value_by_type(), u"Unicode测试")
    
    def test_create_number_property(self):
        """测试创建数字类型属性"""
        # 整数
        prop_int = MessagePropertyValue.create_number(42)
        self.assertEqual(prop_int.get_data_type(), PropertyType.NUMBER)
        self.assertEqual(prop_int.get_string_value_by_type(), "42")
        
        # 浮点数
        prop_float = MessagePropertyValue.create_number(3.14)
        self.assertEqual(prop_float.get_string_value_by_type(), "3.14")
        
        # 负数
        prop_negative = MessagePropertyValue.create_number(-100)
        self.assertEqual(prop_negative.get_string_value_by_type(), "-100")
        
        # 零
        prop_zero = MessagePropertyValue.create_number(0)
        self.assertEqual(prop_zero.get_string_value_by_type(), "0")
        
        # 字符串形式的数字
        prop_str_num = MessagePropertyValue.create_number("123.45")
        self.assertEqual(prop_str_num.get_string_value_by_type(), "123.45")
        
        # 无效数字应该抛出异常
        with self.assertRaises(ValueError):
            MessagePropertyValue.create_number("not_a_number")
    
    def test_create_boolean_property(self):
        """测试创建布尔类型属性"""
        # 布尔值 True
        prop_true = MessagePropertyValue.create_boolean(True)
        self.assertEqual(prop_true.get_data_type(), PropertyType.BOOLEAN)
        self.assertEqual(prop_true.get_string_value_by_type(), "true")
        
        # 布尔值 False
        prop_false = MessagePropertyValue.create_boolean(False)
        self.assertEqual(prop_false.get_string_value_by_type(), "false")
        
        # 字符串 "true"
        prop_str_true = MessagePropertyValue.create_boolean("true")
        self.assertEqual(prop_str_true.get_string_value_by_type(), "true")
        
        # 字符串 "false"
        prop_str_false = MessagePropertyValue.create_boolean("false")
        self.assertEqual(prop_str_false.get_string_value_by_type(), "false")
        
        # 字符串 "TRUE" (大写)
        prop_upper_true = MessagePropertyValue.create_boolean("TRUE")
        self.assertEqual(prop_upper_true.get_string_value_by_type(), "true")
        
        # 无效布尔值应该抛出异常
        with self.assertRaises(ValueError):
            MessagePropertyValue.create_boolean("invalid_bool")
        
        with self.assertRaises(ValueError):
            MessagePropertyValue.create_boolean(1)
    
    def test_create_binary_property(self):
        """测试创建二进制类型属性"""
        # bytes 类型
        binary_data = b"Hello World"
        prop_bytes = MessagePropertyValue.create_binary(binary_data)
        self.assertEqual(prop_bytes.get_data_type(), PropertyType.BINARY)
        self.assertEqual(prop_bytes.get_binary_value(), binary_data)
        self.assertEqual(prop_bytes.get_string_value_by_type(), "Hello World")
        
        # 字符串类型 (会转换为 bytes)
        prop_str = MessagePropertyValue.create_binary("Test String")
        self.assertEqual(prop_str.get_binary_value(), b"Test String")
        self.assertEqual(prop_str.get_string_value_by_type(), "Test String")
        
        # 中文字符串
        chinese_str = "你好世界"
        prop_chinese = MessagePropertyValue.create_binary(chinese_str)
        self.assertEqual(prop_chinese.get_string_value_by_type(), chinese_str)
        
        # 包含非 UTF-8 字节的数据
        non_utf8_bytes = b"\x80\x81\x82\x83"
        prop_non_utf8 = MessagePropertyValue.create_binary(non_utf8_bytes)
        self.assertEqual(prop_non_utf8.get_binary_value(), non_utf8_bytes)
        # 非UTF-8字节应该返回十六进制表示
        hex_result = prop_non_utf8.get_string_value_by_type()
        self.assertTrue(isinstance(hex_result, str))
        
        # 无效类型应该抛出异常
        with self.assertRaises(ValueError):
            MessagePropertyValue.create_binary(123)
        
        with self.assertRaises(ValueError):
            MessagePropertyValue.create_binary(None)
    
    def test_invalid_property_creation(self):
        """测试无效属性创建"""
        # None 值
        with self.assertRaises(ValueError):
            MessagePropertyValue(PropertyType.STRING, None)
        
        # None 类型
        with self.assertRaises(ValueError):
            MessagePropertyValue(None, "value")
        
        # 无效类型
        with self.assertRaises(ValueError):
            MessagePropertyValue("INVALID_TYPE", "value")
    
    def test_get_binary_value_for_non_binary(self):
        """测试非二进制类型调用 get_binary_value"""
        prop = MessagePropertyValue.create_string("test")
        with self.assertRaises(ValueError):
            prop.get_binary_value()


class TestMessageSystemPropertyValue(unittest.TestCase):
    """测试系统属性值类"""
    
    def test_create_system_property(self):
        """测试创建系统属性"""
        prop = MessageSystemPropertyValue.create_string("trace_value")
        self.assertEqual(prop.get_data_type(), SystemPropertyType.STRING)
        self.assertEqual(prop.get_string_value_by_type(), "trace_value")
        
        # 空字符串
        prop_empty = MessageSystemPropertyValue.create_string("")
        self.assertEqual(prop_empty.get_string_value_by_type(), "")
        
        # 中文字符串
        prop_chinese = MessageSystemPropertyValue.create_string("系统属性测试")
        self.assertEqual(prop_chinese.get_string_value_by_type(), "系统属性测试")
    
    def test_invalid_system_property_creation(self):
        """测试无效系统属性创建"""
        with self.assertRaises(ValueError):
            MessageSystemPropertyValue(SystemPropertyType.STRING, None)
        
        with self.assertRaises(ValueError):
            MessageSystemPropertyValue(None, "value")


class TestPropertyTypes(unittest.TestCase):
    """测试属性类型常量类"""
    
    def test_property_type_validation(self):
        """测试属性类型验证"""
        self.assertTrue(PropertyType.is_valid(PropertyType.STRING))
        self.assertTrue(PropertyType.is_valid(PropertyType.NUMBER))
        self.assertTrue(PropertyType.is_valid(PropertyType.BOOLEAN))
        self.assertTrue(PropertyType.is_valid(PropertyType.BINARY))
        self.assertFalse(PropertyType.is_valid("INVALID"))
        self.assertFalse(PropertyType.is_valid(None))
    
    def test_property_type_list(self):
        """测试获取所有属性类型"""
        types = PropertyType.values()
        self.assertIn(PropertyType.STRING, types)
        self.assertIn(PropertyType.NUMBER, types)
        self.assertIn(PropertyType.BOOLEAN, types)
        self.assertIn(PropertyType.BINARY, types)
        self.assertEqual(len(types), 4)
    
    def test_system_property_type_validation(self):
        """测试系统属性类型验证"""
        self.assertTrue(SystemPropertyType.is_valid(SystemPropertyType.STRING))
        self.assertFalse(SystemPropertyType.is_valid("INVALID"))
        self.assertFalse(SystemPropertyType.is_valid(None))
    
    def test_system_property_type_list(self):
        """测试获取所有系统属性类型"""
        types = SystemPropertyType.values()
        self.assertIn(SystemPropertyType.STRING, types)
        self.assertEqual(len(types), 1)
    
    def test_system_property_name_validation(self):
        """测试系统属性名称验证"""
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.TRACEPARENT))
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.TRACESTATE))
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.BAGGAGE))
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.DLQ_MESSAGE_TYPE))
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.DLQ_SOURCE_ARN))
        self.assertTrue(SystemPropertyName.is_valid(SystemPropertyName.DLQ_ORIGIN_MESSAGE_ID))
        self.assertFalse(SystemPropertyName.is_valid("invalid_name"))
        self.assertFalse(SystemPropertyName.is_valid(None))
    
    def test_system_property_name_list(self):
        """测试获取所有系统属性名称"""
        names = SystemPropertyName.values()
        self.assertIn(SystemPropertyName.TRACEPARENT, names)
        self.assertIn(SystemPropertyName.TRACESTATE, names)
        self.assertIn(SystemPropertyName.BAGGAGE, names)
        self.assertIn(SystemPropertyName.DLQ_MESSAGE_TYPE, names)
        self.assertIn(SystemPropertyName.DLQ_SOURCE_ARN, names)
        self.assertIn(SystemPropertyName.DLQ_ORIGIN_MESSAGE_ID, names)
        self.assertEqual(len(names), 6)


if __name__ == '__main__':
    unittest.main()