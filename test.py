#!/usr/bin/python
# -*- coding: utf-8 -*-
# encoding: utf-8
#客户端调用，用于查看API返回结果

import time
if __name__ == '__main__':
    # a = ['a','b','c']
    # x = ','.join(a)
    # a = ' 345 abc  jjj   '
    # x = ' '.join(a.split())
    # print x
    # a = str(int(time.time() - 100*60*60)*1000)
    # print(a)
    d = {0.1:1,0.2:3}
    dks = d.keys()
    print(d)
    d.pop(dks[0])
    print(d)
    print(d.keys())
