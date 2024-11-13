#!/usr/bin/env python
# coding=utf8

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from sample_config import MNSSampleConfig
from mns.account import Account
from mns.queue import *

# 从sample.cfg中读取基本配置信息
# WARNING： Please do not hard code your accessId and accesskey in next line.(more information: https://yq.aliyun.com/articles/55947)
accessKeyId, accessKeySecret, endpoint, token = MNSSampleConfig.load_config()

# 初始化 my_account, my_queue
my_account = Account(endpoint, accessKeyId, accessKeySecret, token)
queue_name = sys.argv[1] if len(sys.argv) > 1 else "MySampleQueue"
my_queue = my_account.get_queue(queue_name)

queue_meta = QueueMeta()
queue_meta.set_maximum_message_size(1024 * 30)
queue_meta.set_visibilitytimeout(30)
queue_meta.set_message_retention_period(60 * 30)
queue_meta.set_delay_seconds(10)
queue_meta.set_polling_wait_seconds(10)
try:
    my_queue.set_attributes(queue_meta)
    print("Set Attributes Succeed! QueueName: %s\n" % queue_name)
except MNSExceptionBase as e:
    if e.type == "QueueNotExist":
        print("Queue not exist, please create queue before send message.")
        sys.exit(0)
    print("Set Attributes Fail! Exception: %s\n" % e)

