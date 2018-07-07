#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-05-24 15:13:31
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$
#创建SocketServerTCP服务器：
import os,sys
import bitmextrade

from sys import version_info  
if version_info.major < 3:
    import SocketServer as socketserver
else:
    import socketserver

import socket
import json

myname = socket.getfqdn(socket.gethostname())
myaddr = socket.gethostbyname(myname)

print('selfip:%s'%(myaddr))
host = str(myaddr)


port = 9102
addr = (host,port)


tradetool = None


class Servers(socketserver.StreamRequestHandler):
    def handle(self):
        global tradetool
        print('got connection from ',self.client_address)
        while True:
            try:  
                data = self.request.recv(1024)
            except EOFError:  
                print('接收客户端错误，客户端已断开连接,错误码:')
                print(EOFError )
                break
            except:  
                print('接收客户端错误，客户端已断开连接')
                break
            if not data: 
                break

            print('data len:%d'%(len(data)))
            print("RECV from ", self.client_address)
            print(data)
            dicdata = json.loads(data)
            tradetool.onTradeMsg(dicdata)

            # self.request.send('aaa')

def startServer():
    server = socketserver.ThreadingTCPServer(addr,Servers,bind_and_activate = False)
    server.allow_reuse_address = True   #设置IP地址和端口可以不使用客户端连接等待，并手动绑定服务器地址和端口，手动激活服务器,要不然每一次重启服务器都会出现端口占用的问题
    server.server_bind()
    server.server_activate()
    print('server started:')
    print(addr)
    server.serve_forever()
    
def main():
    global tradetool
    tradetool = bitmextrade.Future()

    startServer()

#测试
if __name__ == '__main__':
    main()
    
    
