# -*- coding: utf-8 -*-
import sys
import re
import bsdconv
import telnetlib
import time
import pyte
import os
import random

CONST = {}
fishList = []
lastCmd = ''
state = 'WAIT_COMMAND'
lastState = ''
position = ''

def loadConf ():
    print '載入設定檔...'
    global CONST
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
    print '設定檔不存在, 產生範例設定檔...(MochiCake.conf)'
    with open('MochiCake.conf', 'w') as conf:
        conf.write('#user:\n')
        conf.write('#passwd:\n')
        conf.write('#master:\n')
        conf.write('#board:\n')
        conf.close()
    print '完成, 請先完成設定檔'

def checkLackArgument ():
    global CONST
    lack = []
    for i in ['USER', 'PASSWD', 'MASTER', 'BOARD']:
        if not i in CONST:
            lack.append(i)
    return lack

def checkConf (errState, errMsg):
    print '檢查設定檔語法...'
    if errState == 'Normal':
        pass
    elif errState == 'UnknownOption':
        print '未知的選項 :'
        print errMsg
    elif errState == 'ConfFileNotExist':
        genExampleConfFile()
        exit()
    elif errState == 'ConfSyntaxError':
        print '設定檔語法錯誤 :'
        print errMsg
    lack = checkLackArgument()
    if lack != []:
        print '設定檔中缺少必要選項 :'
        for i in lack:
            print i
        exit()
    print '設定檔載入成功'

def prepareConf ():
    errState, errMsg = loadConf()
    checkConf(errState, errMsg)

def term_comm (w=None, wait=None):
	""" 寫入連線、將回傳內容放進虛擬終端機緩衝區、取得目前虛擬終端機的畫面 """
	if w != None:
		conn.write(w.decode('utf8').encode('big5'))
		if wait:
			s = conn.read_some()
			s = conv.conv_chunk(s)
			stream.feed(s.decode("utf-8"))
	if wait!=False:
		time.sleep(0.1)
		s = conn.read_very_eager()
		s = conv.conv_chunk(s)
		stream.feed(s.decode("utf-8"))
	ret="\n".join(screen.display).encode("utf-8")

	#''' 顯示目前畫面 '''
	#sys.stdout.write("\x1b[2J\x1b[H") #清空畫面，將游標移至左上角
	#sys.stdout.write(ret)
	time.sleep(1)
	return ret

def login():
    global CONST
    print '登入中...'
    s = term_comm().split('\n')
    while True:
        s = term_comm()
        if s.find('[您的帳號]') != -1:
            term_comm('%s\r' % CONST['USER'])
            break
    while True:
        s = term_comm()
        if s.find('[您的密碼]') != -1:
            term_comm('%s\r' % CONST['PASSWD'])
            break
    '''跳過進板公佈欄'''
    term_comm('    ')
    term_comm('\x15')   #打開使用者名單
    print '完成'

def enterBoard ():
    global position
    print '離開使用者名單'
    term_comm('\x1b\x5b\x44')

    print '進入看板 %s' % position
    term_comm('\x73%s\n' % position)

    print '完成'
    loadFishList()

    print '打開使用者名單...'
    term_comm('\x15')
    print '完成'

def flatList (inputList, width):
    maxLength = max([len(i) for i in inputList])
    ret = []
    for i in range(0, len(inputList), width):
        tempList = [j for j in inputList[i:width+i]]
        tempStr = ' '.join(['{0:{width}}'.format(j, width=maxLength) for j in tempList])
        ret.append(tempStr)
    return ret

def loadFishList ():
    global fishList
    global position
    print '載入記錄 (fishes/%s)...' % position

    if not os.path.exists('fishes'):
        os.mkdir('fishes')
    if not os.path.isdir('fishes'):
        os.rename('fishes', 'fishes.tmp')

    open('fishes/'+position, 'a').close()
    fishList = []
    with open('fishes/'+position, 'r') as fishes:
        fishList = [i.strip() for i in fishes]
    if len(fishList) == 0:
        print '名單為空'
    else:
        for i in flatList(fishList, 5):
            print i
    print '完成'

def checkNewFish (lines):
    global CONST
    global fishList
    for line in lines[3:]:
        fishID = line[8:20].strip()
        if fishID == CONST['USER']:
            break
        elif not fishID in fishList:
            '''Got a new fish!'''
            print '發現新魚 : \033[1;31m'+fishID+'\033[m'
            fishList.append(fishID)
            fishes = open('fishes/'+position, 'a')
            fishes.write(fishID+'\n')
            fishes.close()

def listFishes ():
    global CONST
    global position
    global fishList
    showState('準備中')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    print '進入寄信選單'
    term_comm('m\nm\n')
    print '完成'

    print '收信人:'+CONST['MASTER']
    term_comm(CONST['MASTER']+'\n') #收信人
    term_comm('[名單] '+position+'\n')
    
    for i in flatList(fishList, 5):
        term_comm(i+'\n')
    
    term_comm('\x18\n\n\n')         #寄信，備份就擺著吧
    term_comm('\x15')    #打開使用者名單
    enterBoard()
    showState('完成')

def seenFish (s):
    global fishList
    global position
    print 'Master 查詢 ' + s + ' @ ' + position
    if s in fishList:
        response('是的, 有看過喔~')
    else:
        # 沒有完全相同的 ID
        for i in fishList:
            if i.startswith(s) or i.endswith(s):
                response('沒有看過，不過有看過 '+i+' 喔')
                return
        response('不, 沒有看過~')
def removeFish (s):
    global fishList
    global position
    f = lambda x : not x == s
    fishList = [i for i in fishList if f(i)]
    with open('fishes/'+position, 'w') as fishes:
        fishes.write('\n'.join(fishList)+'\n')

