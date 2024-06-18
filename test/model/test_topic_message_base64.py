# coding=utf-8
import base64
import unittest

from mns.topic import TopicMessage, Base64TopicMessage


class TestTopicMessageBase64(unittest.TestCase):

    def test_message(self):
        message_body = u"test 字符串"
        topic_message = TopicMessage(message_body)
        base64_message = Base64TopicMessage(message_body)
        # 验证消息体是否正确设置, 消息体为 原值
        self.assertEqual(message_body, topic_message.message_body)
        # 验证消息体是否正确获取
        self.assertEqual(message_body, topic_message.get_messagebody())
        # 验证消息体是否正确设置, 消息体为 base64编码后 的字符串
        self.assertEqual(base64.b64encode(message_body.encode("utf-8")).decode("utf-8"), base64_message.message_body)
        # 验证消息体是否正确获取
        self.assertEqual(message_body, base64_message.get_messagebody())


if __name__ == '__main__':
    unittest.main()