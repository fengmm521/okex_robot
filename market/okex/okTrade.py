#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于访问OKCOIN 期货REST API
from HttpMD5Util import buildMySign,httpGet,httpPost
import json

class OKFuture:
    def __init__(self,url,apikey,secretkey,isTest = True):
        self.__url = url
        self.__apikey = apikey
        self.__secretkey = secretkey
        self.secretkey = secretkey
        self.csocket = None
        self.isTest = isTest
        self.objname = 'okex'
    def setObjName(self,pname):
        self.objname = pname

    def setSocketClient(self,clientSocket):
        self.csocket = clientSocket

    #收到数据处理端的下单消息
    def onTradeMsg(self,msgdic):
    # 下单数据格式:
    #设置打开或者关闭测试模式
    #{type:test,test:1}
    

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

    # 帐户
    # 获取帐户信息
    # {type:account}
    # 提现
    # {type:withdraw,addr:地址,amount:数量,price:支付手续费,cointype:btc}
    # okex资金划转
    # {type:transfer,amount:数量,from:从那个资金帐户划转,to:划转到那个资金帐户,cointype:btc}
    
        bcmsg = ''

        if msgdic['type'] == 'ol':#开多
            if self.isTest:
                print('测试开多，数量:%d,价格:%.2f,是否限价单:%d'%(msgdic['amount'],msgdic['price'],msgdic['islimit']))
                bcmsg = 'test'
            else:
                pmatchPrice = '0'
                if msgdic['islimit'] == 0:
                    pmatchPrice = '1' #对手价，即市价下单
                bcmsg = self.future_trade(symbol = 'btc_usd', contractType = 'quarter',price='%.2f'%(msgdic['price']),amount = str(msgdic['amount']),tradeType = '1',matchPrice = pmatchPrice)
        elif msgdic['type'] == 'cl':#平多
            if self.isTest:
                print('测试平多，数量:%d,价格:%.2f,是否限价单:%d'%(msgdic['amount'],msgdic['price'],msgdic['islimit']))
            else:
                pmatchPrice = '0'
                if msgdic['islimit'] == 0:
                    pmatchPrice = '1' #对手价，即市价下单
                bcmsg = self.future_trade(symbol = 'btc_usd', contractType = 'quarter',price='%.2f'%(msgdic['price']),amount = str(msgdic['amount']),tradeType = '3',matchPrice = pmatchPrice)

        elif msgdic['type'] == 'os':#开空
            if self.isTest:
                print('测试开空，数量:%d,价格:%.2f,是否限价单:%d'%(msgdic['amount'],msgdic['price'],msgdic['islimit']))
            else:
                pmatchPrice = '0'
                if msgdic['islimit'] == 0:
                    pmatchPrice = '1' #对手价，即市价下单
                bcmsg = self.future_trade(symbol = 'btc_usd', contractType = 'quarter',price='%.2f'%(msgdic['price']),amount = str(msgdic['amount']),tradeType = '2',matchPrice = pmatchPrice)

        elif msgdic['type'] == 'cs':#平空
            if self.isTest:
                print('测试平空，数量:%d,价格:%.2f,是否限价单:%d'%(msgdic['amount'],msgdic['price'],msgdic['islimit']))
            else:
                pmatchPrice = '0'
                if msgdic['islimit'] == 0:
                    pmatchPrice = '1' #对手价，即市价下单
                bcmsg = self.future_trade(symbol = 'btc_usd', contractType = 'quarter',price='%.2f'%(msgdic['price']),amount = str(msgdic['amount']),tradeType = '4',matchPrice = pmatchPrice)

        elif msgdic['type'] == 'getall':#获取所有未成交定单，这里主要是看还有多少未成交的
            # 获取所有定单状态
            # {type:getall}
            bcmsg = self.future_orderinfo(symbol = 'btc_usd', contractType = 'quarter', orderId = '-1', status = '1', currentPage = '1', pageLength = '20')
            # pass #返回所有未成交定单数据
        elif msgdic['type'] == 'getID':#获取某个定单的状态,这里主要是看看手续费,成交价
            # 使用定单ID获取定单状态
            # {type:getID,id:123456}
            bcmsg = self.future_orderinfo(symbol = 'btc_usd', contractType = 'quarter', orderId = str(msgdic['id']), status = '', currentPage = '1', pageLength = '20')
            # pass #返回请求定单数据
        elif msgdic['type'] == 'cancelall':#取消所有未成交定单
            # pass
            # 取消所有定单
            # {type:cancelall}
            #首先获取所有未成交定单
            if self.isTest:
                bcmsg = 'test_cancelall'
            else:
                bcmsgtmp = self.future_orderinfo(symbol = 'btc_usd', contractType = 'quarter', orderId = '-1', status = '1', currentPage = '1', pageLength = '20')
                # pass #返回所有未成交定单数据
                bddic = json.loads(bcmsgtmp)
                if bddic['result'] == True and len(bddic['orders']) > 0:
                    corderids = ''
                    for od in bddic['orders']:
                        corderids += str(od['order_id']) + ','
                    corderids = corderids[:-1]
                    bcmsg = self.future_cancel(symbol = 'btc_usd', contractType = 'quarter', orderId = corderids)

        elif msgdic['type'] == 'cancel':#取消某个id定单
            # 取消某个定单
            # {type:cancel,id:123456}
            if self.isTest:
                bcmsg = 'test_cancel,id=%s'%(str(msgdic['id']))
            else:
                bcmsg = self.future_cancel(symbol = 'btc_usd', contractType = 'quarter', orderId = str(msgdic['id']))
            # pass
        elif msgdic['type'] == 'account':#获取帐户信息,帐户权益和保证金率,主要是看会不会全仓爆仓
            # pass
            bcmsg = self.future_userinfo()
        elif msgdic['type'] == 'withdraw':#提现
            if self.isTest:
                bcmsg = 'test_withdraw'
                print(str(msgdic))
            else:
                pass #合约这里没有提现接口，提现要在现货中调用接口
            # pass
        elif msgdic['type'] == 'transfer':#okex资金划转
            # okex资金划转
            # {type:transfer,amount:数量,from:从那个资金帐户划转,to:划转到那个资金帐户,cointype:btc}
            pass #合约这里没有这个接口，在要现在货中调用
        elif msgdict['type'] == 'test':
            self.isTest = bool(msgdict['test'])
            bcmsg = 'setTest:%d'%(self.isTest)
        elif msgdict['type'] == 'funding':#bitmex获取持仓费率,
            pass #okex没有永续合约，所以没有持仓费问题
        print(bcmsg)
        self.sendMsgToClient(str(bcmsg))
    #期货全仓账户信息
    def future_userinfo(self):
        FUTURE_USERINFO = "/api/v1/future_userinfo.do?"
        params ={}
        params['api_key'] = self.__apikey
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_USERINFO,params)

    #期货全仓持仓信息
    def future_position(self,symbol,contractType):
        FUTURE_POSITION = "/api/v1/future_position.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType
        }
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_POSITION,params)

    #期货取消订单
    def future_cancel(self,symbol,contractType,orderId):
        FUTURE_CANCEL = "/api/v1/future_cancel.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType,
            'order_id':orderId
        }
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_CANCEL,params)

    #期货获取订单信息
    def future_orderinfo(self,symbol,contractType,orderId,status,currentPage,pageLength):
        FUTURE_ORDERINFO = "/api/v1/future_order_info.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType,
            'order_id':orderId,
            'status':status,
            'current_page':currentPage,
            'page_length':pageLength
        }
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_ORDERINFO,params)
    #期货下单
    def future_trade(self,symbol,contractType,price='',amount='',tradeType='',matchPrice='',leverRate=''):
        FUTURE_TRADE = "/api/v1/future_trade.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType,
            'amount':amount,
            'type':tradeType,
            'match_price':matchPrice,
            'lever_rate':leverRate
        }
        if price:
            params['price'] = price
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_TRADE,params)

    #向数据处理服务器发送消息
    def sendMsgToClient(self,msg):
        try:
            if self.csocket:
                self.csocket.send(msg.encode())
            else:
                print("没有客户端连接")
        except Exception as e:
            print('客户端网络错误')

    #OKCOIN期货行情信息
    def future_ticker(self,symbol,contractType):
        FUTURE_TICKER_RESOURCE = "/api/v1/future_ticker.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' +symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' +symbol
        return httpGet(self.__url,FUTURE_TICKER_RESOURCE,params)

    #OKCoin期货市场深度信息
    def future_depth(self,symbol,contractType,size): 
        FUTURE_DEPTH_RESOURCE = "/api/v1/future_depth.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' +symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' +symbol
        if size:
            params += '&size=' + size if params else 'size=' + size
        return httpGet(self.__url,FUTURE_DEPTH_RESOURCE,params)

    #OKCoin期货交易记录信息
    def future_trades(self,symbol,contractType):
        FUTURE_TRADES_RESOURCE = "/api/v1/future_trades.do"
        params = ''
        if symbol:
            params += '&symbol=' + symbol if params else 'symbol=' +symbol
        if contractType:
            params += '&contract_type=' + contractType if params else 'contract_type=' +symbol
        return httpGet(self.__url,FUTURE_TRADES_RESOURCE,params)

    #OKCoin期货指数
    def future_index(self,symbol):
        FUTURE_INDEX = "/api/v1/future_index.do"
        params=''
        if symbol:
            params = 'symbol=' +symbol
        return httpGet(self.__url,FUTURE_INDEX,params)

    #获取美元人民币汇率
    def exchange_rate(self):
        EXCHANGE_RATE = "/api/v1/exchange_rate.do"
        return httpGet(self.__url,EXCHANGE_RATE,'')

    #获取预估交割价
    def future_estimated_price(self,symbol):
        FUTURE_ESTIMATED_PRICE = "/api/v1/future_estimated_price.do"
        params=''
        if symbol:
            params = 'symbol=' +symbol
        return httpGet(self.__url,FUTURE_ESTIMATED_PRICE,params)
    
    #期货批量下单
    def future_batchTrade(self,symbol,contractType,orders_data,leverRate):
        FUTURE_BATCH_TRADE = "/api/v1/future_batch_trade.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType,
            'orders_data':orders_data,
            'lever_rate':leverRate
        }
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_BATCH_TRADE,params)

    #期货逐仓账户信息
    def future_userinfo_4fix(self):
        FUTURE_INFO_4FIX = "/api/v1/future_userinfo_4fix.do?"
        params = {'api_key':self.__apikey}
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_INFO_4FIX,params)

    #期货逐仓持仓信息
    def future_position_4fix(self,symbol,contractType,type1):
        FUTURE_POSITION_4FIX = "/api/v1/future_position_4fix.do?"
        params = {
            'api_key':self.__apikey,
            'symbol':symbol,
            'contract_type':contractType,
            'type':type1
        }
        params['sign'] = buildMySign(params,self.__secretkey)
        return httpPost(self.__url,FUTURE_POSITION_4FIX,params)







    
