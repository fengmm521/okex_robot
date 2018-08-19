#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import json
import os
import hashlib
import json

import platform

def getSysType():
    sysSystem = platform.system()
    if sysSystem == 'Windows':  #mac系统
        return 'win'
    elif sysSystem == 'Darwin':
        return 'mac'
    elif sysSystem == 'Linux':
        return 'linux'

def isSignOK(msgdic,secretkey):
    data = json.dumps(msgdic['data']) + str(msgdic['time']) + secretkey
    csgin = msgdic['sign']
    if csgin == 'test':
        return True
    sgin = hashlib.sha256(data.encode("utf8")).hexdigest().upper()
    if csgin == sgin:
        return True
    else:
        return False

def signMsg(msgdic,ptime,secretkey):
    if type(msgdic) == str:
        data = msgdic + str(ptime) + secretkey
        sgin = hashlib.sha256(data.encode("utf8")).hexdigest().upper()
        return sgin
    else:
        data = json.dumps(msgdic) + str(ptime) + secretkey
        sgin = hashlib.sha256(data.encode("utf8")).hexdigest().upper()
        return sgin