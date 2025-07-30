#coding=utf-8
# Copyright (C) 2015, Alibaba Cloud Computing

#Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import xml.dom.minidom
import sys
import base64
import string
import types
from xml.etree import ElementTree
from .mns_exception import *
from .mns_request import *
from .message_property import MessagePropertyValue, PropertyType, MessageSystemPropertyValue, SystemPropertyType
try:
    import json
except ImportError:
    import simplejson as json

XMLNS = "http://mns.aliyuncs.com/doc/v1/"
class EncoderBase:
    @staticmethod
    def insert_if_valid(item_name, item_value, invalid_value, data_dic):
        if item_value != invalid_value:
            data_dic[item_name] = item_value

    @staticmethod
    def list_to_xml(tag_name1, tag_name2, data_list):
        doc = xml.dom.minidom.Document()
        rootNode = doc.createElement(tag_name1)
        rootNode.attributes["xmlns"] = XMLNS
        doc.appendChild(rootNode)
        if data_list:
            for item in data_list:
                keyNode = doc.createElement(tag_name2)
                rootNode.appendChild(keyNode)
                keyNode.appendChild(doc.createTextNode(item))
        else:
            nullNode = doc.createTextNode("")
            rootNode.appendChild(nullNode)
        return doc.toxml("utf-8")

    @staticmethod
    def dic_to_xml(tag_name, data_dic):
        doc = xml.dom.minidom.Document()
        rootNode = doc.createElement(tag_name)
        rootNode.attributes["xmlns"] = XMLNS
        doc.appendChild(rootNode)
        if data_dic:
            for k,v in data_dic.items():
                keyNode = doc.createElement(k)
                if type(v) is dict:
                    for subkey,subv in v.items():
                        if isinstance(subv, list):
                            # 处理列表类型 (如 PropertyValue 列表)
                            for item in subv:
                                subNode = doc.createElement(subkey)
                                if isinstance(item, dict):
                                    for itemkey, itemvalue in item.items():
                                        itemNode = doc.createElement(itemkey)
                                        itemNode.appendChild(doc.createTextNode(str(itemvalue)))
                                        subNode.appendChild(itemNode)
                                else:
                                    subNode.appendChild(doc.createTextNode(str(item)))
                                keyNode.appendChild(subNode)
                        else:
                            subNode = doc.createElement(subkey)
                            subNode.appendChild(doc.createTextNode(str(subv)))
                            keyNode.appendChild(subNode)
                else:
                    #tmp = doc.createTextNode(v.decode('utf-8'))
                    tmp = doc.createTextNode(v)
                    keyNode.appendChild(tmp)
                    #keyNode.appendChild(doc.createTextNode(v))
                rootNode.appendChild(keyNode)
        else:
            nullNode = doc.createTextNode("")
            rootNode.appendChild(nullNode)
        return doc.toxml("utf-8")

    @staticmethod
    def listofdic_to_xml(root_tagname, sec_tagname, dataList):
        doc = xml.dom.minidom.Document()
        rootNode = doc.createElement(root_tagname)
        rootNode.attributes["xmlns"] = XMLNS
        doc.appendChild(rootNode)
        if dataList:
            for subData in dataList:
                secNode = doc.createElement(sec_tagname)
                rootNode.appendChild(secNode)
                if not subData:
                    nullNode = doc.createTextNode("")
                    secNode.appendChild(nullNode)
                    continue
                for k,v in subData.items():
                    keyNode = doc.createElement(k)
                    secNode.appendChild(keyNode)
                    
                    # 检查是否是嵌套的字典结构（如属性）
                    if isinstance(v, dict):
                        # 处理嵌套结构，如 UserProperties 和 SystemProperties
                        for subkey, subv in v.items():
                            if isinstance(subv, list):
                                # 处理列表类型 (如 PropertyValue 列表)
                                for item in subv:
                                    subNode = doc.createElement(subkey)
                                    if isinstance(item, dict):
                                        for itemkey, itemvalue in item.items():
                                            itemNode = doc.createElement(itemkey)
                                            itemNode.appendChild(doc.createTextNode(str(itemvalue)))
                                            subNode.appendChild(itemNode)
                                    else:
                                        subNode.appendChild(doc.createTextNode(str(item)))
                                    keyNode.appendChild(subNode)
                            else:
                                # 处理简单的嵌套值
                                subNode = doc.createElement(subkey)
                                subNode.appendChild(doc.createTextNode(str(subv)))
                                keyNode.appendChild(subNode)
                    else:
                        # 处理简单值
                        keyNode.appendChild(doc.createTextNode(str(v)))
        else:
            nullNode = doc.createTextNode("")
            rootNode.appendChild(nullNode)
        return doc.toxml("utf-8")

