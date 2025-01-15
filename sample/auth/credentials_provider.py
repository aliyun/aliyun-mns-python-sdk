#!/usr/bin/env python
# coding=utf8

from sample_config import MNSSampleConfig
from mns.account import Account
from mns.queue import *
from mns.auth import StaticCredentialsProvider

# get a credential provider object, 以StaticCredentialsProvider为例
credentials_provider = StaticCredentialsProvider("ak", "sk", "token")

# 1. config credentials_provider for Account
my_account = Account("endpoint", credentials_provider=credentials_provider)

# 2. config credentials_provider for MNSClient
my_account = MNSClient("endpoint", credentials_provider=credentials_provider)

# We have got the way to set up credentials provider for various client
# Now I'll show you how to get credentials providers
# pip3 install alibabacloud_credentials
# And you will get the following implemented credentials providers:
# 1. EcsRamRoleCredentialProvider
# 2. RamRoleArnCredentialProvider
# 3. OIDCRoleArnCredentialProvider
# 4. EnvironmentVariableCredentialsProvider
# 5. ......
