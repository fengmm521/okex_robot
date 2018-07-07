#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import json

f = open('../../btc/okexapikey/okexapikey.txt','r')
tmpstr = f.read()
f.close()

apikeydic = json.loads(tmpstr)

#初始化apikey，secretkey,url
apikey = apikeydic['apikey']
secretkey = apikeydic['secretkey']
