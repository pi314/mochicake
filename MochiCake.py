#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import argparse
import sys
import re
import bsdconv
import telnetlib
import time
import pyte
import os
import random

import ConfLoader
import tools

class MochiCakeBot (object):
    def __init__ (self):
        self.conv = bsdconv.Bsdconv("ansi-control,byte:big5-defrag:byte,ansi-control|skip,big5:utf-8,bsdconv_raw")
        self.conv.init()
        self.stream = pyte.Stream()
        self.screen = pyte.Screen(80, 24)
        self.screen.mode.discard(pyte.modes.LNM)
        self.stream.attach(self.screen)
        self.state = ''
        self.board = None
        self.lines = []
        self.fishList = []
        self.cmdBuffer = ''
        self.boardFaultTolerance = False

    def setInitialMovement (self):
        self.setState('WATCH')
        self.board = self.ARGS['BOARD']

    def term_comm (self, w=None, wait=None):
        """ 寫入連線、將回傳內容放進虛擬終端機緩衝區、取得目前虛擬終端機的畫面 """
        if w != None:
            self.conn.write(w.decode('utf8').encode('big5'))
            if wait:
                s = self.conn.read_some()
                s = conv.conv_chunk(s)
                stream.feed(s.decode("utf-8"))
        if wait!=False:
            time.sleep(0.1)
            s = self.conn.read_very_eager()
            s = self.conv.conv_chunk(s)
            self.stream.feed(s.decode("utf-8"))

        ret = "\n".join(self.screen.display).encode("utf-8")
        self.lines = ret.split('\n')
        #''' 顯示目前畫面 '''
        #sys.stdout.write("\x1b[2J\x1b[H") #清空畫面，將游標移至左上角
        #sys.stdout.write(ret)
        #time.sleep(1)
        time.sleep(0.1)
        return ret

    def setArguments (self, args):
        self.ARGS = args

    def login (self, station):
        print '嘗試連至 '+station+' ...'
        self.conn = telnetlib.Telnet(station)
        print '成功'
        print '登入中...'
        while True:
            s = self.term_comm()
            if s.find('[您的帳號]') != -1:
                self.term_comm('%s\n' % self.ARGS['USER'])
                break
        while True:
            s = self.term_comm()
            if s.find('[您的密碼]') != -1:
                self.term_comm('%s\n' % self.ARGS['PASSWD'])
                break
        print '跳過進板公佈欄'
        self.term_comm('    ')
        print '完成'

    def setState (self, newState):
        if self.state == newState:
            return
        if newState == 'WATCH':
            s = '看魚~'
        elif newState == 'WAIT_COMMAND':
            s = '待命!'
        elif newState == 'MOVING':
            s = '移動中~'
        elif newState == 'LOGOUT':
            s = '登出中~'
        elif newState == 'COMPLETE':
            s = '完成~'
        else:
            s = '不懂>"<'

        inList = (self.checkPosition() == 'LIST')

        if not inList:
            self.term_comm('\x15')

        print '狀態更改為 '+newState
        print '更改故鄉為 '+s
        self.term_comm('\x06\x03'+s+'\n')
        print '完成'
        self.state = newState

        if not inList:
            self.term_comm('\x1b\x5b\x44')  # 左

    def loadFishList (self):
        print '載入記錄 (fishes/%s)...' % self.board
        if not os.path.exists('fishes'):
            os.mkdir('fishes')
        if not os.path.isdir('fishes'):
            os.rename('fishes', 'fishes.tmp')

        open('fishes/'+self.board, 'a').close()
        self.fishList = []
        with open('fishes/'+self.board, 'r') as fishes:
            self.fishList = [i.split()[0].strip() for i in fishes]
        if len(self.fishList) == 0:
            print '名單為空'
        else:
            for i in tools.flatList(self.fishList, 5):
                print i
        print '完成'

    def checkNewFish (self):
        currentFishList = []
        for line in self.lines[3:]:
            fishID = line[8:20].strip()
            if fishID == self.ARGS['USER']:
                break
            currentFishList.append(fishID)
            if not fishID in self.fishList:
                '''Got a new fish!'''
                print '有魚上勾了！ \033[1;31m'+fishID+'\033[m  ' + tools.getTimeStr()
                self.fishList.append(fishID)
                fishes = open('fishes/'+self.board, 'a')
                fishes.write(fishID + ' ' + tools.getTimeStr() + '\n')
                fishes.close()
        self.fishList = currentFishList

    def logout (self):
        self.setState('LOGOUT')
        time.sleep(1)
        exit()

    def checkPosition (self):
        self.term_comm()
        if self.lines[0].startswith('【網友列表】'):
            return 'LIST'
        elif self.lines[0].startswith('【主功能表】'):
            return 'MAIN'
        elif self.lines[0].startswith('【板主'):
            return 'BOARD'
        elif self.lines[0].startswith('【電子郵件】'):
            return 'MAIL'
        return 'UNKNOWN'

    def gotoMainList (self):
        print '回到主選單'
        while self.checkPosition() != 'MAIN':
            self.term_comm('\x1b\x5b\x44')  # 左
        print '完成'

    def watch (self):
        self.term_comm()

        # 板名不正確
        if not self.boardFaultTolerance and not '\xe3\x80\x8a'+self.board+'\xe3\x80\x8b' in self.lines[0]:
            print '板名不正確，預期目前應在 ' + self.board
            print self.lines[0]
            print ''
            self.gotoMainList()
            print '進入 '+self.board
            self.term_comm('s'+self.board+'\n')
            # 如果進不去
            if '錯誤的看板名稱' in self.lines[12]:
                print '無法進入 ' + self.board
                print '請檢查是否為板名打錯，或是該板為好友板或秘密板'
                exit()
            if not '\xe3\x80\x8a'+self.board+'\xe3\x80\x8b' in self.lines[0]:
                print '警告：板名和設定不符，無法確定是否正確'
                print '預期為 ' + self.board
                print '實際為 ' + self.lines[0]
                self.boardFaultTolerance = True
            print '完成'
            #self.loadFishList()
        
        # 位置不正確
        if not self.checkPosition() == 'LIST':
            print '位置不正確，預期目前應在使用者名單'
            print self.lines[0]
            print ''
            self.gotoMainList()
            self.term_comm('\x15')    #打開使用者名單
            print '開始看魚'
        
        # 刷新使用者名單
        self.term_comm('s')

        listPositionError = False
        while not self.lines[3].startswith('     1'):
            listPositionError = True
            print '使用者名單的位置錯誤，試著回到第一頁'
            for i in self.lines:
                print i
            self.term_comm('2\r')
            for i in self.lines:
                print i

        if listPositionError:
            print '使用者名單的位置已正確，繼續看魚'
            listPositionError = False

        self.checkNewFish()

    def waitCommand (self):
        self.term_comm()
        if not self.checkPosition() == 'LIST':
            self.term_comm('\x15')   #打開使用者名單
        if self.cmdBuffer != '':
            self.runCommand(self.cmdBuffer)

        self.checkNewCommand()

    def work (self):
        while True:
            if self.state == 'WATCH':
                self.watch()

def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', default='MochiCake.conf')
    #parser.add_argument('-h', default='MochiCake.conf')

    CONFIG_FILE_NAME = parser.parse_args(sys.argv[1:]).f

    if CONFIG_FILE_NAME == 'MochiCake.conf':
        print '未指定設定檔，尋找預設設定檔 MochiCake.conf'
    else:
        print '使用設定檔 ' + CONFIG_FILE_NAME

    args = ConfLoader.loadConf(CONFIG_FILE_NAME)
    if args == False:
        print '程式結束'
        exit()
    MochiCake = MochiCakeBot()
    MochiCake.setArguments(args)
    MochiCake.login('bs2.to')
    MochiCake.setInitialMovement()
    MochiCake.work()

if __name__ == '__main__':
    main()
