#!/usr/bin/env python
# coding=utf8

import base64
import sys

class PropertyType(object):
    """用户自定义属性值类型常量类"""
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    BINARY = "BINARY"
    
    @classmethod
    def values(cls):
        """获取所有类型值"""
        return [cls.NUMBER, cls.STRING, cls.BOOLEAN, cls.BINARY]
    
    @classmethod
    def is_valid(cls, value):
        """检查是否为有效类型"""
        return value in cls.values()

class SystemPropertyType(object):
    """系统属性值类型常量类"""
    STRING = "STRING"
    
    @classmethod
    def values(cls):
        """获取所有类型值"""
        return [cls.STRING]
    
    @classmethod
    def is_valid(cls, value):
        """检查是否为有效类型"""
        return value in cls.values()

class SystemPropertyName(object):
    """系统属性名称枚举类"""
    TRACEPARENT = "traceparent"
    TRACESTATE = "tracestate"
    BAGGAGE = "baggage"
    DLQ_MESSAGE_TYPE = "DLQMessageType"
    DLQ_SOURCE_ARN = "DLQSourceArn"
    DLQ_ORIGIN_MESSAGE_ID = "DLQOriginMessageId"
    
    @classmethod
    def values(cls):
        """获取所有有效的系统属性名称"""
        return [cls.TRACEPARENT, cls.TRACESTATE, cls.BAGGAGE, 
                cls.DLQ_MESSAGE_TYPE, cls.DLQ_SOURCE_ARN, cls.DLQ_ORIGIN_MESSAGE_ID]
    
    @classmethod
    def is_valid(cls, name):
        """检查是否为有效的系统属性名称"""
        return name in cls.values()

class MessagePropertyValue(object):
    """用户自定义消息属性值类，支持显式类型声明"""
    
    def __init__(self, data_type=None, value=None):
        """
        初始化消息属性值
        
        @param data_type: PropertyType 属性类型
        @param value: 属性值
        """
        if data_type is None or value is None:
            raise ValueError("data_type and value cannot be None")
            
        if not PropertyType.is_valid(data_type):
            raise ValueError("Invalid property type: %s" % data_type)
            
        self.data_type = data_type
        self.string_value = None
        self.binary_value = None
        
        if data_type == PropertyType.NUMBER:
            try:
                # 校验是否是数字
                float(str(value))
                self.string_value = str(value)
            except ValueError:
                raise ValueError("Invalid number format: %s" % value)
        elif data_type == PropertyType.STRING:
            # Python 2/3 兼容的字符串处理
            if sys.version_info[0] >= 3:
                self.string_value = str(value)
            else:
                if isinstance(value, str):
                    self.string_value = unicode(value, 'utf-8')
                elif isinstance(value, unicode):
                    self.string_value = value
                else:
                    self.string_value = unicode(str(value))
        elif data_type == PropertyType.BOOLEAN:
            # 校验是否为合法的布尔值
            if isinstance(value, bool):
                self.string_value = str(value).lower()
            elif str(value).lower() in ['true', 'false']:
                self.string_value = str(value).lower()
            else:
                raise ValueError("Invalid boolean value: %s" % value)
        elif data_type == PropertyType.BINARY:
            if isinstance(value, bytes):
                self.binary_value = value
            elif isinstance(value, str):
                try:
                    if sys.version_info[0] >= 3:
                        self.binary_value = value.encode('utf-8')
                    else:
                        self.binary_value = value
                except UnicodeEncodeError:
                    raise ValueError("Invalid string encoding for binary type")
            else:
                raise ValueError("Binary type value must be bytes or string")
        else:
            raise ValueError("Unsupported property type: %s" % data_type)
    
    @classmethod
    def create_string(cls, value):
        """创建字符串类型属性值"""
        return cls(PropertyType.STRING, value)
    
    @classmethod
    def create_number(cls, value):
        """创建数字类型属性值"""
        return cls(PropertyType.NUMBER, value)
    
    @classmethod
    def create_boolean(cls, value):
        """创建布尔类型属性值"""
        return cls(PropertyType.BOOLEAN, value)
    
    @classmethod
    def create_binary(cls, value):
        """创建二进制类型属性值"""
        return cls(PropertyType.BINARY, value)
    
    def get_string_value_by_type(self):
        """根据类型获取字符串值，不做 base64 编码"""
        if self.data_type in [PropertyType.NUMBER, PropertyType.STRING, PropertyType.BOOLEAN]:
            return self.string_value
        elif self.data_type == PropertyType.BINARY:
            # 二进制类型使用 utf-8 解码为字符串
            try:
                return self.binary_value.decode('utf-8')
            except UnicodeDecodeError:
                # 如果不是有效的 utf-8，返回原始字节的十六进制表示
                return self.binary_value.hex() if hasattr(self.binary_value, 'hex') else self.binary_value.encode('hex')
        else:
            return ""
    
    def get_data_type(self):
        """获取数据类型"""
        return self.data_type
    
    def get_raw_value(self):
        """获取原始值"""
        if self.data_type == PropertyType.BINARY:
            return self.binary_value
        else:
            return self.string_value

    def get_binary_value(self):
        """获取二进制值，仅用于二进制类型"""
        if self.data_type == PropertyType.BINARY:
            return self.binary_value
        else:
            raise ValueError("This property is not binary type")

class MessageSystemPropertyValue(object):
    """系统消息属性值类"""
    
    def __init__(self, data_type=None, value=None):
        """
        初始化系统属性值
        
        @param data_type: SystemPropertyType 属性类型
        @param value: 属性值
        """
        if data_type is None or value is None:
            raise ValueError("data_type and value cannot be None")
            
        if not SystemPropertyType.is_valid(data_type):
            raise ValueError("Invalid system property type: %s" % data_type)
            
        self.data_type = data_type
        self.string_value = None
        
        if data_type == SystemPropertyType.STRING:
            # Python 2/3 兼容的字符串处理
            if sys.version_info[0] >= 3:
                self.string_value = str(value)
            else:
                if isinstance(value, str):
                    self.string_value = unicode(value, 'utf-8')
                elif isinstance(value, unicode):
                    self.string_value = value
                else:
                    self.string_value = unicode(str(value))
        else:
            raise ValueError("Unsupported system property type: %s" % data_type)
    
    @classmethod
    def create_string(cls, value):
        """创建字符串类型系统属性值"""
        return cls(SystemPropertyType.STRING, value)
    
    def get_string_value_by_type(self):
        """根据类型获取字符串值，用于序列化"""
        return self.string_value
    
    def get_data_type(self):
        """获取数据类型"""
        return self.data_type
    
    def get_raw_value(self):
        """获取原始值"""
        return self.string_value