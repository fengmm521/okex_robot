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
    


def main():
    global tradetool
    tradetool = analyseManger.TradeTool(apikeytool.apikeydic)

    while True:
        time.sleep(10)
        tradetool.pingAllServer()
        pass

#测试
if __name__ == '__main__':
    main()
    
    
