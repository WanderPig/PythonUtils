#encoding:utf-8
import os
import sys
import zipfile
from ftplib import FTP
import ftplib
import shutil

reload(sys)
sys.setdefaultencoding('gbk')

#获取调用文件所在目录
curPath = os.getcwd()

tempPath = curPath + "\\temp"

svnLogFile = tempPath + "\\svnLogFile.txt"

configFile = curPath + "\\config.txt"

svnLibPath = "svn://10.127.128.64/tlol/Version/Main"

svnFolderName = curPath + "\\Main"

targetPath = curPath + "\\temp\\target"

versionFilePath = curPath + "\\temp\\AutoUploadVersion.txt"

downloadPath = curPath + "\\download"

downloadVersionPath = downloadPath + "\\AutoUploadVersion.txt"

ftpUserName = "wangdi_yd"

curVersion = "0"

def CopyFile(curFilePath):

	curFindPos = 1;

	targetFullPath = targetPath + "\\" + curFilePath

	while (curFindPos >= 0):

		curFindPos = targetFullPath.find('\\', curFindPos+1, -1)

		if(curFindPos > 0):

			curSubPath = targetFullPath[0:curFindPos]

			if not os.path.exists(curSubPath):

				os.makedirs(curSubPath)

		else:

			if os.path.isdir(curFilePath):

				if not (os.path.exists(curSubPath)):

					os.makedirs(curSubPath)
			else:

				if os.path.isfile(curFilePath):

					open(targetFullPath, "wb").write(open(curFilePath, "rb").read())		

def CleanDir( Dir ):

    if os.path.isdir( Dir ):

        paths = os.listdir( Dir )

        for path in paths:

            filePath = os.path.join( Dir, path )

            if os.path.isfile( filePath ):

                try:

                    os.remove( filePath )

                    print filePath

                except os.error:

                    autoRun.exception( "remove %s error." %filePath )#引入logging

            elif os.path.isdir( filePath ):

                if filePath[-4:].lower() == ".svn".lower():

                    continue

                shutil.rmtree(filePath,True)

    return True

def readVerionFromFile(versionFilePath):
	curSvnVersionFile = open(versionFilePath)

	line = curSvnVersionFile.readline()

	while line:

		findIndex = line.find("vision", 0)

		if (findIndex > 0):

			return line[10:].strip('\n')

		line = curSvnVersionFile.readline()

def uploadFTP(uploadFilePath):

	ftp = FTP()

	#ftp.set_debuglevel(2)

	try:

		print "connectint ftp...."

		ftp.connect('10.7.39.29',888,1000)

	except ftplib.error_perm:

		print 'connect ftp error'

		return

	try:

		print "login ftp....."

		ftp.login('happy', 'happy')

	except ftplib.error_perm:

		print "login error"

		return

	try:

		print "enter ftp doc"

		ftp.cwd(ftpUserName)

	except ftplib.error_perm:

		try:

			print "create a doc"

			ftp.mkd(ftpUserName)

			ftp.cwd(ftpUserName)

		except ftplib.error_perm:

			print "ftp:can not make dir"

			return

	uploadFile_hander = open(uploadFilePath, 'rb')

	uploadVersionFile_hander = open(tempPath + "\\AutoUploadVersion.txt", 'rb')

	print "cleaning cur doc"

	curFileList =  ftp.nlst()

	for fileName in curFileList:

		if(fileName == "AutoUploadVersion.txt" or fileName == os.path.basename(uploadFilePath)):

			ftp.sendcmd('DELE ' + fileName)

	print "uploading file " + os.path.basename(uploadFilePath)

	ftp.storbinary("stor " + "AutoUploadVersion.txt", uploadVersionFile_hander)

	ftp.storbinary("stor " + os.path.basename(uploadFilePath), uploadFile_hander)

	uploadFile_hander.close()

	uploadVersionFile_hander.close()

	ftp.quit()

	print "ftp:upload ok"





def zip_dir(dirname,zipfilename):

    filelist = []

    if os.path.isfile(dirname):

        filelist.append(dirname)

    else :

        for root, dirs, files in os.walk(dirname):

            for name in files:

                filelist.append(os.path.join(root, name))
        
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)

    for tar in filelist:

        arcname = tar[len(dirname):]
        #print arcname
        zf.write(tar,arcname)

    zf.close()

