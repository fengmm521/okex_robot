#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于访问OKCOIN 期货REST API

import bitmex

import json

# kfpth = '../../../../btc/bitmex/key.txt'
# kfpth = '/Users/Allen/Documents/key/bitmexkey.txt'



class BitMexFuture:

    def __init__(self,apiconfpth = None):

        if not apiconfpth:
            apiconfpth = '../../../../btc/bitmex/key.txt'
        
        f = open(apiconfpth,'r')
        lines = f.readlines()
        f.close()

        apikey = lines[0].replace('\r','').replace('\n','')
        secretkey = lines[1].replace('\r','').replace('\n','')

        self.client = bitmex.bitmex(test=False, api_key=apikey, api_secret=secretkey)
        # https://www.bitmex.com/realtime
        # https://www.bitmex.com/api/v1
        self.baseAmount = 100
        self.isTest = True

        dep = self.future_depth()
        print(dep)

    def testTradeSave(self,out):
        f = open('testtrade.txt','a')
        outstr = out + '\n'
        f.write(outstr)
        f.close()

    def onTradeMsg(self,msgdict):
        #{'type':'os','amount':0,'postOnly':1}
        #{'type':'test','test':1}
        #{'type':'set','amount':100}

        if msgdict['type'] == 'test':
            self.isTest = bool(msgdict['test'])
        elif msgdict['type'] == 'set':
            self.baseAmount = msgdict['amount']
        else:
            dep = self.future_depth(size = 1)
            if self.isTest:
                out = ''
                if len(dep) == 2:
                    depjson = json.dumps(dep)
                    msgjson = json.dumps(msgdict)
                    out = '(%s,sell:%.1f,buy:%.1f)'%(msgdict['type'],dep[0]['price'],dep[1]['price']) + '-' + msgjson + '-' + depjson 
                else:
                    out = '(%s,getDepErro)'%(msgdict['type']) + '-' + msgjson + '-' + str(dep) 
                self.testTradeSave(out)
                return
            else:
                if msgdict['type'] == 'os':
                    
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    if msgdict['amount'] > 0:
                        self.future_trade_xbtusd(selldep['price'], msgdict['amount'],'os',bool(msgdict['postOnly']))
                    else:
                        self.future_trade_xbtusd(selldep['price'], self.baseAmount,'os',bool(msgdict['postOnly']))
                elif msgdict['type'] == 'clos': #平多并开空
                    
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    tmpamount = self.baseAmount*2
                    if msgdict['amount'] > 0:
                        tmpamount = msgdict['amount']*2
                    self.future_trade_xbtusd(selldep['price'], tmpamount,'os',bool(msgdict['postOnly']))
                elif msgdict['type'] == 'cs':
                    # dep = self.future_depth(size = 1)
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    if msgdict['amount'] > 0:
                        self.future_trade_xbtusd(buydep['price'], msgdict['amount'],'cs',bool(msgdict['postOnly']))
                    else:
                        self.future_trade_xbtusd(buydep['price'], self.baseAmount,'cs',bool(msgdict['postOnly']))

                elif msgdict['type'] == 'ol':
                    # dep = self.future_depth(size = 1)
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    if msgdict['amount'] > 0:
                        self.future_trade_xbtusd(buydep['price'], msgdict['amount'],'ol',bool(msgdict['postOnly']))
                    else:
                        self.future_trade_xbtusd(buydep['price'], self.baseAmount,'ol',bool(msgdict['postOnly']))
                elif msgdict['type'] == 'csol': #平空并开多
                    # dep = self.future_depth(size = 1)
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    tmpamount = self.baseAmount * 2
                    if msgdict['amount'] > 0:
                        tmpamount = msgdict['amount'] * 2
                    self.future_trade_xbtusd(buydep['price'], tmpamount,'ol',bool(msgdict['postOnly']))
                elif msgdict['type'] == 'cl':
                    # dep = self.future_depth(size = 1)
                    # [{'symbol': 'XBTUSD', 'id': 8799324550, 'side': 'Sell', 'size': 87938, 'price': 6754.5}, {'symbol': 'XBTUSD', 'id': 8799324600, 'side': 'Sell', 'size': 825379, 'price': 6754.0}, {'symbol': 'XBTUSD', 'id': 8799324650, 'side': 'Buy', 'size': 777661, 'price': 6753.5}, {'symbol': 'XBTUSD', 'id': 8799324700, 'side': 'Buy', 'size': 42653, 'price': 6753.0}]
                    if len(dep) != 2:
                        print('获取市场深度错误，下单失改')
                        return
                    selldep = dep[0]
                    buydep = dep[1]
                    if msgdict['amount'] > 0:
                        self.future_trade_xbtusd(selldep['price'], msgdict['amount'],'cl',bool(msgdict['postOnly']))
                    else:
                        self.future_trade_xbtusd(selldep['price'], self.baseAmount,'cl',bool(msgdict['postOnly']))
                else:
                    print('type erro:',msgdict['type'])
                out = ''
                if len(dep) == 2:
                    depjson = json.dumps(dep)
                    msgjson = json.dumps(msgdict)
                    out = '(%s,sell:%.1f,buy:%.1f)'%(msgdict['type'],dep[0]['price'],dep[1]['price']) + '-' + msgjson + '-' + depjson 
                else:
                    out = '(%s,getDepErro)'%(msgdict['type']) + '-' + msgjson + '-' + str(dep) 
                self.testTradeSave(out)

    #xbtusd期货下单
    def future_trade_xbtusd(self,price,amount,tradeType,postOnly = False):
    # bitmex的被动下单方式:
    # 设置order的execInst参数为ParticipateDoNotInitiate，当下单价格为主动成交时，下单会被取消
    # ParticipateDoNotInitiate: Also known as a Post-Only order. 
    # If this order would have executed on placement, it will cancel instead.
        res = None
        tmpprice = '%.1f'%(float(price))
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


    #期货取消所有定单订单
    def future_cancel(self,symbol,contractType,orderId):
        res = None
        if orderId == '' or (not orderId):
            res = self.client.Order.Order_cancelAll().result()
            print(res)
        else:
            res = self.client.Order.Order_cancel(orderId).result()
            print(res)
        return res

    #期货获取订单信息
    def future_orderinfo(self,symbol,contractType,orderId,status,currentPage,pageLength):
        pass
        # FUTURE_ORDERINFO = "/api/v1/future_order_info.do?"
        # params = {
        #     'api_key':self.__apikey,
        #     'symbol':symbol,
        #     'contract_type':contractType,
        #     'order_id':orderId,
        #     'status':status,
        #     'current_page':currentPage,
        #     'page_length':pageLength
        # }
        # params['sign'] = buildMySign(params,self.__secretkey)
        # return httpPost(self.__url,FUTURE_ORDERINFO,params)

    

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


    #期货全仓账户信息
    def future_userinfo(self):
        pass
        # FUTURE_USERINFO = "/api/v1/future_userinfo.do?"
        # params ={}
        # params['api_key'] = self.__apikey
        # params['sign'] = buildMySign(params,self.__secretkey)
        # return httpPost(self.__url,FUTURE_USERINFO,params)

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





    