class SetAccountAttrEncoder(EncoderBase):
    @staticmethod
    def encode(data):
        account_attr = {}
        EncoderBase.insert_if_valid("LoggingBucket", data.logging_bucket, None, account_attr)
        return EncoderBase.dic_to_xml("Account", account_attr)

class QueueEncoder(EncoderBase):
    @staticmethod
    def encode(data, has_slice = True):
        queue = {}
        EncoderBase.insert_if_valid("VisibilityTimeout", str(data.visibility_timeout), "-1", queue)
        EncoderBase.insert_if_valid("MaximumMessageSize", str(data.maximum_message_size), "-1", queue)
        EncoderBase.insert_if_valid("MessageRetentionPeriod", str(data.message_retention_period), "-1", queue)
        EncoderBase.insert_if_valid("DelaySeconds", str(data.delay_seconds), "-1", queue)
        EncoderBase.insert_if_valid("PollingWaitSeconds", str(data.polling_wait_seconds), "-1", queue)

        logging_enabled = str(data.logging_enabled)
        if str(data.logging_enabled).lower() == "true":
            logging_enabled = "True"
        elif str(data.logging_enabled).lower() == "false":
            logging_enabled = "False"
        EncoderBase.insert_if_valid("LoggingEnabled", logging_enabled, "None", queue)
        return EncoderBase.dic_to_xml("Queue", queue)

class MessageEncoder(EncoderBase):
    @staticmethod
    def encode(data):
        message = {}
        if data.base64encode:
            #base64 only support str
            tmpbody = data.message_body.encode('utf-8')
            msgbody = base64.b64encode(tmpbody).decode('utf-8')
        else:
            #xml only support unicode when contains Chinese
            if sys.version_info.major >= 3:
                msgbody = data.message_body
            else:
                msgbody = data.message_body.decode('utf-8') if isinstance(data.message_body, str) else data.message_body
        EncoderBase.insert_if_valid("MessageBody", msgbody, u"", message)
        EncoderBase.insert_if_valid("DelaySeconds", str(data.delay_seconds), u"-1", message)
        EncoderBase.insert_if_valid("Priority", str(data.priority), u"-1", message)
        EncoderBase.insert_if_valid("MessageGroupId", data.message_group_id, "", message)

        # 添加用户自定义属性序列化
        if hasattr(data, 'user_properties') and data.user_properties:
            user_props_list = []
            for name, prop_value in data.user_properties.items():
                # 根据类型决定如何获取值
                if prop_value.get_data_type() == PropertyType.BINARY:
                    # 二进制类型：进行 base64 编码
                    encoded_value = base64.b64encode(prop_value.get_binary_value()).decode('ascii')
                else:
                    # 其他类型：直接获取字符串值
                    encoded_value = prop_value.get_string_value_by_type()
                property_value_dict = {
                    "Name": name,
                    "Value": encoded_value,
                    "Type": prop_value.get_data_type()
                }
                user_props_list.append(property_value_dict)
            if user_props_list:
                message["UserProperties"] = {"PropertyValue": user_props_list}
        
        # 添加系统属性序列化
        if hasattr(data, 'system_properties') and data.system_properties:
            sys_props_list = []
            for name, prop_value in data.system_properties.items():
                system_property_value_dict = {
                    "Name": name,
                    "Value": prop_value.get_string_value_by_type(),
                    "Type": prop_value.get_data_type()
                }
                sys_props_list.append(system_property_value_dict)
            if sys_props_list:
                message["SystemProperties"] = {"SystemPropertyValue": sys_props_list}

        return EncoderBase.dic_to_xml("Message", message)

