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
    
#     {
#     "iOkexRate":0.0005,     //okex主动成交费率
#     "pOkexRate":0.0002,     //okex被动成交费率
#     "iBiemexRate":0.00075,  //bitmex主动成交费率
#     "pBiemexRate":-0.00025,  //bitmex被动成交费率
#     "stepPercent":4,        //下单网格价格是全主动成交手续费的倍数
#     "movePercent":0.6,      //网格滑动价格在网络价格的比例
#     "normTime":3,           //基准价格重新计算时间,单位:小时
#     "reconfigTime":60,       //配置文件检测刷新时间，单位:秒
#     "baseAmount":1           //单次下单量
# }

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
    
    
