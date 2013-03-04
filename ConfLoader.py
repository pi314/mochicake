# -*- coding: utf-8 -*-
import tools
class ConfLoader (object):
    def loadConf (self, confFileName):
        print '載入設定檔...('+confFileName+')'
        args = self.__readConfigFile__(confFileName)
        if args['ERROR'] != []:
            print ''
            print '設定檔語法錯誤:'
            for e in args['ERROR']:
                print 'Line {0}: \033[1;31m{1}\033[m'.format(e[0], e[1])

        if args['WARNING'] != []:
            print ''
            print '警告: 以下參數被覆蓋'
            for e in args['WARNING']:
                print 'Line {0}: \033[1;33m{1}\033[m'.format(e[0], e[1])

        if args['UNKNOWN']:
            print ''
            print '未知的參數:'
            for e in args['UNKNOWN']:
                print 'Line {0}: \033[1;32m{1}\033[m'.format(e[0], e[1])

        if args['ARGS'] != {}:
            print ''
            print '已載入的參數:'
            tempList = []
            for key in args['ARGS']:
                tempList.append(key+':')
                if key == 'PASSWD':
                    tempList.append('********')
                else:
                    tempList.append(args['ARGS'][key])
            for i in tools.flatList(tempList, 2):
                print i

        if args['ERROR'] != []:
            if args['ERROR'] == [[0, 'Configure file does not exist']]:
                self.__genExampleConfFile__(confFileName)
            return False

        if self.__checkLackArguments__(args['ARGS']) != []:
            print '設定檔中缺少必要選項 :'
            for i in lack:
                print i
            return False

        print '設定檔載入成功'
        print ''
        return args['ARGS']
            
    def __readConfigFile__ (self, confFileName):
        ret = {
            'UNKNOWN':[],
            'WARNING':[],
            'ERROR':[],
            'ARGS':{}
        }
        try:
            lineNum = 0
            for line in open(confFileName):
                lineNum = lineNum + 1
                if line[0] == '#':
                    continue
                line = line.strip()
                key, value = line.split(':')
                key = key.upper()
                value = value.strip()

                # 語法錯誤
                if value == '' or key == '':
                    ret['ERROR'].append([lineNum, line])
                    continue

                # 有參數被覆寫
                if key in ret['ARGS']:
                    ret['WARNING'].append([lineNum, key])

                # 未知的參數
                if not key in ['USER', 'PASSWD', 'MASTER', 'BOARD']:
                    ret['UNKNOWN'].append([lineNum, key])

                ret['ARGS'][key] = value

        except IOError:
            ret['ERROR'] = [[0, 'Configure file does not exist']]
        except ValueError as e:
            ret['ERROR'] = [[lineNum, line]]
        return ret

    def __genExampleConfFile__ (self, confFileName):
        print '設定檔不存在, 產生範例設定檔...('+confFileName+')'
        with open(confFileName, 'w') as conf:
            conf.write('#user:\n')
            conf.write('#passwd:\n')
            conf.write('#master:\n')
            conf.write('#board:\n')
            conf.close()
        print '完成, 請先完成設定檔'

    def __checkLackArguments__ (self, args):
        lack = []
        for i in ['USER', 'PASSWD', 'MASTER', 'BOARD']:
            if not i in args:
                lack.append(i)
        return lack

if __name__ == '__main__':
    c = ConfLoader()
    print c.loadConf('MochiCake.conf')
