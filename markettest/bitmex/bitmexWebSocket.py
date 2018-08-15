#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于访问OKCOIN 期货REST API

import websocket
import socket
import sys
import hmac
import hashlib

try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
from magetool import timetool
from future.builtins import bytes


class bitmexWSTool(object):
    """docstring for wsDataTool"""
    def __init__(self):
        super(bitmexWSTool, self).__init__()

        self.selltop = []
        self.buytop = []

        self.csocket = None


        self.lastPingTime = int(time.time())

        self.sendcount = 100   #每100次log提示一次没有客户端连接


        self.testDatas = []

        self.initTestDatas()

        self.sendIndex = 0

        #每一个周期里包括，开多，涨价，平多，价跌，开空，跌价，平空，涨价，8个价位测试，
        #涨价和跌价主要为了测试，价络改变后的自动取消和自动再下单操作
        self.sendZhouQI = 0  #测试下单周期，第一个周期正常成交，第二个周期发送定单被取消信号


        self.tradeBackDelay = 1 #下单确认返回延时

        #下单状态，ok:返回已完全成交,cancel:取消定单，市场价格下降，市场价格上涨
        self.tradeBackStates = ['ok','cancel','pdown','pup']



    def initTestDatas(self):
        f = open('deepdatatest.txt','r')
        lines = f.readlines()
        f.close()
        for l in lines:
            tmpl = l.replace('\n','')
            tmpd = json.loads(tmpl)
            tmpdata = {"table":"quote","action":"insert","data":[{"timestamp":"2018-08-15T14:57:10.278Z","symbol":"XBTUSD","bidSize":1591830,"bidPrice":tmpd['buy'],"askPrice":tmpd['sell'],"askSize":38682}]}
            self.testDatas.append(tmpdata)

    #接收来自测试下单服务器的消息
    def reciveMsgFromTestTradeServer(self,msgdic):
        print(msgdic)
        #{'type':下单类型,price:下单价格,amount:下单数量,cid:下单用户ID},下单类型分为:开多，开空，平多，平空，取消定单5种
        #所要测试的状态
        #1.完成成交，
        #2.定单取消
        #3,市价下跌
        #4,市价上涨

    #发送已完全成交消息给管理服务器
    def sendTradeOK(self):
        pass

    def sendDeepDataToClient(self):
        # {"table":"quote","action":"insert","data":[{"timestamp":"2018-08-15T14:57:10.278Z","symbol":"XBTUSD","bidSize":1591830,"bidPrice":6374,"askPrice":6374.5,"askSize":38682}]}
        dicdat = self.testDatas[self.sendIndex]
        self.sendIndex += 1
        msg = json.dumps(dicdat)
        self.sendMsgToClient(msg)
        self.updateTopDeep(msg)

    def updateTopDeep(self,datas):
        if len(datas) > 0:
            timeint,timestr = self.timeconvent(datas[-1]['timestamp'])
            self.selltop = [datas[-1]['askPrice'],datas[-1]['askSize'],timeint,timestr]
            self.buytop = [datas[-1]['bidPrice'],datas[-1]['bidSize'],timeint,timestr]
            print(self.buytop,self.selltop)
            self.savedatas.append([int(time.time()),self.buytop,self.selltop])
            if len(self.savedatas) >= 100:
                self.savedatas = []
        else:
            print('数据错误')

    def setSocketClient(self,clientsocket):
        self.csocket = clientsocket

    def reciveMsgFromClient(self,msgdic):
        print(msgdic)
        self.sendMsgToClient(str(msgdic))

    def sendMsgToClient(self,msg):
        def run(*args):
            try:
                if self.csocket:
                    self.csocket.send(msg.encode())
                else:
                    self.sendcount -= 1
                    if self.sendcount < 0:
                        self.sendcount = 100
                        print("没有客户端连接")
            except Exception as e:
                self.csocket = None
                print('客户端网络错误1')
        thread.start_new_thread(run, ())

    def timeconvent(self,utcstrtime):
        timest = timetool.utcStrTimeToTime(utcstrtime)
        timeint = int(timest)
        ltimeStr = str(timetool.timestamp2datetime(timeint,True))   
        return timeint,ltimeStr 
    

    def onMessage(self,msg):                #收到新的推送数据
        datdic = json.loads(msg)
        if 'table' in datdic:
            # self.sendMsgToClient(msg.encode())
            if datdic['table'] == 'tradeBin1m': #得到1分钟k线相关数据

            elif datdic['table'] == 'quote': #得到最高级深度数据更新
                # self.updateTopDeep(datdic['data'])
                print(msg)
    # "execution:XBTUSD","order:XBTUSD","margin:XTBUSD","position:XTBUSD"]
            elif datdic['table'] == 'execution':
                print(msg)
            elif datdic['table'] == 'order':
                print(msg)
            elif datdic['table'] == 'margin':
                print(msg)
            elif datdic['table'] == 'position':
                print(msg)
            else:
                print(msg)
        else:
            # print(msg)
            pass


def main():
    bitwstool = bitmexWSTool(None,None)
    bitwstool.wsRunForever()

if __name__ == '__main__':
    main()

    
