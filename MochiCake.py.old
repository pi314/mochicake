# -*- coding: utf-8 -*-
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

    def getArguments (self, args):
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

        inList = self.lines[0].startswith('【網友列表】')

        if not inList:
            self.term_comm('\x15')

        print '狀態更改為 '+newState
        print '更改故鄉為 '+s
        self.term_comm('\x06\x03'+s+'\n')
        print '完成'
        self.state = newState

        if not inList:
            self.term_comm('\x1b\x5b\x44')  # 左

    def setMovement (self, movement):
        self.movement = movement

    def nextMovement (self):
        return self.movement

    def goWatch (self, dest=None):
        if dest == None:
            dest = self.board
        self.__enterBoard__(dest)
        self.__startWatch__()

    def __enterBoard__ (self, dest):
        while True:
            try:
                print '回到主選單'
                while self.__checkPosition__() != 'MAIN':
                    self.term_comm('\x1b\x5b\x44')  # 左
                print '進入 '+dest
                self.setState('MOVING')
                self.board = dest
                self.term_comm('s%s\n' % self.board)
                if '錯誤的看板名稱' in self.lines[15]:
                    print '錯誤: '+dest+' 無法進入'
                    if dest == self.ARGS['BOARD']:
                        print '程式結束'
                        exit()
                    else:
                        print '回到預設板: '+self.ARGS['BOARD']
                        self.__enterBoard__(self.ARGS['BOARD'])
                        return
                print '完成'
                self.__loadFishList__()
                return
            except KeyboardInterrupt:
                print '在 enterBoard 中按下 ^C'
                self.CLI()

    def __loadFishList__ (self):
        print '載入記錄 (fishes/%s)...' % self.board
        if not os.path.exists('fishes'):
            os.mkdir('fishes')
        if not os.path.isdir('fishes'):
            os.rename('fishes', 'fishes.tmp')

        open('fishes/'+self.board, 'a').close()
        self.fishList = []
        with open('fishes/'+self.board, 'r') as fishes:
            self.fishList = ' '.join([i.strip() for i in fishes]).split()
        if len(self.fishList) == 0:
            print '名單為空'
        else:
            for i in tools.flatList(self.fishList, 5):
                print i
        print '完成'

    def __startWatch__ (self):
        while True:
            try:
                print '開始看魚'
                self.setState('WATCH')
                self.term_comm('\x15')   #打開使用者名單
                listPositionError = False
                while True:
                    if not self.__checkPosition__() == 'LIST':
                        while not self.__checkPosition__() == 'MAIN':
                            self.term_comm('\x1b\x5b\x44')  # 左
                        self.term_comm('\x15')              # 打開使用者名單

                    if self.lines[-1].startswith('★'+self.ARGS['MASTER']):
                        cmd = ' '.join(self.lines[-1].split()[1:])
                        self.waitCommand(cmd)
                        self.term_comm('s')

                    # 刷新使用者名單
                    self.term_comm('s')

                    if self.lines[-1].startswith('★'+self.ARGS['MASTER']):
                        cmd = ' '.join(self.lines[-1].split()[1:])
                        self.waitCommand(cmd)
                        self.term_comm('s')

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

                    self.__checkNewFish__()
                    if self.__checkCommand__():
                        self.waitCommand(cmd)
                        self.term_comm('s')
            except KeyboardInterrupt:
                print '在 startwatch 中按下 ^C'
                self.CLI()

    def __checkNewFish__ (self):
        for line in self.lines[3:]:
            fishID = line[8:20].strip()
            if fishID == self.ARGS['USER']:
                break
            elif not fishID in self.fishList:
                '''Got a new fish!'''
                print '發現新魚 : \033[1;31m'+fishID+'\033[m'
                self.fishList.append(fishID)
                fishes = open('fishes/'+self.board, 'a')
                fishes.write(fishID+'\n')
                fishes.close()

    def __checkCommand__ (self):
        for line in self.lines[3:]:
            fishID = line[8:20].strip()
            #找到 master, 看有沒有指令
            if fishID == self.ARGS['MASTER']:
                words = line.split()
                if words[-2] == 'MochiCake':
                    return True
                else:
                    return False
                break
        # 沒有找到 MASTER
        return False

    def waitCommand (self, command=None):
        self.setState('WAIT_COMMAND')
        self.term_comm()
        if not self.lines[0].startswith('【網友列表】'):
            self.term_comm('\x15')   #打開使用者名單
        if command != None:
            self.__processCommandFromMaster__(command)
        self.term_comm('s')
        print '進入 while loop'

        while True:
            self.term_comm()
            if self.lines[-1].startswith('★'+self.ARGS['MASTER']):
                # 有水球!
                print '指令'
                cmd = ' '.join(self.lines[-1].split()[1:])
                if cmd == 'end':
                    print 'end 指令'
                    self.setMovement('WATCH')
                    self.setState('WATCH')
                    return
                self.__processCommandFromMaster__(cmd)
                self.term_comm('s')     # 把水球按掉

    def __processCommandFromMaster__ (self, cmd):
        print '接收到指令 ['+cmd+']'
        if cmd == 'logout':
            self.logout()
        elif cmd == 'hello':
            self.__water__(self.ARGS['MASTER'], '哈囉>ω<')
        elif cmd == 'list':
            self.__mailListToMaster__()
        elif cmd == 'where':
            self.__water__(self.ARGS['MASTER'], '現在在 '+self.board+' 唷~')
        elif cmd.startswith('goto '):
            self.__enterBoard__(cmd[5:])
            self.term_comm('\x15')   #打開使用者名單
            self.setState('COMPLETE')
            time.sleep(1)
            self.setState('WAIT_COMMAND')
        else:
            self.__water__(self.ARGS['MASTER'], '不懂>"<')

    def __water__ (self, target, message):
        print '開始試著丟水球給 '+target
        if not self.__checkPosition__() == 'LIST':
            self.term_comm('\x15')   #打開使用者名單

        for line in self.lines[3:]:
            targetID = line[8:20].strip()
            if targetID == target:
                print '找到 ' + target
                fishNum = line[0:6].strip()
                print '試著送出訊息 '+message
                self.term_comm(fishNum+'\n')
                self.term_comm('w'+message+'\n\n')
                break

    def CLI (self):
        print 'CLI'
        print 'Not implement yet'
        exit()
        pass

    def logout (self):
        self.setState('LOGOUT')
        time.sleep(1)
        exit()

    def __checkPosition__ (self):
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
    def __mailListToMaster__ (self):
        self.setState('MOVING')
        while (self.__checkPosition__() != 'MAIN'):
            self.term_comm('\x1b\x5b\x44')  # 左
        print '已回到主選單'
        print '進入寄信選單'
        self.term_comm('m\n')
        if (self.__checkPosition__() != 'MAIL'):
            print '位置錯誤，預期在郵件選單，卻在 '+self.__checkPosition__()
            term_comm('\x15')    #打開使用者名單
            return
        self.term_comm('m\n')           # 寄信~
        print '完成'
        print '收信人: '+self.ARGS['MASTER']
        self.term_comm(self.ARGS['MASTER']+'\n')    # 收信人
        self.term_comm('[名單] '+self.board+'\n')   # 主旨
        s = '\n'.join(tools.flatList(self.fishList, 5))
        self.term_comm(s)
        self.term_comm('\x18\n\n\n')         # 存檔
        self.goWatch(self.board)
        self.setState('COMPLETE')
        pass

def main ():
    c = ConfLoader.ConfLoader()
    MochiCake = MochiCakeBot()
    args = c.loadConf('MochiCake.conf')
    if args == False:
        print '程式結束'
        exit()
    MochiCake.getArguments(args)
    MochiCake.login('bs2.to')

    MochiCake.setMovement('WATCH')
    MochiCake.board = MochiCake.ARGS['BOARD']
    while True:
        nm = MochiCake.nextMovement()
        if nm == 'WATCH':
            MochiCake.goWatch()
        elif nm == 'WAIT_COMMAND':
            MochiCake.waitCommand()

if __name__ == '__main__':
    main()
