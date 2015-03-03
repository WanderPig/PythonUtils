#encoding:utf-8
import os
import sys


sourcePath = sys.argv[1]
distPath = sys.argv[2]
txtFiles = os.listdir(sourcePath)


def ReadTxtNames():
	retNames = [];
	for filename in txtFiles:
		pos = filename.rfind("txt")
		if pos != -1 and filename[0] != '~':
			retNames.append(filename)
	return retNames;

def ConvertTxt(filename):
	curTxt = open(sourcePath + filename, "r")
	curTxtByte = curTxt.read()
	curTxt.close()
	generateTxt = open(distPath + filename, "w+")
	#print curTxtByte
	generateTxt.write(getEncodeStr(curTxtByte))
	generateTxt.close()
	return
	
def getEncodeStr(word,val='utf-8'):
    if os.name=='nt':
        wtemp=u'wtemp'
        if type(word)==type(wtemp):
            disvalue=word
        else:
            disvalue=unicode(word, 'mbcs')
        if val.lower()!='utf-8':
            try:
                tdv=disvalue.encode(val)
            except:
                tdv=disvalue.encode('utf-8')
        else:
            tdv=disvalue.encode(val)
        return tdv
    else:
        return word

def BeginConvert():
	sourceTxts = ReadTxtNames();
	for filename in sourceTxts:
		ConvertTxt(filename)

BeginConvert();
		
	
