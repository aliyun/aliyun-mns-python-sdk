#!/usr/bin/env python
# coding=utf8
# Copyright (C) 2015, Alibaba Cloud Computing

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

import threading
from sample_config import MNSSampleConfig
from mns.account import Account
from mns.queue import *

accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()


class SendThread(threading.Thread):
    def __init__(self, name, queue_name, msg_count):
        super(SendThread, self).__init__(name=name)
        self.queue_name = queue_name
        self.msg_count = msg_count
        # 在多线程场景下，每个线程需要独立构建Account对象
        self.account = Account(endpoint, accessKeyId, accessKeySecret, token)
        self.queue = self.account.get_queue(queue_name)

    def run(self):
        print("%sSend Message To Queue%s\nQueueName: %s\nMessageCount: %s\nThreadName: %s"
              % (10 * "=", 10 * "=", self.queue_name, self.msg_count, self.name))
        for j in range(self.msg_count):
            try:
                msg_body = u"I am test message %s-%s." % (self.name, j)
                msg = Message(msg_body)
                re_msg = self.queue.send_message(msg)
                print("Send Message Succeed! MessageBody: %s MessageID: %s"
                      % (msg_body, re_msg.message_id))
            except MNSExceptionBase as e:
                if e.type == "QueueNotExist":
                    print("Queue not exist, please create queue before send message.")
                    sys.exit(0)
                print("Send Message Fail! Exception:%s\n" % e)


class RecvThread(threading.Thread):
    def __init__(self, name, queue_name, wait_seconds):
        super(RecvThread, self).__init__(name=name)
        self.queue_name = queue_name
        self.wait_seconds = wait_seconds
        # 在多线程场景下，每个线程需要独立构建Account对象
        self.account = Account(endpoint, accessKeyId, accessKeySecret, token)
        self.queue = self.account.get_queue(queue_name)

    def run(self):
        no_message_count = 0
        print("%sReceive And Delete Message From Queue%s\nQueueName: %s\nWaitSeconds: %s\n"
              % (10 * "=", 10 * "=", self.queue_name, self.wait_seconds))
        while True:
            if no_message_count > 50:
                print("Long time without receiving messages, exiting.")
                sys.exit(0)

            # 读取消息
            try:
                # receive_message 返回字节串，receive_message_with_str_body 返回字符串
                # recv_msg = my_queue.receive_message(wait_seconds)
                recv_msg = self.queue.receive_message_with_str_body(self.wait_seconds)
                print("Receive Message Succeed! ReceiptHandle: %s MessageBody: %s MessageID: %s"
                      % (recv_msg.receipt_handle, recv_msg.message_body, recv_msg.message_id))
            except Exception as e:
                if hasattr(e, 'type'):
                    if e.type == u"QueueNotExist":
                        print("Queue not exist, please create queue before receive message.")
                        sys.exit(0)
                    elif e.type == u"MessageNotExist":
                        print("Queue is empty!")
                        no_message_count += 1
                        continue
                print("Receive Message Fail! Exception: %s\n" % e)
                continue

            # 删除消息
            try:
                self.queue.delete_message(recv_msg.receipt_handle)
                print("Delete Message Succeed!  ReceiptHandle: %s" % recv_msg.receipt_handle)
            except Exception as e:
                print("Delete Message Fail! Exception: %s\n" % e)


if __name__ == "__main__":
    thread_count = 3
    queue_name = sys.argv[1] if len(sys.argv) > 1 else "MySampleQueue"
    send_threads = []
    for i in range(thread_count):
        send_thread = SendThread("SendThread{}".format(i), queue_name, 600)
        send_thread.start()
        send_threads.append(send_thread)
        recv_thread = RecvThread("RecvThread{}".format(i), queue_name, 0)
        recv_thread.start()

    for send_thread in send_threads:
        send_thread.join()

    print("All threads finished.")
