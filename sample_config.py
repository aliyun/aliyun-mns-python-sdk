#!/usr/bin/env python
# coding=utf8
# Copyright (C) 2015, Alibaba Cloud Computing

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os
import sys

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser as ConfigParser


class MNSSampleConfig:

    @staticmethod
    def load_config():
        cfg_fn = os.path.join(os.path.dirname(os.path.abspath(__file__)) + "/sample.cfg")
        required_ops = [("Base", "Endpoint")]
        parser = ConfigParser.ConfigParser()
        parser.read(cfg_fn)
        for sec, op in required_ops:
            if not parser.has_option(sec, op):
                sys.stderr.write("ERROR: need (%s, %s) in %s.\n" % (sec, op, cfg_fn))
                sys.stderr.write("Read README to get help information.\n")
                sys.exit(1)

        access_key_id = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_ID")
        access_key_secret = os.getenv("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        security_token = os.getenv("ALIBABA_CLOUD_ACCESS_SECURITY_TOKEN") or ""
        endpoint = parser.get("Base", "Endpoint")
        return access_key_id, access_key_secret, endpoint, security_token
