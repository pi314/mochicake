# -*- coding: utf-8 -*-
import sys
import re
import bsdconv
import telnetlib
import time
import pyte

#board=sys.argv[1]
#user=sys.argv[2]
USER = 'pi'
PASSWD = '72ab8af5'
BOARD = 'P_pi314'

#big5(含uao)，去雙色字，轉utf-8
conv=bsdconv.Bsdconv("ansi-control,byte:big5-defrag:byte,ansi-control|skip,big5:utf-8,bsdconv_raw")
conv.init()

stream = pyte.Stream()
screen = pyte.Screen(80, 24)
screen.mode.discard(pyte.modes.LNM)
stream.attach(screen)

def term_comm(w=None, wait=None):
	"""
	寫入連線、將回傳內容放進虛擬終端機緩衝區、取得目前虛擬終端機的畫面
	"""
	if w!=None:
		conn.write(w)
		if wait:
			s=conn.read_some()
			s=conv.conv_chunk(s)
			stream.feed(s.decode("utf-8"))
	if wait!=False:
		time.sleep(0.1)
		s=conn.read_very_eager()
		s=conv.conv_chunk(s)
		stream.feed(s.decode("utf-8"))
	ret="\n".join(screen.display).encode("utf-8")

	#顯示目前畫面
	sys.stdout.write("\x1b[2J\x1b[H") #清空畫面，將游標移至左上角
	sys.stdout.write(ret)
	time.sleep(1)
	return ret

conn = telnetlib.Telnet("bs2.to")

'''登入'''
while True:
	s = term_comm()
	if s.find('[您的帳號]') != -1:
		term_comm('%s\r' % USER, wait=True)
		break

while True:
	s = term_comm()
	if s.find('[您的密碼]') != -1:
		term_comm('%s\r' % PASSWD, wait=True)
		break

'''跳過進板公佈欄'''
term_comm('  ', wait=True)

'''進入看板'''
term_comm('\x73%s\r' % BOARD, wait=True)

'''打開使用者名單'''
term_comm('\x15', wait=True)

open('fishes', 'a').close()
fishList = []
with open('fishes', 'r') as fishes:
    fishList = [i.strip() for i in fishes]
    print fishList

try:
    '''抓魚'''
    while True:
        s = term_comm('s',wait=True)
        a = s.split("\n")
        index = 3
        while True:
            line = a[index]
            fishID = line[8:20].strip()
            if fishID == USER:
                break
            elif not fishID in fishList:
                '''Got a new fish!'''
                print '\033[1;31m'+fishID+'\033[m'
                fishList.append(fishID)
                fishes = open('fishes', 'a')
                fishes.write(fishID+'\n')
                fishes.close()
            index = index + 1
except KeyboardInterrupt:
    '''左左左'''
    term_comm('\x1b\x5b\x44', wait=True)
    term_comm('\x1b\x5b\x44', wait=True)
    term_comm('\x1b\x5b\x44', wait=True)

    '''登出'''
    term_comm('qqqqqg\rg\rq\r')
    exit()
