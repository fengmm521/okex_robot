#!/usr/bin/python
# -*- coding: utf-8 -*-
#用于访问OKCOIN 期货REST API

import os
import sys
import time

def getDataPID():
    f = open('datapsid.txt','r')
    pid = f.read()
    f.close()
    return pid

def main():
    bitmexDataPID = getDataPID()
    print('bitmexDataPID=%s'%(bitmexDataPID))
    while True:
        time.sleep(1)
        if os.path.exists('socketerro.txt'):
            bitmexDataPID = getDataPID()
            cmd = '/bin/kill %s'%(bitmexDataPID)
            print(cmd)
            os.system(cmd)
            time.sleep(0.1)
            if os.path.exists('datapsid.txt'):
                os.remove('datapsid.txt')
            time.sleep(0.3)
            cmd = '/bin/sh startDataServer.sh'
            print('restart Data Server')
            print(cmd)
            os.system(cmd)
            time.sleep(10)

if __name__ == '__main__':
    main()





    