def CopyFileLeft(curFilePath, curzipObj):

	curFindPos = 1;

	targetFullPath = curPath.replace('\\','/') + "/" + curFilePath

	while (curFindPos >= 0):

		curFindPos = targetFullPath.find('/', curFindPos+1, -1)

		if(curFindPos > 0):

			curSubPath = targetFullPath[0:curFindPos]

			if not os.path.exists(curSubPath):

				os.makedirs(curSubPath)

		else:

			open(targetFullPath, "wb").write(curzipObj.read(curFilePath))

def unzip_file(zipfilename, unzipto):

	unziptodir = unzipto.replace('\\','/')

	if not os.path.exists(unziptodir):

		os.mkdir(unziptodir, 0777)

	zfobj = zipfile.ZipFile(zipfilename)

	for name in zfobj.namelist():

		name = name.replace('\\','/')
       
		CopyFileLeft(name, zfobj)


def ReadConfig():

	global svnLibPath
	global ftpUserName
	global curVersion

	try:

		configfile_hander = open(configFile)

		svnLibPath = configfile_hander.readline().strip('\n')

		ftpUserName = configfile_hander.readline().strip('\n')

		curVersion = configfile_hander.readline().strip('\n')

		configfile_hander.close()

		return True;

	except:

		return False;

def UpdateConfig():

	try:

		configfile_hander = open(configFile, 'w')

		configfile_hander.write(svnLibPath + '\n')

		configfile_hander.write(ftpUserName+ '\n')

		configfile_hander.write(curVersion+ '\n')

		configfile_hander.close()

		return True;

	except:

		print "update config fail"

		return False;



def PrepareDocs():

	print "cleaning temp path :" + tempPath

	CleanDir(tempPath)

	if not os.path.exists(tempPath):

		os.makedirs(tempPath)



def UpdateSvn():

	global curVersion

	if os.path.exists(svnFolderName):

		print "svn updating to " + svnFolderName 


		os.system("svn update -r " + curVersion + " " + svnFolderName)

		os.system("svn update " + svnFolderName  + " > " + svnLogFile)

	else:

		print "svn checkout form " + svnLibPath

		os.system("svn checkout " + svnLibPath + " > " + svnLogFile)

	print "check target path"

	if not os.path.exists(targetPath):

		os.makedirs(targetPath)

	print "generate svn version info"

	os.system("svn info " + svnLibPath + " > " + versionFilePath)

	curVersion = readVerionFromFile(versionFilePath)

	print "generate svn log info"

	curSvnLogFile = open(svnLogFile)

	line = curSvnLogFile.readline()

	changeFileList = []

	while line:

		subString = line.split('    ')

		if len(subString) > 1:

			changeFileList.append(subString[1])

		line = curSvnLogFile.readline().strip('\n')

	for changeFilePath in changeFileList:

		curFullPath = curPath + "\\" + changeFilePath

		targetFullPath = targetPath + "\\" + changeFilePath

		if(os.path.exists(curFullPath)):

			print "copying file: " + targetFullPath

			CopyFile(changeFilePath)

		else:

			print  "not found: " + curFullPath
	
def BeginUpload():

	print "reading config"

	if not ReadConfig():

		print "read config file error"

		return

	print curVersion

	PrepareDocs()

	UpdateSvn()

	print "ziping file"

	zip_dir(targetPath, tempPath + "\\" + curVersion + ".zip")

	uploadFTP(tempPath + "\\" + curVersion + ".zip")

	UpdateConfig()

	print "finish"

	os.system("pause")

def BeginDownLoad():

	#PrepareDocs()

	print "checking version file"

	downloadVersion = readVerionFromFile(downloadVersionPath)

	print "checking zip file"

	curZipFilePath = downloadPath + "\\" + downloadVersion + ".zip"

	if not os.path.exists(curZipFilePath):

		print "error ! can not find zip file :path :" + curZipFilePath

		return 

	print "unziping files"

	unzip_file(curZipFilePath, curPath)

	return

if __name__ == '__main__':
	BeginUpload()