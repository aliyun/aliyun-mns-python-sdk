import unittest

from mns.mns_xml_handler import *


class SendMessageTest(unittest.TestCase):

    def test_send_base64_message(self):
        # 构建 request, 模拟 进行base64编码 时, send_message 对于 消息体 的 encode()结果
        message_body = "I am 测试字符串."
        queue_name = "test_queue"
        req = SendMessageRequest(queue_name, message_body, base64encode=True)
        # 生成 发送请求的请求体
        xml_data = MessageEncoder.encode(req)
        # 解析 请求体, 转换为 字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        # 进行 base64编码时，send_message 的 encode() 结果为 base64编码后的字符串
        self.assertEqual(base64.b64encode(message_body.encode("utf-8")).decode("utf-8"), data_dic["MessageBody"])

    def test_send_raw_message(self):
        # 构建 request, 模拟 不进行base64编码 时, send_message 对于 消息体 的 encode()结果
        message_body = "I am 测试字符串."
        queue_name = "test_queue"
        req = SendMessageRequest(queue_name, message_body, base64encode=False)
        # 生成 发送请求的请求体
        xml_data = MessageEncoder.encode(req)
        # 解析 请求体, 转换为 字典
        data_dic = {}
        DecoderBase.xml_to_dic("Message", xml_data, data_dic)
        # 进行 base64编码时，send_message 的 encode() 结果为 原字符串
        self.assertEqual(message_body, data_dic["MessageBody"])


if __name__ == '__main__':
    unittest.main()
