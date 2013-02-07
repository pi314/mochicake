# -*- coding: utf-8 -*-
import sys
import re
import bsdconv
import telnetlib
import time
import pyte

CONST = {}
fishList = []

def loadConf ():
    try:
        unknown = ''
        lineTemp = ''
        with open('MochiCake.conf') as conf:
            for line in conf:
                if line[0] == '#':
                    continue
                lineTemp = line
                key, value = line.split(':')
                key = key.lower()
                value = value.strip()
                if value == '':
                    return 'ConfSyntaxError', lineTemp
                elif key in ['user', 'passwd', 'master', 'board']:
                    CONST[key.upper()] = value
                else:
                    CONST[key] = value
                    unknown += line
            if unknown == '':
                return 'Normal', ''
            else:
                return 'UnknownOption', unknown
    except IOError:
        return 'ConfFileNotExist', 'MochiCake.conf'
    except ValueError as e:
        return 'ConfSyntaxError', lineTemp

def genExampleConfFile ():
    with open('MochiCake.conf', 'w') as conf:
        conf.write('#user:\n')
        conf.write('#passwd:\n')
        conf.write('#master:\n')
        conf.write('#board:\n')
        conf.close()
def checkLackArgument ():
    neceArgs = ['USER', 'PASSWD', 'MASTER', 'BOARD']
    lack = []
    for i in neceArgs:
        if not i in CONST:
            lack.append(i)
    return lack

def checkConf (errState, errMsg):
    if errState == 'Normal':
        pass
    elif errState == 'UnknownOption':
        print 'Unknown option : '
        print errMsg
    elif errState == 'ConfFileNotExist':
        print 'Configuration file not exist, generating example file...'
        genExampleConfFile()
        print 'Done, please complete configuration file.'
        exit()
    elif errState == 'ConfSyntaxError':
        print 'Configuration file syntax error :'
        print errMsg
    lack = checkLackArgument()
    if lack != []:
        print 'Needed argument does not exist in MochiCake.conf:'
        for i in lack:
            print i
        exit()
    print 'Configuration file loaded successfully.'

def term_comm (w=None, wait=None):
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
	#sys.stdout.write("\x1b[2J\x1b[H") #清空畫面，將游標移至左上角
	#sys.stdout.write(ret)
	time.sleep(1)
	return ret

def login(user, passwd):
    print '登入中...'
    s = term_comm().split('\n')
    while True:
        s = term_comm()
        if s.find('[您的帳號]') != -1:
            term_comm('%s\r' % CONST['USER'], wait=True)
            break
    while True:
        s = term_comm()
        if s.find('[您的密碼]') != -1:
            term_comm('%s\r' % CONST['PASSWD'], wait=True)
            break
    '''跳過進板公佈欄'''
    term_comm('    ', wait=True)
    print '完成'

def enterBoard (board):
    print '進入看板 %s' % CONST['BOARD']
    term_comm('\x73%s\r' % CONST['BOARD'], wait=True)
    print '完成'
    loadFishList(board)

def loadFishList (board):
    print '載入記錄 (fishes/%s)...' % CONST['BOARD']
    open('fishes', 'a').close()
    fishList = []
    with open('fishes', 'r') as fishes:
        fishList = [i.strip() for i in fishes]
        print fishList
    print '完成'

def checkNewFish ():
    for line in a[3:]:
        fishID = line[8:20].strip()
        if fishID == CONST['USER']:
            break
        elif not fishID in fishList:
            '''Got a new fish!'''
            print '發現新魚 : \033[1;31m'+fishID+'\033[m'
            fishList.append(fishID)
            fishes = open('fishes', 'a')
            fishes.write(fishID+'\n')
            fishes.close()
def logout ():
    print '登出中...'
    '''左左左'''
    term_comm('\x1b\x5b\x44', wait=True)
    term_comm('\x1b\x5b\x44', wait=True)
    term_comm('\x1b\x5b\x44', wait=True)

    '''登出'''
    term_comm('qqqqqg\rg\rq\r')
    exit()

if __name__ == '__main__' or True:
    errState, errMsg = loadConf()
    checkConf(errState, errMsg)

    #big5(含uao)，去雙色字，轉utf-8
    conv=bsdconv.Bsdconv("ansi-control,byte:big5-defrag:byte,ansi-control|skip,big5:utf-8,bsdconv_raw")
    conv.init()
    stream = pyte.Stream()
    screen = pyte.Screen(80, 24)
    screen.mode.discard(pyte.modes.LNM)
    stream.attach(screen)

    conn = telnetlib.Telnet("bs2.to")

    login(CONST['USER'], CONST['PASSWD'])

    enterBoard(CONST['BOARD'])

    print '打開使用者名單...'
    term_comm('\x15', wait=True)
    print '完成'

    print '開始看魚'
    try:
        '''抓魚'''
        while True:
            s = term_comm('s',wait=True)
            a = s.split("\n")
            checkNewFish()
    except KeyboardInterrupt:
        print '接收到 ^C 按鍵'
        logout()
    exit()