class MessagesEncoder:
    @staticmethod
    def encode(message_list, base64encode):
        msglist = []
        for msg in message_list:
            item = {}
            if base64encode:
                #base64 only support str
                #tmpbody = msg.message_body.encode('utf-8') if isinstance(msg.message_body, unicode) else msg.message_body
                tmpbody = msg.message_body.encode('utf-8')
                msgbody = base64.b64encode(tmpbody).decode('utf-8')
            else:
                #xml only support unicode when contains Chinese
                if sys.version_info.major >= 3:
                    msgbody = msg.message_body
                else:
                    msgbody = msg.message_body.decode('utf-8') if isinstance(msg.message_body, str) else msg.message_body
            EncoderBase.insert_if_valid("MessageBody", msgbody, u"", item)
            EncoderBase.insert_if_valid("DelaySeconds", str(msg.delay_seconds), u"-1", item)
            EncoderBase.insert_if_valid("Priority", str(msg.priority), u"-1", item)
            EncoderBase.insert_if_valid("MessageGroupId", msg.message_group_id, "", item)

            # 添加用户自定义属性序列化
            if hasattr(msg, 'user_properties') and msg.user_properties:
                user_props_list = []
                for name, prop_value in msg.user_properties.items():
                    # 根据类型决定如何获取值
                    if prop_value.get_data_type() == PropertyType.BINARY:
                        # 二进制类型：进行 base64 编码
                        encoded_value = base64.b64encode(prop_value.get_binary_value()).decode('ascii')
                    else:
                        # 其他类型：直接获取字符串值
                        encoded_value = prop_value.get_string_value_by_type()
                    property_value_dict = {
                        "Name": name,
                        "Value": encoded_value,
                        "Type": prop_value.get_data_type()
                    }
                    user_props_list.append(property_value_dict)
                if user_props_list:
                    item["UserProperties"] = {"PropertyValue": user_props_list}
            
            # 添加系统属性序列化
            if hasattr(msg, 'system_properties') and msg.system_properties:
                sys_props_list = []
                for name, prop_value in msg.system_properties.items():
                    system_property_value_dict = {
                        "Name": name,
                        "Value": prop_value.get_string_value_by_type(),
                        "Type": prop_value.get_data_type()
                    }
                    sys_props_list.append(system_property_value_dict)
                if sys_props_list:
                    item["SystemProperties"] = {"SystemPropertyValue": sys_props_list}

            msglist.append(item)
        return EncoderBase.listofdic_to_xml(u"Messages", u"Message", msglist)

class TopicMessageEncoder:
    @staticmethod
    def encode(req):
        message = {}
        #xml only support unicode when contains Chinese
        msgbody = req.message_body
        EncoderBase.insert_if_valid("MessageBody", msgbody, "", message)
        EncoderBase.insert_if_valid("MessageTag", req.message_tag, "", message)
        EncoderBase.insert_if_valid("MessageGroupId", req.message_group_id, "", message)
        msg_attr = {}
        if req.direct_mail is not None:
            msg_attr["DirectMail"] = json.dumps(req.direct_mail.get())
        if req.direct_sms is not None:
            msg_attr["DirectSMS"] = json.dumps(req.direct_sms.get())
        if msg_attr != {}:
            message["MessageAttributes"] = msg_attr

        # 添加用户自定义属性序列化
        if hasattr(req, 'user_properties') and req.user_properties:
            user_props_list = []
            for name, prop_value in req.user_properties.items():
                # 根据类型决定如何获取值
                if prop_value.get_data_type() == PropertyType.BINARY:
                    # 二进制类型：进行 base64 编码
                    encoded_value = base64.b64encode(prop_value.get_binary_value()).decode('ascii')
                else:
                    # 其他类型：直接获取字符串值
                    encoded_value = prop_value.get_string_value_by_type()
                property_value_dict = {
                    "Name": name,
                    "Value": encoded_value,
                    "Type": prop_value.get_data_type()
                }
                user_props_list.append(property_value_dict)
            if user_props_list:
                message["UserProperties"] = {"PropertyValue": user_props_list}
        
        # 添加系统属性序列化
        if hasattr(req, 'system_properties') and req.system_properties:
            sys_props_list = []
            for name, prop_value in req.system_properties.items():
                system_property_value_dict = {
                    "Name": name,
                    "Value": prop_value.get_string_value_by_type(),
                    "Type": prop_value.get_data_type()
                }
                sys_props_list.append(system_property_value_dict)
            if sys_props_list:
                message["SystemProperties"] = {"SystemPropertyValue": sys_props_list}
        
        return EncoderBase.dic_to_xml("Message", message)