def showState (s):
    global lastState
    if lastState != s:
        print '更改故鄉為 '+s
        term_comm('\x06\x03'+s+'\n')
        print '完成'
        lastState = s

def response (s):
    term_comm('\x12'+s+'\n\n')
    # 把水球按掉，不然畫面不會變
    term_comm('s')
    return

def processCommandFromMaster (cmd, lines):
    global state, position, lastCmd
    print '接收到指令 '+cmd
    if state == 'WAIT_COMMAND':
        if cmd in ['list']:
            response('收到~ 再次確認~')
            state = 'WAIT_CONFIRM'
        elif cmd == 'hello':
            response('哈囉>ω<')
        elif cmd == 'ok':
            showState('看魚~');
        elif cmd == 'where':
            response(position);
        elif cmd.startswith('seen '):
            seenFish(cmd[5:])
        elif cmd == 'logout':
            logout()
        elif cmd == 'reload':
            enterBoard()
        elif cmd.startswith('remove '):
            removeFish(cmd[7:])
            response('刪除 '+s+' 完成~')
        elif cmd.startswith('goto '):
            response('前往 '+cmd[5:]+'!')
            position = cmd[5:]
            enterBoard()
            response('到達!')
        else:
            response('不懂>"<')
    elif state == 'WAIT_CONFIRM':
        if cmd == 'ok':
            if lastCmd == 'logout':
                logout()
            elif lastCmd == 'list':
                listFishes()
            response('動作完成~')
            state = 'WAIT_COMMAND'
        elif cmd == 'no':
            response('動作取消~')
            state = 'WAIT_COMMAND'
        else:
            response('不懂>"<')
            pass
    lastCmd = cmd

def processCommandFromShell (cmd):
    if cmd == 'cmds':
        print '''
cmds     : 列出所有指令
exit     : MochiCake 繼續看魚
logout   : MochiCake 登出
position : 印出 MochiCake 所在板名 (pos)
list     : 列出當前魚名單 (ls)
where    : 印出當前所在板名
reload   : 重新載入該板的魚名單
remove   : 從名單中刪除一些魚 (rm)
           remove fish1 fish2 ...
'''
    elif cmd == 'logout':
        logout()
        exit()
    elif cmd == '' or cmd == 'exit':
        print '無輸入指令，繼續看魚'
        return 'BACK_SEE_FISH'
    elif cmd == 'position' or cmd == 'pos':
        print '目前位置 : '+position
    elif cmd == 'list' or cmd == 'ls':
        for i in flatList(fishList, 5):
            print i
    elif cmd == 'where':
        print position
    elif cmd == 'reload':
        loadFishList()
    elif cmd.startswith('remove '):
        for i in cmd.split()[1:]:
            removeFish(i)
            print '刪除 '+i+'完成'
    else:
        print '未知的指令'
    return 'CONTINUE'

def checkCommand (lines):
    global CONST
    for line in lines[3:]:
        fishID = line[8:20].strip()
        #找到 master, 看有沒有指令
        if fishID == CONST['MASTER']:
            words = line.split()
            if words[-2] == 'MochiCake':
                return True
            else:
                return False
            break
    # 沒有找到 MASTER
    return False

def logout ():
    showState('登出中~')
    exit()
    print '登出中...'
    '''左左左左左'''
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')
    term_comm('\x1b\x5b\x44')

    print '已回到主選單'

    '''登出'''
    try:
        term_comm('g\ng\nq\n')
    except EOFError:
        pass
    exit()

def watch ():
    global CONST
    showState('看魚~')
    while True:
        scr = term_comm()
        lines = scr.split("\n")
        if lines[-1].startswith('★'+CONST['MASTER']):
            return
        scr = term_comm('s',wait=True)
        lines = scr.split("\n")
        if lines[-1].startswith('★'+CONST['MASTER']):
            return
        while not lines[3].startswith('     1'):
            print '使用者名單的位置錯誤，試著回到第一頁'
            term_comm('1\n')
        checkNewFish(lines)
        if checkCommand(lines):
            return 

def waitCommand ():
    global CONST
    showState('待命!')
    while True:
        scr = term_comm()
        lines = scr.split("\n")
        if lines[-1].startswith('★'+CONST['MASTER']):
            # 有水球！
            cmd = ' '.join(lines[-1].split()[1:])
            if cmd == 'end':
                return
            processCommandFromMaster(cmd, lines)
    
def commandLineInterface ():
    print '進入指令模式，輸入 cmds 查看指令列表'
    while True:
        try:
            cmd = raw_input('MochiCake > ').strip()
            result = processCommandFromShell(cmd)
            if result == 'BACK_SEE_FISH':
                return
        except KeyboardInterrupt:
            print '再度接收到 ^C 按鍵，登出'
            logout()
    
def main ():
    global conv, stream, screen, conn
    global position, CONST
    prepareConf()

    #big5(含uao)，去雙色字，轉utf-8
    conv = bsdconv.Bsdconv("ansi-control,byte:big5-defrag:byte,ansi-control|skip,big5:utf-8,bsdconv_raw")
    conv.init()
    stream = pyte.Stream()
    screen = pyte.Screen(80, 24)
    screen.mode.discard(pyte.modes.LNM)
    stream.attach(screen)

    conn = telnetlib.Telnet("bs2.to")

    login() #登入並進入使用者名單

    position = CONST['BOARD']
    enterBoard()
    while True:
        try:
            # 查看使用者名單，直到 Master 提出指示 (MochiCake)
            watch()
            waitCommand()
        except KeyboardInterrupt:
            print '\n接收到 ^C 按鍵，MochiCake 暫停'
            commandLineInterface()
    exit()

if __name__ == '__main__' or True:
    main()
