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

# 创建队列, 具体属性请参考mns/queue.py中的QueueMeta结构
queue_meta = QueueMeta()
try:
    queue_url = my_queue.create(queue_meta)
    print("Create Queue Succeed! QueueName: %s\n" % queue_name)
except MNSExceptionBase as e:
    if e.type == "QueueAlreadyExist":
        print("Queue already exist, please delete it before creating or use it directly.")
        sys.exit(0)
    print("Create Queue Fail! Exception: %s\n" % e)