class ReceiptHandlesEncoder:
    @staticmethod
    def encode(receipt_handle_list):
        return EncoderBase.list_to_xml("ReceiptHandles", "ReceiptHandle", receipt_handle_list)

class TopicEncoder(EncoderBase):
    @staticmethod
    def encode(data):
        topic = {}
        logging_enabled = str(data.logging_enabled)
        if str(data.logging_enabled).lower() == "true":
            logging_enabled = "True"
        elif str(data.logging_enabled).lower() == "false":
            logging_enabled = "False"
        EncoderBase.insert_if_valid("MaximumMessageSize", str(data.maximum_message_size), "-1", topic)
        EncoderBase.insert_if_valid("LoggingEnabled", logging_enabled, "None", topic)
        return EncoderBase.dic_to_xml("Topic", topic)

class SubscriptionEncoder(EncoderBase):
    @staticmethod
    def encode(data, set=False):
        subscription = {}
        EncoderBase.insert_if_valid("NotifyStrategy", data.notify_strategy, "", subscription)
        if not set:
            EncoderBase.insert_if_valid("Endpoint", data.endpoint, "", subscription)
            EncoderBase.insert_if_valid("FilterTag", data.filter_tag, "", subscription)
            EncoderBase.insert_if_valid("NotifyContentFormat", data.notify_content_format, "", subscription)
        return EncoderBase.dic_to_xml("Subscription", subscription)

