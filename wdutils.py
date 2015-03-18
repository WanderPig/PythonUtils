#coding=utf-8
import os
import zipfile
import commands
from hashlib import md5

__author__ = 'WD'

#覆盖拷贝文件夹
def CopyFolder(source_dir, target_dir):
    for f in os.listdir(source_dir):
        source_file = os.path.join(source_dir, f)
        target_file = os.path.join(target_dir, f)

        if os.path.isfile(source_file):
            #创建目录
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            open(target_file, "wb").write(open(source_file, "rb").read())

        if os.path.isdir(source_file):
            CopyFolder(source_file, target_file)
    return


#为目标文件创造所需路径
def MakePath(targetPath):
    curFindPos = 1
    targetFullPath = targetPath.replace('\\','/')

    while curFindPos >= 0:
        curFindPos = targetFullPath.find('/', curFindPos+1)
        if curFindPos >= 0:
            curSubPath = targetFullPath[0:curFindPos]
            if not os.path.exists(curSubPath):
                os.makedirs(curSubPath)
    return


# 删除整个文件夹
def DeleteFolder(path):
    if not os.path.exists(path):
        return

    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for folder in dirs:
            os.rmdir(os.path.join(root, folder))

    os.rmdir(path)
    return

def DeleteFile(filePath):
    if os.path.isfile(filePath):
        os.remove(filePath)
    return

# 删除文件夹里的所有文件
def CleanFolder(path):
    if not os.path.exists(path):
        return

    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        for folder in dirs:
            os.rmdir(os.path.join(root, folder))
    return


# 压缩文件夹
def ZipFolder(folderPath, zipFilePath):

    filelist = []

    if os.path.isfile(folderPath):
        filelist.append(folderPath)
    else :
        for root, dirs, files in os.walk(folderPath):
            for name in files:
                filelist.append(os.path.join(root, name))

    MakePath(zipFilePath)
    zf = zipfile.ZipFile(zipFilePath, "w", zipfile.zlib.DEFLATED)

    for tar in filelist:
        arcname = tar[len(folderPath):]
        #print arcname
        zf.write(tar,arcname)

    zf.close()

    return


# 解压文件夹
def UnzipFile(zipFilePath, exportPath):

    unziptodir = exportPath.replace('\\','/')

    zfobjs = zipfile.ZipFile(zipFilePath)

    for curFilePath in zfobjs.namelist():
        curFilePath = curFilePath.replace('\\','/')
        targetFilePath = unziptodir + '/' + curFilePath
        MakePath(targetFilePath)
        open(unziptodir + '/' + curFilePath, "wb").write(zfobjs.read(curFilePath))

    return


# 获取MD5值
def GetMD5(file_path):
    m = md5()
    a_file = open(file_path, 'rb')
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()

#执行命令，如果错误，打印错误代码
def DoCmd(cmd):
    print "\nexecute command:" + cmd
    (status, output) = commands.getstatusoutput(cmd)
    if status == 0:
        print "\ncmd success!"
    else:
        print "\ncmd fail:" + output
    return status == 0


# 编译
def CmdXcodeListProj(projPath):
    return DoCmd("xcodebuild -list -project '" + projPath + "'")

# 打包
def CmdXcodeArchive(projPath, scheme, archivePath):
    return DoCmd("xcodebuild -project '" + projPath + '''' -scheme "''' + scheme + '''" archive -archivePath ''' + archivePath)

# 生成IPA
def CmdXcodeExportArchive(archivePath, exportPath, provisioningProfile):
    return DoCmd("xcodebuild -exportArchive -exportFormat ipa -archivePath " + archivePath + " -exportPath " + exportPath + ''' -exportSigningIdentity "''' +provisioningProfile+ '''"''')


def CmdXcodeBuild(projPath):
    return DoCmd("xcodebuild -project '" + projPath + "/Unity-iPhone.xcodeproj'  -configuration 'Release' -target 'Unity-iPhone'")


def CmdXcodeGenIpa(projPath, appName, exportPath, codeSign):
    return DoCmd("/usr/bin/xcrun -sdk iphoneos PackageApplication -v '" + projPath+ "/build/" + appName + "' -o '" + exportPath  + "'" + ''' －－sign "''' + codeSign + '''"''')

def CmdUnityScript(unityPath, projPath, method):
    return DoCmd(unityPath + " -batchmode -quit -projectPath " + projPath + " -executeMethod " + method)


#常用命令
#sys.argv 获取命令行参数
#os.sep 路径分隔符
#os.path.exists 文件是否存在
#os.path.dirname 文件所在文件夹
