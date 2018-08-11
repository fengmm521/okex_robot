#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于访问OKCOIN 期货REST API

import bitmex

import json

# kfpth = '../../../../btc/bitmex/key.txt'
# kfpth = '/Users/Allen/Documents/key/bitmexkey.txt'



class BitMexFuture:

    def __init__(self,apikey,secretkey,isTest = True):

        self.apikey = apikey
        self.secret = secretkey

        self.client = bitmex.bitmex(test=False, api_key=apikey, api_secret=secretkey)
        # https://www.bitmex.com/realtime
        # https://www.bitmex.com/api/v1
        self.baseAmount = 100
        self.isTest = isTest

        dep = self.future_depth()
        print(dep)

        self.csocket = None

    def setClientSocket(self,clientsocket):
        self.csocket = clientsocket

    #向数据分析客户端发送消息
    def sendMsgToClient(self,msg):
        try:
            if self.csocket:
                self.csocket.send(msg.encode())
            else:
                print("没有客户端连接")
        except Exception as e:
            print('客户端网络错误')

    #收到来自数据分析客户端的下单请求
    def onTradeMsg(self,msgdict):
        #{'type':'os','amount':0,'postOnly':1}
        #{'type':'test','test':1}
        #{'type':'set','amount':100}
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
        
        bcmsg = ''
        if msgdict['type'] == 'test':
            self.isTest = bool(msgdict['test'])
            bcmsg = 'setTest:%d'%(self.isTest)
        elif msgdict['type'] == 'ol':#开多
            # self.baseAmount = msgdict['amount']
            if self.isTest:
                bcmsg = 'bimex_test_ol'
            else:
                bcmsg = self.future_trade_xbtusd(msgdict['price'], msgdict['amount'],'ol',bool(msgdict['islimit']))
            savestr = 'ol,price:%.1f,amount:%d,islimit:%d,bc:'%(msgdict['price'],msgdict['amount'],msgdict['islimit']) + str(bcmsg)
            self.testTradeSave(savestr)
            print(savestr)
        elif msgdict['type'] == 'cl':#平多
            if self.isTest:
                bcmsg = 'bimex_test_cl'
            else:
                bcmsg = self.future_trade_xbtusd(msgdict['price'], msgdict['amount'],'cl',bool(msgdict['islimit']))
            savestr = 'cl,price:%.1f,amount:%d,islimit:%d,bc:'%(msgdict['price'],msgdict['amount'],msgdict['islimit']) + str(bcmsg)
            self.testTradeSave(savestr)
            print(savestr)
        elif msgdict['type'] == 'os':#开空
            if self.isTest:
                bcmsg = 'bimex_test_os'
            else:
                bcmsg = self.future_trade_xbtusd(msgdict['price'], msgdict['amount'],'os',bool(msgdict['islimit']))
            savestr = 'os,price:%.1f,amount:%d,islimit:%d,bc:'%(msgdict['price'],msgdict['amount'],msgdict['islimit']) + str(bcmsg)
            self.testTradeSave(savestr)
            print(savestr)
        elif msgdict['type'] == 'cs':#平空
            if self.isTest:
                bcmsg = 'bimex_test_cs'
            else:
                bcmsg = self.future_trade_xbtusd(msgdict['price'], msgdict['amount'],'cs',bool(msgdict['islimit']))
            savestr = 'os,price:%.1f,amount:%d,islimit:%d,bc:'%(msgdict['price'],msgdict['amount'],msgdict['islimit']) + str(bcmsg)
            self.testTradeSave(savestr)
            print(savestr)
        elif msgdic['type'] == 'getall':#获取所有未成交定单
            # pass #返回所有未成交定单数据
            bcmsg = self.future_orderinfo()
        elif msgdic['type'] == 'getID':#获取某个定单的状态
            self.future_orderinfo(self,orderID = msgdict['id'])
        elif msgdic['type'] == 'cancelall':#取消所有未成交定单
            bcmsg = self.future_cancel(orderId = '')
        elif msgdic['type'] == 'cancel':#取消某个id定单
            bcmsg = self.future_cancel(orderId = msgdict['id'])
        elif msgdic['type'] == 'account':#获取帐户信息
            bcmsg = self.future_userinfo()
        elif msgdic['type'] == 'withdraw':#提现
            pass
            #暂时没实现提现接口
        elif msgdic['type'] == 'transfer':#okex资金划转
            pass
            #bitmex没有资金划转
        elif msgdict['type'] == 'funding':#bitmex获取持仓费率,
            bcmsg = self.future_funding()
        print(bcmsg)
        self.sendMsgToClient(str(bcmsg))
        return
    #获取最近5次的持仓费率
    def future_funding(self):
        #https://www.bitmex.com/api/v1/funding?count=5&reverse=true
        res = self.client.Funding.Funding_get(filter = '{"symbol":"xbtusd"}',count = 5,reverse = True).result()
        print(res)
        return res
    #期货全仓账户信息
    def future_userinfo(self):
        res = self.client.User.User_getMargin().result()
        print(res)
        return res
        #https://www.bitmex.com/api/v1/user/margin?currency=XBt

    #期货取消所有定单订单
    def future_cancel(self,orderId = ''):
        res = None
        if orderId == '' or (not orderId):
            res = self.client.Order.Order_cancelAll().result()
            print(res)
        else:
            res = self.client.Order.Order_cancel(orderId).result()
            print(res)
        return res

    #期货获取所有订单信息,或者某一个定单信息
    def future_orderinfo(self,orderID = ''):
        # https://www.bitmex.com/api/v1/order?filter=%7B%22symbol%22%3A%20%22XBTUSD%22%7D&count=100&reverse=true
        #获取最后10定单，有成交的也有没有成交的
        if orderID == '':
            res = self.client.Order.Order_getOrders(filter = '{"symbol":"xbtusd"}',count = 10,reverse = True).result()
            print(res)
            return res
        else:
            res = self.client.Order.Order_getOrders(filter = '{"symbol":"xbtusd","orderID": "%s"}'%(orderID),count = 10,reverse = True).result()
            print(res)
            return res
  #       [{
  #   "orderID": "87adcf6b-e22c-34d8-4902-242a24b9ba02",   #定单ID,
  #   "clOrdID": "",                                        #定单用户定义ID
  #   "clOrdLinkID": "",
  #   "account": 278343,
  #   "symbol": "XBTUSD",
  #   "side": "Buy",                                        #定单开单方向
  #   "simpleOrderQty": null,
  #   "orderQty": 600,                                      #定单委托数量
  #   "price": 5800,
  #   "displayQty": null,
  #   "stopPx": null,
  #   "pegOffsetValue": null,
  #   "pegPriceType": "",
  #   "currency": "USD",
  #   "settlCurrency": "XBt",
  #   "ordType": "Limit",        #定单类型
  #   "timeInForce": "GoodTillCancel",
  #   "execInst": "",
  #   "contingencyType": "",
  #   "exDestination": "XBME",
  #   "ordStatus": "New",        #定单状态，Filled:完全成交,New:未成交
  #   "triggered": "",
  #   "workingIndicator": true,                         #是否有效定单
  #   "ordRejReason": "",
  #   "simpleLeavesQty": 0.1034,  #委托价值
  #   "leavesQty": 600,           #未成交委托数量
  #   "simpleCumQty": 0,
  #   "cumQty": 0,
  #   "avgPx": null,
  #   "multiLegReportingType": "SingleSecurity",
  #   "text": "Submission from www.bitmex.com",
  #   "transactTime": "2018-08-10T23:08:56.018Z",
  #   "timestamp": "2018-08-10T23:08:56.018Z"
  # },{}]
    

    def testTradeSave(self,out):
        f = open('testtrade.txt','a')
        outstr = out + '\n'
        f.write(outstr)
        f.close()
    #xbtusd期货下单
    def future_trade_xbtusd(self,price,amount,tradeType,postOnly):
    # bitmex的被动下单方式:
    # 设置order的execInst参数为ParticipateDoNotInitiate，当下单价格为主动成交时，下单会被取消
    # ParticipateDoNotInitiate: Also known as a Post-Only order. 
    # If this order would have executed on placement, it will cancel instead.
        res = None
        tmpprice = '%.1f'%(float(price))
        # postOnly = not islimit
        # print('-----------------------')
        # print(self.client.Order.__dict__)
        # print(dir(self.client.Order))
        if tradeType == 'ol': #开多
            
            if postOnly:
                print('被动开多:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=int(amount),execInst='ParticipateDoNotInitiate', price=float(tmpprice)).result()
            else:
                print('开多:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=int(amount), price=float(tmpprice)).result()
        elif tradeType == 'cl': #平多
            
            if postOnly:
                print('被动平多:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-int(amount),execInst='ParticipateDoNotInitiate', price=float(tmpprice)).result()
            else:
                print('平多:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-int(amount),execInst='Close', price=float(tmpprice)).result()
        elif tradeType == 'os': #开空
            
            if postOnly:
                print('被动开空:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-int(amount),execInst='ParticipateDoNotInitiate', price=float(tmpprice)).result()
            else:
                print('开空:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=-int(amount), price=float(tmpprice)).result()
        elif tradeType == 'cs': #平空
            
            if postOnly:
                print('被动平空:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=int(amount),execInst='ParticipateDoNotInitiate', price=float(tmpprice)).result()
            else:
                print('平空:',tmpprice,amount)
                res = self.client.Order.Order_new(symbol='XBTUSD', orderQty=int(amount),execInst='Close', price=float(tmpprice)).result()
        else:
            print('tradeType,下单类型设置错误:',tradeType)
        return res[0]

    #OKCoin期货市场深度信息
    def future_depth(self,size = 2,symbol = 'XBT',contractType = 'XBTUSD'): 
        if symbol == 'XBT':
            if contractType == 'XBTUSD':
                #https://www.bitmex.com/api/v1/orderBook/L2?symbol=xbt&depth=2
                res = self.client.OrderBook.OrderBook_getL2(symbol=symbol,depth=size).result()
                return res[0]
            else:
                print('合约交易类型%s不可用:'%(contractType))

        else:
            print('市场类型%s不可用:'%(symbol))

        return None
    
    


    #OKCoin期货交易记录信息
    def future_trades(self,symbol,contractType):
        pass
        # FUTURE_TRADES_RESOURCE = "/api/v1/future_trades.do"
        # params = ''
        # if symbol:
        #     params += '&symbol=' + symbol if params else 'symbol=' +symbol
        # if contractType:
        #     params += '&contract_type=' + contractType if params else 'contract_type=' +symbol
        # return httpGet(self.__url,FUTURE_TRADES_RESOURCE,params)


    #获取美元人民币汇率
    def exchange_rate(self):
        pass
        # EXCHANGE_RATE = "/api/v1/exchange_rate.do"
        # return httpGet(self.__url,EXCHANGE_RATE,'')


    


    #期货全仓持仓信息
    def future_position(self,symbol,contractType):
        pass
        # FUTURE_POSITION = "/api/v1/future_position.do?"
        # params = {
        #     'api_key':self.__apikey,
        #     'symbol':symbol,
        #     'contract_type':contractType
        # }
        # params['sign'] = buildMySign(params,self.__secretkey)
        # return httpPost(self.__url,FUTURE_POSITION,params)


    #期货批量下单
    def future_batchTrade(self,symbol,contractType,orders_data,leverRate):
        pass
        # FUTURE_BATCH_TRADE = "/api/v1/future_batch_trade.do?"
        # params = {
        #     'api_key':self.__apikey,
        #     'symbol':symbol,
        #     'contract_type':contractType,
        #     'orders_data':orders_data,
        #     'lever_rate':leverRate
        # }
        # params['sign'] = buildMySign(params,self.__secretkey)
        # return httpPost(self.__url,FUTURE_BATCH_TRADE,params)

def main():
    futuretool = BitMexFuture()
    dep = futuretool.future_depth()
    print(type(dep))
    print(type(dep[0]))
    print(dep)

if __name__ == '__main__':
    main()





    
