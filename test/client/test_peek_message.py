#!/usr/bin/env python
# coding=utf-8
import unittest

from mns.mns_client import MNSClient
from mns.mns_xml_handler import *

RAW_XML_DATA = u"""<?xml version="1.0" ?>
                <Message xmlns="http://mns.aliyuncs.com/doc/v1">
                  <MessageId>0909FF0D9C3A630C372B8A14BD2011B6</MessageId>
                  <MessageBodyMD5>9D75198CAA17528AB23790C1861987AF</MessageBodyMD5>
                  <MessageBody>I am 测试字符串.</MessageBody>
                  <ReceiptHandle>8-0zxjHBaWtzPz8zphz0z6OGz5yWWidU1fJM</ReceiptHandle>
                  <EnqueueTime>1716809414944</EnqueueTime>
                  <FirstDequeueTime>1716809420986</FirstDequeueTime>
                  <NextVisibleTime>1716809470986</NextVisibleTime>
                  <DequeueCount>1</DequeueCount>
                  <Priority>10</Priority>
                </Message>
                """
BASE64_XML_DATA = u"""<?xml version="1.0" ?>
                    <Message xmlns="http://mns.aliyuncs.com/doc/v1">
                      <MessageId>0909AC939C3A61357F898A13F0DBEB97</MessageId>
                      <MessageBodyMD5>A9B134C465C384F49EB89A6E3870D996</MessageBodyMD5>
                      <MessageBody>SSBhbSDmtYvor5XlrZfnrKbkuLIu</MessageBody>
                      <ReceiptHandle>8-0zxjHAX72zPzaztyz0z6GXzcSROgZnrPNl</ReceiptHandle>
                      <EnqueueTime>1716809362651</EnqueueTime>
                      <FirstDequeueTime>1716809369536</FirstDequeueTime>
                      <NextVisibleTime>1716809419536</NextVisibleTime>
                      <DequeueCount>1</DequeueCount>
                      <Priority>10</Priority>
                    </Message>
                    """

access_id = "access_id"
access_key = "access_key"
host = "http://accoundId.mns.region.aliyuncs.com"

class PeekMessageTest(unittest.TestCase):

    def test_peek_base64_message_not_decode(self):
        # 构建 request, 模拟 不进行base64解码 时, peek_message 对于 经过base64编码的消息体 的 decode()结果
        message_body = u"I am 测试字符串."
        queue_name = "test_queue"
        req = PeekMessageRequest(queue_name, False)
        resp = PeekMessageResponse()
        data = PeekMessageDecoder.decode(BASE64_XML_DATA, req.base64decode)
        MNSClient.make_peekresp(MNSClient(host, access_id, access_key), data, resp)
        # 不进行 base64解码时，peek_message 的 decode() 结果为 原base64编码字符串
        self.assertEqual(base64.b64encode(message_body.encode("utf-8")).decode("utf-8"), resp.message_body)

    def test_peek_base64_message_decode(self):
        # 构建 request, 模拟 进行base64解码 时, peek_message 对于 经过base64编码的消息体 的 decode()结果
        message_body = u"I am 测试字符串."
        queue_name = "test_queue"
        req = PeekMessageRequest(queue_name, True)
        resp = PeekMessageResponse()
        data = PeekMessageDecoder.decode(BASE64_XML_DATA, req.base64decode)
        MNSClient.make_peekresp(MNSClient(host, access_id, access_key), data, resp)
        # 进行 base64解码时，peek_message 的 decode() 结果为 base64解码后的字节串
        self.assertEqual(message_body.encode('utf-8'), resp.message_body)

    def test_peek_raw_message_not_decode(self):
        # 构建 request, 模拟 不进行base64解码 时，peek_message 对于 原始消息体 的 decode()结果
        message_body = u"I am 测试字符串."
        queue_name = "test_queue"
        req = PeekMessageRequest(queue_name, False)
        resp = PeekMessageResponse()
        data = PeekMessageDecoder.decode(RAW_XML_DATA, req.base64decode)
        MNSClient.make_peekresp(MNSClient(host, access_id, access_key), data, resp)
        # 不进行 base64解码时，peek_message 的 decode() 结果为 原始字符串
        self.assertEqual(message_body, resp.message_body)

    def test_peek_raw_message_decode(self):
        # 构建 request, 模拟 进行base64解码 时，peek_message 对于 原始消息体 的 decode()结果
        # 当 原字符串 中含有非 ascii 字符时, 发生 ValueError
        # 当 原字符串 不满足 base64 的填充时, 发生 binascii.Error, 其是 ValueError 的子类
        with self.assertRaises(ValueError):
            message_body = u"I am 测试字符串."
            queue_name = "test_queue"
            req = PeekMessageRequest(queue_name, True)
            resp = PeekMessageResponse()
            # 解码时会发生错误
            data = PeekMessageDecoder.decode(RAW_XML_DATA, req.base64decode)
            MNSClient.make_peekresp(MNSClient(host, access_id, access_key), data, resp)
            # 不进行 base64解码时，peek_message 的 decode() 结果为 原始字符串
            self.assertEqual(message_body, resp.message_body)


if __name__ == '__main__':
    unittest.main()
