#coding=utf8

import os
import sys
import commands

tips =  "fail [-f ipa file path] [-d new ipa name] [-p mobileprovision path] [-s codesign string] "
def DoCmd(cmd):
    (status, output) = commands.getstatusoutput(cmd)
    if status != 0:
        print "\nfail:" + output
    return status == 0

def main():
    argvLen = len(sys.argv)
    if argvLen != 9:
        print tips
        return

    srcFilePath = ""
    distFileName = ""
    provFilePath = ""
    codeSign = ""
    for i in range(0,4):
        if sys.argv[2*i + 1] == "-f":
            srcFilePath = sys.argv[2*(i+1)]
        elif sys.argv[2*i + 1] == "-d":
            distFileName = sys.argv[2*(i+1)]
        elif sys.argv[2*i + 1] == "-p":
            provFilePath = sys.argv[2*(i+1)]
        elif sys.argv[2*i + 1] == "-s":
            codeSign = sys.argv[2*(i+1)]
        else:
            print "argv error: " + sys.argv[2*i + 1] + "\n" + tips
            return

    if len(srcFilePath) == 0 or len(distFileName) == 0 or len(provFilePath) == 0 or len(codeSign) == 0:
        print "argv num error"+ "\n" + tips
        return


    targetDir = os.path.dirname(srcFilePath)

    workPath = os.path.join(targetDir , "wdcodesign_tmp")

    targetFilePath = os.path.join(targetDir , distFileName)

    if os.path.exists(targetFilePath):
        print targetFilePath + " already exist, please change the name"
        return
        
    if os.path.exists(workPath):
        DoCmd("rm -rf " + workPath)

    if not DoCmd("unzip " + srcFilePath + " -d " + workPath):
        return

    payloadPath = os.path.join(workPath, "Payload")

    appName = ""
    for f in os.listdir(payloadPath):
        appName = f
    
    srcAppPath = os.path.join(payloadPath, appName)

    codesignDocPath = os.path.join(srcAppPath, "_CodeSignature")

    if not DoCmd("rm -rf " + codesignDocPath):
        return

    if not DoCmd("cp " + provFilePath + " " + os.path.join(srcAppPath, "embedded.mobileprovision")):
        return

    resourceRulePath = os.path.join(srcAppPath, "ResourceRules.plist")

    if os.path.exists(resourceRulePath):
        if not DoCmd('''/usr/bin/codesign -f -s "''' + codeSign + '''" --resource-rules ''' + resourceRulePath + " " + srcAppPath):
            return
    else:
        if not DoCmd('''/usr/bin/codesign -f -s "''' + codeSign + '''" ''' + srcAppPath):
            return

    if not DoCmd("cd " + workPath + " && zip -r " + targetFilePath + " *"):
        return

    print "generate success to path:" + targetFilePath
    return


if __name__=='__main__':
    main()
  