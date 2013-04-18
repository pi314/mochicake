import time
def flatList (inputList, width):
    maxLength = max([len(i) for i in inputList])
    ret = []
    for i in range(0, len(inputList), width):
        tempList = [j for j in inputList[i:width+i]]
        tempStr = ' '.join(['{0:{width}}'.format(j, width=maxLength) for j in tempList])
        ret.append(tempStr)
    return ret

def getTimeStr ():
    return time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
