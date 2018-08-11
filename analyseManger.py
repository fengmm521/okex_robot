#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import os,sys
from sys import version_info  

if version_info.major < 3:
    magetoolpth = '/usr/local/lib/python2.7/site-packages'
    if magetoolpth not in sys.path:
        sys.path.append(magetoolpth)
    else:
        print('heave magetool pth')

import socket
import threading
import time
import json

from magetool import pathtool
from magetool import timetool
sys.path.append('util')
import signTool



def sayMsg(msg):
    cmd = 'say %s'%(msg)
    os.system(cmd)
    print msg


class TradeTool(object):
    """docstring for ClassName"""
    def __init__(self,configdic,isTest = True):
        #期货交易工具
        self.configdic = configdic
        self.isTest = isTest

        self.initTraddeConfig()

        #okex
        self.okexSeckey = configdic['okex']['secretkey']
        self.okexDataSocket = None
        self.okexDatathr = None
        self.okexTradeSocket = None
        self.okexTradethr = None



        #bitmex
        self.bitmexSeckey = configdic['bitmex']['secretkey']
        self.bitmexDataSocket = None
        self.bitmexDatathr = None
        self.bitmexTradeSocket = None
        self.bitmexTradethr = None


        self.avrOkexBuy = 0.0
        self.avrBitmexBuy = 0.0

        self.avrOkexSell = 0.0
        self.avrBitmexSell = 0.0

        self.avrDelayTime = 1*60*60   #单位:秒

        self.okexBTC = 0.0
        self.bitmexBTC = 0.0

        self.tradeSavePth = 'log/trade.txt'
        
        self.socketstate = {'bd':False,'bt':False,'od':False,'ot':False}

        ptime = int(time.time())
        self.lastimedic = {'bd':ptime,'bt':ptime,'od':ptime,'ot':ptime}

        self.initSocket()

        self.okexDatas = []             #买一价，卖一价，接收数据时间
        self.bitmexDatas = []           #买一价，卖一价, 接收数据时间
        self.lastSub = {}               #okex的卖一价和bitmex的买一价的差价，bitmex的卖一价和okex的买一价的差价,时间差,最后接收时间

    #初始化交易参数,如单次下单合约值，谁主动成交，谁被动成交,交易手续费等
    def initTraddeConfig(self):
        pass

    def initSocket(self):
        isErro = False
        try:
            print('connecting okex http trade server:',self.configdic['okex']['httpaddr'],self.configdic['okex']['httpport'])
            self.okexTradeSocket = socket.socket()  # instantiate
            self.okexTradeSocket.connect((self.configdic['okex']['httpaddr'], self.configdic['okex']['httpport']))  # connect to the server
            print('okex http trade server connected!')
            def okexTradeRun():
                while True:
                    data = self.okexTradeSocket.recv(100*1024)
                    datadic = json.loads(data.decode())
                    self.onOkexTradeBack(datadic)
            self.okexTradethr = threading.Thread(target=okexTradeRun,args=())
            self.okexTradethr.setDaemon(True)
            self.okexTradethr.start()
            self.socketstate['ot'] = True
        except Exception as e:
            print('connect okex http trade server erro...')
            self.okexTradeSocket = None
            isErro =  True
        try:
            print('connecting okex ws data server:',self.configdic['okex']['wsaddr'],self.configdic['okex']['wsport'])
            self.okexDataSocket = socket.socket()  # instantiate
            self.okexDataSocket.connect((self.configdic['okex']['wsaddr'], self.configdic['okex']['wsport']))  # connect to the server
            print('okex ws data server connected!')
            def okexDataRun():
                while True:
                    data = self.okexDataSocket.recv(100*1024)
                    datadic = json.loads(data.decode())
                    self.onOkexData(datadic)
            self.okexDatathr = threading.Thread(target=okexDataRun,args=())
            self.okexDatathr.setDaemon(True)
            self.okexDatathr.start()
            self.socketstate['od'] = True
        except Exception as e:
            print('connect erro okex ws data...')
            self.okexDataSocket = None
            isErro =  True
        try:
            print('connecting bitmex Trade data server:',self.configdic['bitmex']['httpaddr'],self.configdic['bitmex']['httpport'])
            self.bitmexTradeSocket = socket.socket()  # instantiate
            self.bitmexTradeSocket.connect((self.configdic['bitmex']['httpaddr'], self.configdic['bitmex']['httpport']))  # connect to the server
            print('bitmex ws Trade server connected!')
            def okexDataRun():
                while True:
                    data = self.bitmexTradeSocket.recv(100*1024)
                    datadic = json.loads(data.decode())
                    self.onBitmexTradeBack(datadic)
            self.bitmexTradethr = threading.Thread(target=okexDataRun,args=())
            self.bitmexTradethr.setDaemon(True)
            self.bitmexTradethr.start()
            self.socketstate['bt'] = True
        except Exception as e:
            print('connect erro bitmex trade...')
            self.bitmexTradeSocket = None
            isErro =  True
        try:
            print('connecting bitmex ws data server:',self.configdic['bitmex']['wsaddr'],self.configdic['bitmex']['wsport'])
            self.bitmexDataSocket = socket.socket()  # instantiate
            self.bitmexDataSocket.connect((self.configdic['bitmex']['wsaddr'], self.configdic['bitmex']['wsport']))  # connect to the server
            print('bitmex ws data server connected!')
            def bitmexDataRun():
                while True:
                    data = self.bitmexDataSocket.recv(100*1024)
                    try:
                        datadic = json.loads(data.decode())
                        self.onBitmexData(datadic)
                    except Exception as e:
                        print('-------erro bitmex data -------')
                        print(data)
                    
            self.bitmexDatathr = threading.Thread(target=bitmexDataRun,args=())
            self.bitmexDatathr.setDaemon(True)
            self.bitmexDatathr.start()
            self.socketstate['bd'] = True
        except Exception as e:
            print('connect erro bitmex ws data...')
            self.bitmexDataSocket = None
            isErro =  True
        return (not isErro)

    def timeconvent(self,utcstrtime):
        timest = timetool.utcStrTimeToTime(utcstrtime)
        timeint = int(timest)
        ltimeStr = str(timetool.timestamp2datetime(timeint,True))   
        return timeint,ltimeStr 

    def updateDataSub(self):
        #self.okexDatas = []             #买一价，卖一价，接收数据时间
        #self.bitmexDatas = []           #买一价，卖一价, 接收数据时间
        #self.lastSub = []               #okex的卖一价和bitmex的买一价的差价，bitmex的卖一价和okex的买一价的差价,时间差,最后接收时间
        if self.okexDatas and self.bitmexDatas:
            self.lastSub['ob'] = {'subOB':self.okexDatas[1][0] - self.bitmexDatas[0][0],'odeep':self.okexDatas[1][1],'bdeep':self.bitmexDatas[0][1]}
            self.lastSub['bo'] = {'subBO':self.bitmexDatas[1][0] - self.okexDatas[0][0],'odeep':self.okexDatas[0][1],'bdeep':self.bitmexDatas[1][1]}
            self.lastSub['otime'] = self.okexDatas[2]
            self.lastSub['btime'] = self.bitmexDatas[2]
            self.lastSub['subtime'] = self.okexDatas[2] - self.bitmexDatas[2]
            # print('-'*20)
            print('ob:',round(self.lastSub['ob']['subOB'],3),self.lastSub['ob']['odeep'],self.lastSub['ob']['bdeep'],'bo:',round(self.lastSub['bo']['subBO'],3),self.lastSub['bo']['odeep'],self.lastSub['bo']['bdeep'],self.lastSub['subtime'])
    
    #检测是否需要下单
    def tradeTest(self):
        pass
    # 下单数据格式:
    # 开多,
    # {type:ol,amount:100,price:100,islimit:1}
    # 平多,
    # {type:cl,amount:100,price:100,islimit:1}
    # 开空,
    # {type:os,amount:100,price:100,islimit:1}
    # 平空
    # {type:cs,amount:100,price:100,islimit:1}

    # 获取定单状态
    # 获取所有定单状态
    # {type:getall}
    # 使用定单ID获取定单状态
    # {type:getID,id:123456}
    # 取消某个定单
    # {type:cancel,id:123456}
    # 取消所有定单
    # {type:cancelall}
    # 获取费率
    # {type:funding}

    # 帐户
    # 获取帐户信息
    # {type:account}
    # 提现
    # {type:withdraw,addr:地址,amount:数量,price:支付手续费,cointype:btc}
    # okex资金划转
    # {type:transfer,amount:数量,from:从那个资金帐户划转,to:划转到那个资金帐户,cointype:btc}
    #收到数据   
    #okex数据
    def onOkexData(self,datadic):
        if 'type' in datadic and datadic['type'] == 'pong':
            self.socketstate['od'] = True
            print('pong from okex ws data server...')
        elif type(datadic) == list and 'channel' in datadic[0] and datadic[0]['channel'] == 'ok_sub_futureusd_btc_depth_quarter_5':
            # print(datadic)
            data = datadic[0]['data']
            self.sells5 = data['asks'][::-1]
            self.buys5 = data['bids']
            self.okexDatas = [self.buys5[0],self.sells5[0],int(time.time())]             #买一价，卖一价，接收数据时间
            self.updateDataSub()
            # print(self.buys5[0],self.sells5[0])
        else:
            print(datadic)
        self.lastimedic['od'] = int(time.time())
    #交易下单返回状态
    def onOkexTradeBack(self,datadic):
        if 'type' in datadic and datadic['type'] == 'pong':
            self.socketstate['ot'] = True
            print('pong from okex trade http server...')
        else:
            print(datadic)
        self.lastimedic['ot'] = int(time.time())

    #bitmex数据
    def onBitmexData(self,datadic):
        if 'type' in datadic and datadic['type'] == 'pong':
            self.socketstate['bd'] = True
            print('pong from bitmex ws data server...')
        elif 'table' in datadic and datadic['table'] == 'quote':
            datas = datadic['data']
            timeint,timestr = self.timeconvent(datas[-1]['timestamp'])
            self.selltop = [datas[-1]['askPrice'],datas[-1]['askSize'],timeint,timestr]
            self.buytop = [datas[-1]['bidPrice'],datas[-1]['bidSize'],timeint,timestr]
            self.bitmexDatas = [self.buytop,self.selltop,self.buytop[2]]           #买一价，卖一价, 接收数据时间
            self.updateDataSub()
            # print(self.buytop,self.selltop)
        else:
            print(datadic)
        self.lastimedic['bd'] = int(time.time())
    def onBitmexTradeBack(self,datadic):
        if 'type' in datadic and datadic['type'] == 'pong':
            self.socketstate['bt'] = True
            print('pong from bitmex trade http server...')
        else:
            print(datadic)

        self.lastimedic['bt'] = int(time.time())

    #更新交易状态
    def updateTradeState(self):
        pass

    def sendMsgToBitmexData(self,ptype,msg,isSigned = False):
        try:
            if self.bitmexDataSocket:
                if isSigned:
                    outobj = {'type':ptype,'time':int(time.time()),'sign':'issigned','data':msg}
                    outstr = json.dumps(outobj)
                    self.bitmexDataSocket.send(outstr.encode())
                else:
                    ptime = int(time.time())
                    sign = signTool.signMsg(msg,ptime,self.bitmexSeckey)
                    outobj = {'type':ptype,'time':ptime,'sign':sign,'data':msg}
                    outstr = json.dumps(outobj)
                    self.bitmexDataSocket.send(outstr.encode())
            else:
                print("没有bitmexDataSocket客户端连接")
        except Exception as e:
            print('服务器端bitmexDataSocket网络错误1')

    def sendMsgToBitmexTrade(self,ptype,msg,isSigned = False):
        try:
            if self.bitmexTradeSocket:
                if isSigned:
                    outobj = {'type':ptype,'time':int(time.time()),'sign':'issigned','data':msg}
                    outstr = json.dumps(outobj)
                    self.bitmexTradeSocket.send(outstr.encode())
                else:
                    ptime = int(time.time())
                    sign = signTool.signMsg(msg,ptime,self.bitmexSeckey)
                    outobj = {'type':ptype,'time':ptime,'sign':sign,'data':msg}
                    outstr = json.dumps(outobj)
                    self.bitmexTradeSocket.send(outstr.encode())
            else:
                print("没有bitmexTradeSocket客户端连接")
        except Exception as e:
            print('服务器端bitmexTradeSocket网络错误1')

    def sendMsgToOkexData(self,ptype,msg,isSigned = False):
        try:
            if self.okexDataSocket:
                if isSigned:
                    outobj = {'type':ptype,'time':int(time.time()),'sign':'issigned','data':msg}
                    outstr = json.dumps(outobj)
                    self.okexDataSocket.send(outstr.encode())
                else:
                    ptime = int(time.time())
                    sign = signTool.signMsg(msg,ptime,self.okexSeckey)
                    outobj = {'type':ptype,'time':ptime,'sign':sign,'data':msg}
                    outstr = json.dumps(outobj)
                    self.okexDataSocket.send(outstr.encode())
            else:
                print("没有okexDataSocket客户端连接")
        except Exception as e:
            print('服务器端okexDataSocket网络错误1')

    def sendMsgToOkexTrade(self,ptype,msg,isSigned = False):
        try:
            if self.okexTradeSocket:
                if isSigned:
                    outobj = {'type':ptype,'time':int(time.time()),'sign':'issigned','data':msg}
                    outstr = json.dumps(outobj)
                    self.okexTradeSocket.send(outstr.encode())
                else:
                    ptime = int(time.time())
                    sign = signTool.signMsg(msg,ptime,self.okexSeckey)
                    outobj = {'type':ptype,'time':ptime,'sign':sign,'data':msg}
                    outstr = json.dumps(outobj)
                    self.okexTradeSocket.send(outstr.encode())
            else:
                print("没有okexDataSocket客户端连接")
        except Exception as e:
            print('服务器端okexDataSocket网络错误1')
    
    #当有客户端30秒没有接收到数据时就发送ping
    def pingAllServer(self,ptimeDelay = 30):
        ptime = int(time.time())
        for k in self.socketstate.keys():
            if ptime - self.lastimedic[k] > ptimeDelay:
                self.socketstate[k] = False
            else:
                self.socketstate[k] = True
        if not self.socketstate['bd']:
            self.sendMsgToBitmexData('ping','ping',isSigned = True)
        if not self.socketstate['bt']:
            self.sendMsgToBitmexTrade('ping','ping',isSigned = True)
        if not self.socketstate['od']:
            self.sendMsgToOkexData('ping','ping',isSigned = True)
        if not self.socketstate['ot']:
            self.sendMsgToOkexTrade('ping','ping',isSigned = True)
    def printSet(self):
        print 'isTest:',self.isTest
        print 'amount:',self.amount

    def cleanAllTrade(self):
        pass


def main():
     pass
if __name__ == '__main__':
    main()
   
