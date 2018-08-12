#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-24 15:13:31
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
#创建SocketServerTCP服务器：
import os,sys
import analyseManger
sys.path.append('util')
import apikeytool
import time
import json
    

def reconfig():
    f = open('tradeconfig.json','r')
    tmpstr = f.read()
    f.close()
    configdic = json.loads(tmpstr)
    return configdic

def main():
    global tradetool

    configdic = reconfig()

    tradetool = analyseManger.TradeTool(apikeytool.apikeydic,configdic)

    delaycount = configdic['reconfigTime']
    while True:
        
        time.sleep(10)
        tradetool.pingAllServer()
        
        delaycount -= 10
        if delaycount <= 0:
            configdic = reconfig()
            delaycount = configdic['reconfigTime']
            tradetool.initTraddeConfig(configdic)


#测试
if __name__ == '__main__':
    main()
    
    