#-------------------------------------------------decode-----------------------------------------------------#
class DecoderBase:
    @staticmethod
    def xml_to_nodes(tag_name, xml_data):
        if xml_data == "":
            raise MNSClientNetworkException("RespDataDamaged", "Xml data is \"\"!")

        try:
            if (sys.version_info.major < 3) and (not isinstance(xml_data, str)):
                xml_data = xml_data.encode('utf-8')
            dom = xml.dom.minidom.parseString(xml_data)
        except Exception:
            raise MNSClientNetworkException("RespDataDamaged", xml_data)

        nodelist = dom.getElementsByTagName(tag_name)
        if not nodelist:
            raise MNSClientNetworkException("RespDataDamaged", "No element with tag name '%s'.\nData:%s" % (tag_name, xml_data))

        return nodelist[0].childNodes

    @staticmethod
    def xml_to_dic(tag_name, xml_data, data_dic, req_id=None):
        try:
            for node in DecoderBase.xml_to_nodes(tag_name, xml_data):
                if node.nodeName != "#text":
                    # 检查是否是属性相关的嵌套结构
                    if node.nodeName in ["UserProperties", "SystemProperties"]:
                        DecoderBase._parse_properties_node(node, data_dic)
                    elif node.childNodes != []:
                        data_dic[node.nodeName] = node.firstChild.data
                    else:
                        data_dic[node.nodeName] = ""
        except MNSClientNetworkException as e:
            raise MNSClientNetworkException(e.type, e.message, req_id)

    @staticmethod
    def xml_to_listofdic(root_tagname, sec_tagname, xml_data, data_listofdic, req_id=None):
        try:
            for message in DecoderBase.xml_to_nodes(root_tagname, xml_data):
                if message.nodeName != sec_tagname:
                    continue

                data_dic = {}
                for property in message.childNodes:
                    if property.nodeName in ["UserProperties", "SystemProperties"]:
                        DecoderBase._parse_properties_node(property, data_dic)
                    elif property.nodeName != "#text" and property.childNodes != []:
                        data_dic[property.nodeName] = property.firstChild.data
                data_listofdic.append(data_dic)
        except MNSClientNetworkException as e:
            raise MNSClientNetworkException(e.type, e.message, req_id)
    
    @staticmethod
    def _parse_properties_node(properties_node, data_dic):
        """
        解析属性节点（UserProperties 或 SystemProperties）
        """
        try:
            properties_type = properties_node.nodeName
            properties_data = {}
            
            if properties_type == "UserProperties":
                property_values = []
                for child_node in properties_node.childNodes:
                    if child_node.nodeName == "PropertyValue":
                        prop_data = {}
                        for prop_child in child_node.childNodes:
                            if prop_child.nodeName != "#text" and prop_child.childNodes:
                                prop_data[prop_child.nodeName] = prop_child.firstChild.data
                        if prop_data:
                            property_values.append(prop_data)
                
                if property_values:
                    properties_data["PropertyValue"] = property_values
            
            elif properties_type == "SystemProperties":
                property_values = []
                for child_node in properties_node.childNodes:
                    if child_node.nodeName == "SystemPropertyValue":
                        prop_data = {}
                        for prop_child in child_node.childNodes:
                            if prop_child.nodeName != "#text" and prop_child.childNodes:
                                prop_data[prop_child.nodeName] = prop_child.firstChild.data
                        if prop_data:
                            property_values.append(prop_data)
                
                if property_values:
                    properties_data["SystemPropertyValue"] = property_values
            
            if properties_data:
                data_dic[properties_type] = properties_data
                
        except Exception:
            # 属性解析失败不影响主要消息解析
            pass
    @staticmethod
    def parse_properties_from_dict(data_dic, properties_type):
        """
        通用方法：从解析后的字典中提取属性
        
        @param data_dic: 解析后的消息字典
        @param properties_type: 属性类型，"UserProperties" 或 "SystemProperties"
        @return: 属性字典，key为属性名，value为属性值对象
        """
        props = {}
        
        if properties_type not in data_dic:
            return props
        
        properties_dict = data_dic[properties_type]
        
        # 确定属性值的键名和对应的类
        if properties_type == "UserProperties":
            value_key = "PropertyValue"
            property_class = MessagePropertyValue
        elif properties_type == "SystemProperties":
            value_key = "SystemPropertyValue"
            property_class = MessageSystemPropertyValue
        else:
            return props
        
        # 处理属性值列表
        if value_key in properties_dict:
            property_values = properties_dict[value_key]
            
            # 确保是列表格式
            if not isinstance(property_values, list):
                property_values = [property_values]
            
            for prop_data in property_values:
                if isinstance(prop_data, dict):
                    name = prop_data.get("Name")
                    value = prop_data.get("Value")
                    prop_type = prop_data.get("Type")
                    
                    if name and value is not None and prop_type:
                        try:
                            # 用户属性的二进制类型需要特殊处理
                            if (properties_type == "UserProperties" and 
                                prop_type == PropertyType.BINARY):
                                try:
                                    binary_data = base64.b64decode(value)
                                    prop_value = property_class(PropertyType.BINARY, binary_data)
                                except Exception:
                                    raise MNSClientException("InvalidBinaryData", "Failed to decode binary data for property '%s'." % name)
                            else:
                                prop_value = property_class(prop_type, value)
                            props[name] = prop_value
                        except Exception:
                            raise MNSClientException("InvalidPropertyValue", "Failed to create property value for '%s' with type '%s'." % (name, prop_type))
        
        return props
    
    @staticmethod
    def parse_user_properties_from_dict(data_dic):
        """从解析后的字典中提取用户自定义属性"""
        return DecoderBase.parse_properties_from_dict(data_dic, "UserProperties")
    
    @staticmethod
    def parse_system_properties_from_dict(data_dic):
        """从解析后的字典中提取系统属性"""
        return DecoderBase.parse_properties_from_dict(data_dic, "SystemProperties")


class ListQueueDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, with_meta, req_id=None):
        queueurl_list = []
        queuemeta_list = []
        next_marker = u""
        if (xml_data != ""):
            try:
                root = ElementTree.fromstring(xml_data)
                namespace = root.tag[0:-6]
                queues = list(root.iter(namespace + "Queue"))
                for queue in queues:
                    queuemeta = {}
                    for node in queue:
                        nodename = node.tag[len(namespace):]
                        nodevalue = node.text.strip()
                        if nodename == "QueueURL" and len(nodevalue) > 0 :
                            queueurl_list.append(nodevalue)
                        if len(nodevalue) > 0:
                            queuemeta[nodename] = nodevalue
                    if with_meta:
                        queuemeta_list.append(queuemeta)

                marker = list(root.iter(namespace + "NextMarker"))
                for node in marker:
                    next_marker = node.text.strip()
            except Exception as err:
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        else:
            raise MNSClientNetworkException("RespDataDamaged", "Xml data is \"\"!", req_id)
        return queueurl_list, str(next_marker), queuemeta_list

class GetAccountAttrDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Account", xml_data, data_dic)
        key_list = ["LoggingBucket"]
        for key in key_list:
            if key not in data_dic:
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic

class GetQueueAttrDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Queue", xml_data, data_dic, req_id)
        key_list = ["ActiveMessages", "CreateTime", "DelayMessages", "DelaySeconds", "InactiveMessages", "LastModifyTime", "MaximumMessageSize", "MessageRetentionPeriod", "QueueName", "VisibilityTimeout", "PollingWaitSeconds", "LoggingEnabled"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic

class SendMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic, req_id)
        key_list = ["MessageId", "MessageBodyMD5"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)

        receipt_handle = ""
        if "ReceiptHandle" in data_dic.keys():
            receipt_handle = data_dic["ReceiptHandle"]
        
        message_group_id = ""
        if "MessageGroupId" in data_dic.keys():
            message_group_id = data_dic["MessageGroupId"]

        return data_dic["MessageId"], data_dic["MessageBodyMD5"], receipt_handle, message_group_id

class BatchSendMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_listofdic = []
        message_list = []
        DecoderBase.xml_to_listofdic("Messages", "Message", xml_data, data_listofdic, req_id)
        try:
            for data_dic in data_listofdic:
                entry = SendMessageResponseEntry()
                entry.message_id = data_dic["MessageId"]
                entry.message_body_md5 = data_dic["MessageBodyMD5"]
                entry.message_group_id = data_dic.get("MessageGroupId", "")
                message_list.append(entry)
        except Exception as err:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return message_list

    @staticmethod
    def decodeError(xml_data, req_id=None):
        try:
            return ErrorDecoder.decodeError(xml_data, req_id)
        except Exception:
            pass

        data_listofdic = []
        DecoderBase.xml_to_listofdic("Messages", "Message", xml_data, data_listofdic, req_id)
        if len(data_listofdic) == 0:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)

        errType = None
        errMsg = None
        key_list1 = sorted(["ErrorCode", "ErrorMessage"])
        key_list2 = sorted(["MessageId", "MessageBodyMD5"])
        for data_dic in data_listofdic:
            keys = sorted(data_dic.keys())
            if keys != key_list1 and keys != key_list2:
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
            if keys == key_list1 and errType is None:
                errType = data_dic["ErrorCode"]
                errMsg = data_dic["ErrorMessage"]
        return errType, errMsg, None, None, data_listofdic

class RecvMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, base64decode, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic, req_id)
        key_list = ["DequeueCount", "EnqueueTime", "FirstDequeueTime", "MessageBody", "MessageId", "MessageBodyMD5", "NextVisibleTime", "ReceiptHandle", "Priority"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)

        if base64decode:
            decode_str = base64.b64decode(data_dic["MessageBody"])
            data_dic["MessageBody"] = decode_str
        
        user_properties = DecoderBase.parse_user_properties_from_dict(data_dic)
        system_properties = DecoderBase.parse_system_properties_from_dict(data_dic)

        if user_properties:
            data_dic["UserProperties"] = user_properties
        if system_properties:
            data_dic["SystemProperties"] = system_properties

        return data_dic

class BatchRecvMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, base64decode, req_id=None):
        data_listofdic = []
        message_list = []
        DecoderBase.xml_to_listofdic("Messages", "Message", xml_data, data_listofdic, req_id)
        try:
            for data_dic in data_listofdic:
                msg = ReceiveMessageResponseEntry()
                if base64decode:
                    msg.message_body = base64.b64decode(data_dic["MessageBody"])
                else:
                    msg.message_body = data_dic["MessageBody"]
                msg.dequeue_count = int(data_dic["DequeueCount"])
                msg.enqueue_time = int(data_dic["EnqueueTime"])
                msg.first_dequeue_time = int(data_dic["FirstDequeueTime"])
                msg.message_id = data_dic["MessageId"]
                msg.message_body_md5 = data_dic["MessageBodyMD5"]
                msg.priority = int(data_dic["Priority"])
                msg.next_visible_time = int(data_dic["NextVisibleTime"])
                msg.receipt_handle = data_dic["ReceiptHandle"]
                msg.message_group_id = data_dic.get("MessageGroupId", "")
                msg.user_properties = DecoderBase.parse_user_properties_from_dict(data_dic)
                msg.system_properties = DecoderBase.parse_system_properties_from_dict(data_dic)

                message_list.append(msg)
        except Exception as err:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return message_list

class PeekMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, base64decode, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic, req_id)
        key_list = ["DequeueCount", "EnqueueTime", "FirstDequeueTime", "MessageBody", "MessageId", "MessageBodyMD5", "Priority"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        if base64decode:
            decode_str = base64.b64decode(data_dic["MessageBody"])
            data_dic["MessageBody"] = decode_str
        
        user_properties = DecoderBase.parse_user_properties_from_dict(data_dic)
        system_properties = DecoderBase.parse_system_properties_from_dict(data_dic)
        
        if user_properties:
            data_dic["UserProperties"] = user_properties
        if system_properties:
            data_dic["SystemProperties"] = system_properties
        return data_dic

class BatchPeekMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, base64decode, req_id=None):
        data_listofdic = []
        message_list = []
        DecoderBase.xml_to_listofdic("Messages", "Message", xml_data, data_listofdic, req_id)
        try:
            for data_dic in data_listofdic:
                msg = PeekMessageResponseEntry()
                if base64decode:
                    msg.message_body = base64.b64decode(data_dic["MessageBody"])
                else:
                    msg.message_body = data_dic["MessageBody"]
                msg.dequeue_count = int(data_dic["DequeueCount"])
                msg.enqueue_time = int(data_dic["EnqueueTime"])
                msg.first_dequeue_time = int(data_dic["FirstDequeueTime"])
                msg.message_id = data_dic["MessageId"]
                msg.message_body_md5 = data_dic["MessageBodyMD5"]
                msg.priority = int(data_dic["Priority"])
                msg.user_properties = DecoderBase.parse_user_properties_from_dict(data_dic)
                msg.system_properties = DecoderBase.parse_system_properties_from_dict(data_dic)
                message_list.append(msg)
        except Exception as err:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return message_list

class BatchDeleteMessageDecoder(DecoderBase):
    @staticmethod
    def decodeError(xml_data, req_id=None):
        try:
            return ErrorDecoder.decodeError(xml_data, req_id)
        except Exception:
            pass

        data_listofdic = []
        DecoderBase.xml_to_listofdic("Errors", "Error", xml_data, data_listofdic, req_id)
        if len(data_listofdic) == 0:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)

        key_list = sorted(["ErrorCode", "ErrorMessage", "ReceiptHandle"])
        for data_dic in data_listofdic:
            for key in key_list:
                keys = sorted(data_dic.keys())
                if keys != key_list:
                    raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_listofdic[0]["ErrorCode"], data_listofdic[0]["ErrorMessage"], None, None, data_listofdic

class ChangeMsgVisDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("ChangeVisibility", xml_data, data_dic, req_id)

        if "ReceiptHandle" in data_dic.keys() and "NextVisibleTime" in data_dic.keys():
            return data_dic["ReceiptHandle"], data_dic["NextVisibleTime"]
        else:
            raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)

class ListTopicDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, with_meta, req_id=None):
        topicurl_list = []
        topicmeta_list = []
        next_marker = ""
        if (xml_data != ""):
            try:
                root = ElementTree.fromstring(xml_data)
                namespace = root.tag[0:-6]
                topics = list(root.iter(namespace + "Topic"))
                for topic in topics:
                    topicMeta = {}
                    for node in topic:
                        nodeName = node.tag[len(namespace):]
                        nodeValue = node.text.strip()
                        if nodeName == "TopicURL" and len(nodeValue) > 0:
                            topicurl_list.append(nodeValue)
                        if len(nodeValue) > 0:
                            topicMeta[nodeName] = nodeValue
                    if with_meta:
                        topicmeta_list.append(topicMeta)

                marker = list(root.iter(namespace + "NextMarker"))
                for node in marker:
                    next_marker = node.text.strip()
            except Exception as err:
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        else:
            raise MNSClientNetworkException("RespDataDamaged", "Xml data is \"\"!", req_id)
        return topicurl_list, str(next_marker), topicmeta_list

class GetTopicAttrDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Topic", xml_data, data_dic, req_id)
        key_list = ["MessageCount", "CreateTime", "LastModifyTime", "MaximumMessageSize", "MessageRetentionPeriod", "TopicName", "LoggingEnabled"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic

class PublishMessageDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic, req_id)
        key_list = ["MessageId", "MessageBodyMD5"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic["MessageId"], data_dic["MessageBodyMD5"], data_dic.get("MessageGroupId", "")

class ListSubscriptionByTopicDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        subscriptionurl_list = []
        next_marker = ""
        if (xml_data != ""):
            try:
                root = ElementTree.fromstring(xml_data)
                namespace = root.tag[0:-13]
                subscriptions = list(root.iter(namespace + "Subscription"))
                for subscription in subscriptions:
                    for node in subscription:
                        nodeName = node.tag[len(namespace):]
                        nodeValue = node.text.strip()
                        if nodeName == "SubscriptionURL" and len(nodeValue) > 0:
                            subscriptionurl_list.append(nodeValue)
                marker = list(root.iter(namespace + "NextMarker"))
                for node in marker:
                    next_marker = node.text.strip()
            except Exception:
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        else:
            raise MNSClientNetworkException("RespDataDamaged", "Xml data is \"\"!", req_id)
        return subscriptionurl_list, str(next_marker)

class GetSubscriptionAttrDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Subscription", xml_data, data_dic, req_id)
        key_list = ["TopicOwner", "TopicName", "SubscriptionName", "Endpoint", "NotifyStrategy", "NotifyContentFormat", "CreateTime", "LastModifyTime"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic

class ErrorDecoder(DecoderBase):
    @staticmethod
    def decodeError(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("Error", xml_data, data_dic, req_id)
        key_list = ["Code", "Message", "RequestId", "HostId"]
        for key in key_list:
            if key not in data_dic.keys():
                raise MNSClientNetworkException("RespDataDamaged", xml_data, req_id)
        return data_dic["Code"], data_dic["Message"], data_dic["RequestId"], data_dic["HostId"], None

class OpenServiceDecoder(DecoderBase):
    @staticmethod
    def decode(xml_data, req_id=None):
        data_dic = {}
        DecoderBase.xml_to_dic("OpenService", xml_data, data_dic, req_id)
        return data_dic
