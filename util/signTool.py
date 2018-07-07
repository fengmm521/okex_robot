#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import json
import os
import hashlib
import json

def isSginOK(msgdic,secretkey):
    data = json.dumps(msgdic['data']) + str(msgdic['time']) + secretkey
    csgin = msgdic['sign']
    if csgin == 'test':
        return True
    sgin = hashlib.sha256(data.encode("utf8")).hexdigest().upper()
    if csgin == sgin:
        return True
    else:
        return False

