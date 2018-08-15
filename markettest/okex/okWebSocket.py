#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time
import zlib
import hashlib
import websocket
import json
import thread
#okex
#websocket只用来定阅数据推送，下单使用rest的https接口发送

class okWSTool():
    def __init__(self):

        self.csocket = None

        self.sells5 = []
        self.buys5 = []


        self.objname = 'okex'

        self.sendcount = 100   #每100次log提示一次没有客户端连接

        self.testdatas = []

        self.sendTestIndex = 0

        self.sendTestDelay = 1

        self.initTestData()

    def initTestData(self):
        f = open('testdata2.txt','r')
        lines = f.readlines()
        f.close()
        for l in lines():
            tmpl = l.replace('\n','')
            if len(tmpl) > 5:
                dtmp = json.loads(tmpl)
                dattmp = [{"binary":0,"channel":"ok_sub_futureusd_btc_depth_quarter_5","data":{"asks":[[dtmp['buy'],150,2.3403,12.5319,803]],"bids":[[dtmp['sell'],150,0.2809,0.2809,18]],"timestamp":1534351230420}}]
                self.testdatas.append(dattmp)

    def sendDataTest(self):
        #[{"binary":0,"channel":"ok_sub_futureusd_btc_depth_quarter_5","data":{"asks":[[6409.26,150,2.3403,12.5319,803],[6408.64,20,0.312,10.1916,653],[6407.76,121,1.8883,9.8796,633],[6407.63,192,2.9964,7.9913,512],[6406.43,320,4.9949,4.9949,320]],"bids":[[6406.39,18,0.2809,0.2809,18],[6406.18,18,0.2809,0.5618,36],[6405.27,1181,18.4379,18.9997,1217],[6405.15,150,2.3418,21.3415,1367],[6405.11,128,1.9984,23.3399,1495]],"timestamp":1534351230420}}]
        #[{"binary":0,"channel":"ok_sub_futureusd_btc_depth_quarter_5","data":{"asks":[[6409.26,150,2.3403,12.5319,803]],"bids":[[6406.39,18,0.2809,0.2809,18]]],"timestamp":1534351230420}}]

        msgdic = self.testdatas[self.sendTestIndex]
        self.sendTestIndex += 1
        if self.sendTestIndex == len(self.testdatas):
            self.sendTestIndex = 0

        msg = json.dumps(msgdic)

        self.sendMsgToClient(msg)


    def setObjName(self,pname):
        self.objname = pname

    #事件回调函数
    def setSocketClient(self,clientsocket):
        self.csocket = clientsocket

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
                print('客户端网络错误')
                if self.csocket:
                    self.csocket.close()
                self.csocket = None
                return
        thread.start_new_thread(run, ())
        
    #接收到测试下单服务器数据
    def reciveDataFromTestTrade(self,datadict):
        print(data)
        #{'type':下单类型,price:下单价格,amount:下单数量,cid:下单用户ID},下单类型分为:开多，开空，平多，平空，取消定单5种
        #要返回的发送的交易状态信息
        #1.完全成交信息
        #2.定单取消信息
        #3.价格上涨信息
        #4.价格下跌信息
    #收到来自数据处理的命令消息
    def reciveCmdFromClient(self,cmd):
        print(cmd)
        self.sendMsgToClient(str(cmd))


    def setDeeps(self,datadic):
        self.sells5 = datadic['asks'][::-1]
        self.buys5 = datadic['bids']
        print(self.buys5[0],self.sells5[0])

    def saveTestData(self,msg):
        f = open('testdata.txt','a')
        f.write(msg + '\n')
        f.close()

    def on_message(self,ws,data):
        # data = self.inflate(evt) #data decompress
        try:
            self.sendMsgToClient(data)
            datadic = json.loads(data)[0]
            chanle = datadic['channel']
            if chanle == 'ok_sub_futureusd_btc_depth_quarter_5':#深度全量数据
                # print(datadic)
                # self.setDeeps(datadic['data'])
                self.saveTestData(data)
            elif chanle == 'ok_sub_futureusd_trades':
                #交易数据更新
                self.onTrade(datadic)
            elif chanle == 'ok_sub_futureusd_positions': #合约持仓信息更新
                self.onPositionsChange(datadic)
            elif chanle == 'ok_sub_futureusd_userinfo':  #合约帐户信息更新
                self.onUserInfoChange(datadic)
            else:
                # print(data)
                pass
        except Exception as e:
            print('-'*20)
            print(data)


    
    #ping服务器查看连接是否断开
    #服务器未断开会返回{"event":"pong"}
    def pingServer(self):
        channelcmd = "{'event':'ping'}"
        self.wsocket.send(channelcmd);


def main():


    oktool = okWSTool()
    oktool.wsRunForever()
if __name__ == '__main__':
    main()