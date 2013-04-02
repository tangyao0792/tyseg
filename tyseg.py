#!/usr/bin/
#coding=utf-8

'''
#=============================================================================
#     FileName: tyseg.py
#         Desc: A module for divide chinese words in a sentence.
#       Author: Tang Yao
#        Email: tangyao0792@gmail.com
#     HomePage: 
#      Version: 0.0.1
#   LastChange: 2013-01-22 00:27:18
#      History:
#=============================================================================
'''


from chardet import detect
from math import log
import os
import cPickle
import time


trie = {}

# valic char set
validChar = set()


def build_trie():
    global trie, validChar
    # if cache exists, load cache
    if os.path.exists('tempfile'):
        print 'loading trie from cache....'
        with open('tempfile', 'rb') as fin:
            trie = cPickle.load(fin)
            validChar = cPickle.load(fin)
    else:
        with open('dict.txt', 'rb') as fin:
            # first line total frequent
            total = float(fin.readline())
            lines = fin.read().split('\n')
            for line in lines:
                line = line.split(' ')
                if len(line) >= 2:
                    word = line[0].decode('utf-8')
                    freq = - log(float(line[1]) / (total))
                    root = trie
                    #build trie
                    for c in word:
                        validChar.add(c)
                        if not c in root:
                            root[c] = {}
                        root = root[c]
                    root['freq'] = freq
        # write cache
        with open('tempfile', 'wb') as fout:
            cPickle.dump(trie, fout)
            cPickle.dump(validChar, fout)


def getFreq(word):
    root = trie
    for c in word:
        if c in root:
            root = root[c]
        else:
            return 0
    if not 'freq' in root:
        return 0
    return root['freq']


def cut(line):
    '''This function return a list of words'''
    try:
        line = line.decode('utf-8')
    except:
        pass
    seg = []
    last = 0
    length = len(line)
    for last in range(0, length):
        if line[last] in validChar:
            break
    if last > 0:
        seg.append(line[0: last])
    pos = last
    while pos < length:
        while pos < length:
            if not line[pos] in  validChar:
                break
            pos = pos + 1
        seg = seg + _cut(line[last:pos])
        last = pos
        while pos < length:
            if line[pos] in validChar:
                break
            pos = pos + 1
        if pos > last:
            seg.append(line[last: pos])
        last = pos
    if last < length:
        seg.append(line[last: ])
    return seg


def _cut(line):
    '''This funciton return a list of words
       But all the words should be in the dict
    '''
    n = len(line)
    dp = [0] * n
    # father position
    fa = [-1] * n
    flag = [0] * n
    # dynamic programming
    for i in range(0, min(MAXLENGTH, n)):
        dp[i] = getFreq(line[0: i+1])
    for i in range(0, n):
        for j in range(i+1, i+MAXLENGTH):
            if j == n:
                break
            tmp = getFreq(line[i+1:j+1])
            if tmp == 0:
                continue
            if dp[i] + tmp < dp[j] or dp[j] == 0:
                dp[j] = dp[i] + tmp
                fa[j] = i
    # get divide position
    p = n - 1
    while p != -1:
        flag[p] = 1
        p = fa[p]

    seg = []
    last = ''
    for i in range(0, n):
        last = last + line[i]
        if flag[i] == 1:
            seg.append(last)
            last = ''
    return seg


# the max length of a word
MAXLENGTH = 10
print 'building trie...'
t1 = time.time()
build_trie()
print 'completed...', 'it costs', str(time.time() - t1)[:5], 'seconds'

def loadText(filename):
    text = open(filename).read()
    return cut(text)

# debug
if __name__ == '__main__':
    seg = loadText('test.txt')
    print '/'.join(seg)
