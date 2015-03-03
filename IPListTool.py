#coding=utf8

import wx
import codecs
import os
import zipfile
from ftplib import FTP
import ftplib

LIST_TYPE_ANDROID = 0
LIST_TYPE_TENCENT = 1
LIST_TYPE_APPSTORE = 2

PATH_IPLIST_ANDROID = "./Config/AndroidSample.txt"
PATH_IPLIST_TENCENT = "./Config/TencentSample.txt"
PATH_IPLIST_APPSTORE = "./Config/AppStoreSample.txt"
PATH_IPLIST_COMMON = "../../CDN/tianlong3D/conf/serverlist/Android_test_IPList.txt"

WORLD_STATE_0=u'顺畅'
WORLD_STATE_1=u'拥挤'
WORLD_STATE_2=u'火爆'
WORLD_STATE_3=u'维护'

WORLD_TYPE_0=u'不推荐'
WORLD_TYPE_1=u'推荐'

SERVERINFO_ADD = 1
SERVERINFO_MODIFY = 2

def MessageNotice(notice):
    dlg = wx.MessageDialog(None, notice, u"Notice", wx.OK)
    dlg.ShowModal()
    dlg.Destroy()

def uploadFTP(uploadFilePath):

    if not os.path.exists(uploadFilePath):
        MessageNotice('upload file not exist:' + uploadFilePath)
        return False
    ftp = FTP()

    #ftp.set_debuglevel(2)

    try:

        print "connectint ftp...."

        ftp.connect('10.127.129.197',2121,1000)

    except ftplib.error_perm:

        MessageNotice('connect ftp error')

        return False

    try:

        print "login ftp....."

        ftp.login('YDTL', 'tl3dzhuanyong')

    except ftplib.error_perm:

        MessageNotice("login error")

        return False

    try:

        print "enter ftp doc"

        ftp.cwd("./")

    except ftplib.error_perm:

        try:

            print "create a doc"

            ftp.mkd(ftpUserName)

            ftp.cwd(ftpUserName)

        except ftplib.error_perm:

            MessageNotice("ftp:can not make dir")

            return False

    uploadFile_hander = open(uploadFilePath, 'rb')

    print "cleaning cur doc"

    curFileList =  ftp.nlst()

    for fileName in curFileList:

        if fileName == os.path.basename(uploadFilePath):

            ftp.sendcmd('DELE ' + fileName)

    print "uploading file " + os.path.basename(uploadFilePath)


    ftp.storbinary("stor " + os.path.basename(uploadFilePath), uploadFile_hander)

    uploadFile_hander.close()

    ftp.quit()

    print "ftp:upload ok"
    return True

def zip_dir(dirname, zipfilename):

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

def generateChannel(svnPath, targetPath, zipPath, channelName):
    file_list = open(channelName + "List.txt")

    print channelName + "List.txt"
    generate_list = []
    for curline in file_list.readlines():
        print curline
        curline = curline.replace("\n","")
        open(targetPath + "/" + curline, "wb").write(
            open(channelName + "Sample.txt", "rb").read())
        open(svnPath + "/" + curline, "wb").write(
            open(channelName + "Sample.txt", "rb").read())

    targetZipName = "./tianlong3D.zip";
    targetFTPName = "./tianlong3D.zip.FTP";
    
    if os.path.exists(targetZipName):
        os.remove(targetZipName)

    if os.path.exists(targetFTPName):
        os.remove(targetFTPName)
        
    zip_dir(zipPath, targetZipName)
    os.rename(targetZipName, targetFTPName)
    return

def GenerateCDNZip(argv):
    argLen = len(argv)

    if(argLen < 2):
        print "need a svn path"
        return

    svnPath = argv[1]
    rootPath = "./"
    
    if(argLen < 3):
        targetPath = argv[2];
        print "need a target path"
        return

    if(argLen < 4):
        print "need a channel name"
        return

    if not os.path.exists(rootPath):
        print "target path not exist"
        return

    #--------------生产目标目录并清空---------------
    targetPath = rootPath + "/target/tianlong3D"
    zipPath = rootPath + "/target"
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)

    targetPath = targetPath + "/conf"
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)

    targetPath = targetPath + "/serverlist"
    if not os.path.exists(targetPath):
        os.makedirs(targetPath)

    for root, dirs, files in os.walk(targetPath, topdown=False):
        for f in files:
            os.remove(os.path.join(root, f))
        
    channelList = []

    for i in range(3, argLen):
        channelList.append(argv[i])
        print argv[i]

    #---------------获取参数------------------
    for channelName in channelList:
        generateChannel(svnPath, targetPath,zipPath, "Config/" + channelName)
    
    #os.system('pause')
    return
    return
class IPListData():
    def LoadFile(self, filepath):
        f = codecs.open(filepath,'r','utf8')
        #取Head结构
        self.head = {}
        for index in range(4):
            self.head[index] = f.readline()
        #取Body结构
        self.body = {}
        index = 0
        while 1:
            templine = f.readline()
            if not templine:
                break
            templine = templine.replace('\r\n','')
            self.body[index] = templine
            index = index + 1
        f.close()
        
    def WriteFile(self, filepath):
        #try:
            f = codecs.open(os.path.join(filepath),'w','utf8')
            #写头部结构
            strlist = []
            for key, value in self.head.iteritems():
                #strlist.append(value)
                strlist.append(value)
            #写Body结构
            for key, value in self.body.iteritems():
                value = value + '\r\n'
                strlist.append(value)
            strlist[len(strlist)-1] = strlist[len(strlist)-1].replace('\r\n','')
            f.writelines(strlist)
        #except:
        #    return False
        #finally:
            f.close()
            return True

class WorldIDFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent,-1,u"IPList工具", size=(300, 130), style = wx.SYSTEM_MENU|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        panel = wx.Panel(self,-1)
        self.iplistData = IPListData()
        self.iplistData.LoadFile(PATH_IPLIST_COMMON)
        BTN_OK = 401
        
        wx.StaticText(panel, -1, u'', (10, 30))
        self.TEXT_DESC = wx.TextCtrl(panel, -1, '', (10, 30), (80,30))

        wx.Button(panel, BTN_OK, u"导入当前WorldID", (100, 30))
        wx.EVT_BUTTON(self, BTN_OK, self.OnOKClick)
        return

    def OnOKClick(self, e):
        curWorldID = self.TEXT_DESC.GetValue()
        if not self.parent.CheckWorldID(curWorldID):
            MessageNotice(u"该WorldID已经存在")
            return

        for key, value in self.iplistData.body.iteritems():
            worldlist = value.split()
            worldID = worldlist[0]
            if worldID == curWorldID:
                self.parent.WorldIDImport(value)
                self.Destroy()
                return
        MessageNotice(u"没有找到该WorldID")
        return
    
class ServerInfoFrame(wx.Frame):
    def __init__(self, parent, mode):
        wx.Frame.__init__(self, parent,-1,u"IPList工具", size=(500, 250), style = wx.SYSTEM_MENU|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
        self.parent = parent
        panel = wx.Panel(self,-1)

 
        CHOICE_STATE=501
        CHOICE_TYPE=502
        BTN_ADD_SERVER = 503
        BTN_MODIFY_SERVER = 504
        #间隔
        TEXT_DISTANCE=20

        CONTROL_Y_START = 10
        CONTROL_Y_END = 80
        
        #下拉
        stateList = [WORLD_STATE_0, WORLD_STATE_1, WORLD_STATE_2, WORLD_STATE_3]
        typeList = [WORLD_TYPE_0, WORLD_TYPE_1]
        self.StateChoice = wx.Choice(panel, CHOICE_STATE, (30, CONTROL_Y_END + TEXT_DISTANCE), choices=stateList)
        self.TypeChoice = wx.Choice(panel, CHOICE_TYPE, (100, CONTROL_Y_END + TEXT_DISTANCE), choices=typeList)
        self.StateChoice.SetSelection(0)   
        self.TypeChoice.SetSelection(0)

        #输入
        wx.StaticText(panel, -1, u'ID', (30, CONTROL_Y_START))
        self.TEXT_ID = wx.TextCtrl(panel, -1, '', (30, CONTROL_Y_START +TEXT_DISTANCE), (50,30))

        
        wx.StaticText(panel, -1, u'描述', (90, CONTROL_Y_START))
        self.TEXT_DESC = wx.TextCtrl(panel, -1, '', (90, CONTROL_Y_START+TEXT_DISTANCE), (80,30))
        
        wx.StaticText(panel, -1, u'服务器名', (180, CONTROL_Y_START))
        self.TEXT_NAME = wx.TextCtrl(panel, -1, '', (180, CONTROL_Y_START+TEXT_DISTANCE), (80,30))
        
        wx.StaticText(panel, -1, u'IP', (270, CONTROL_Y_START))
        self.TEXT_IP = wx.TextCtrl(panel, -1, '', (270, CONTROL_Y_START+TEXT_DISTANCE), (120,30))
        
        wx.StaticText(panel, -1, u'端口', (400, CONTROL_Y_START))
        self.TEXT_PORT = wx.TextCtrl(panel, -1, '', (400, CONTROL_Y_START+TEXT_DISTANCE), (50,30))
        
        wx.StaticText(panel, -1, u'组名', (180, CONTROL_Y_END))
        self.TEXT_GROUP = wx.TextCtrl(panel, -1, '', (180, CONTROL_Y_END+TEXT_DISTANCE), (50,30))
        
        wx.StaticText(panel, -1, u'版本号1', (250, CONTROL_Y_END))
        self.TEXT_VERSION1 = wx.TextCtrl(panel, -1, '', (250, CONTROL_Y_END+TEXT_DISTANCE), (30,30))
        
        wx.StaticText(panel, -1, u'版本号2', (300, CONTROL_Y_END))
        self.TEXT_VERSION2 = wx.TextCtrl(panel, -1, '', (300, CONTROL_Y_END+TEXT_DISTANCE), (30,30))
        
        wx.StaticText(panel, -1, u'版本号3', (350, CONTROL_Y_END))
        self.TEXT_VERSION3 = wx.TextCtrl(panel, -1, '', (350, CONTROL_Y_END+TEXT_DISTANCE), (30,30))
        
        wx.StaticText(panel, -1, u'版本号4', (400, CONTROL_Y_END))
        self.TEXT_VERSION4 = wx.TextCtrl(panel, -1, '', (400, CONTROL_Y_END+TEXT_DISTANCE), (30,30))

        self.listdata = {}

        if mode == SERVERINFO_ADD:
            wx.Button(panel, BTN_ADD_SERVER, u"添加服务器", (210, 170 ))
            wx.EVT_BUTTON(self, BTN_ADD_SERVER, self.OnAddServerClick)
        elif mode == SERVERINFO_MODIFY:
            wx.Button(panel, BTN_MODIFY_SERVER, u"修改", (210, 170 ))
            wx.EVT_BUTTON(self, BTN_MODIFY_SERVER, self.OnModifyServerClick)
        return

    def SetData(self, listdata):
        worlddata = listdata.split()
        self.TEXT_ID.SetValue(worlddata[0])
        self.TEXT_DESC.SetValue(worlddata[1])
        self.TEXT_NAME.SetValue(worlddata[2])
        self.TEXT_IP.SetValue(worlddata[3])
        self.TEXT_PORT.SetValue(worlddata[4].decode('utf8'))
        self.TEXT_GROUP.SetValue(worlddata[7])
        if int(worlddata[5]) == 0:
            self.StateChoice.SetSelection(0)
        elif int(worlddata[5]) == 1:
            self.StateChoice.SetSelection(1)
        elif int(worlddata[5]) == 2:
            self.StateChoice.SetSelection(2)
        elif int(worlddata[5]) == 3:
            self.StateChoice.SetSelection(3)

        if int(worlddata[6]) == 0:
            self.TypeChoice.SetSelection(0)
        elif int(worlddata[6]) == 1:
            self.TypeChoice.SetSelection(1)

        if len(worlddata) > 8:
            self.TEXT_VERSION1.SetValue(worlddata[8].decode('utf8'))
            self.TEXT_VERSION2.SetValue(worlddata[9].decode('utf8'))
            self.TEXT_VERSION3.SetValue(worlddata[10].decode('utf8'))
            self.TEXT_VERSION4.SetValue(worlddata[11].decode('utf8'))

        self.listdata = listdata
        
        return

    def GetData(self):
        worldid = self.TEXT_ID.GetValue()
        if len(worldid) == 0:
            MessageNotice(u"world id none")
            return False

        desc = self.TEXT_DESC.GetValue()
        if len(desc) == 0:
            MessageNotice(u"desc none")
            return False

        name = self.TEXT_NAME.GetValue()
        if len(name) == 0:
            MessageNotice(u"name none")
            return False

        ip = self.TEXT_IP.GetValue()
        if len(ip) == 0:
            MessageNotice(u"ip none")
            return False

        port = self.TEXT_PORT.GetValue()
        if len(port) == 0:
            MessageNotice(u"port none")
            return False

        group = self.TEXT_GROUP.GetValue()
        if len(group) == 0:
            MessageNotice(u"group none")
            return False

        servertype = str(self.TypeChoice.GetSelection())
        if len(servertype) == 0:
            MessageNotice(u"type none")
            return False

        state = str(self.StateChoice.GetSelection())
        if len(state) == 0:
            MessageNotice(u"state none")
            return False

        version1 = self.TEXT_VERSION1.GetValue()
        version2 = self.TEXT_VERSION2.GetValue()
        version3 = self.TEXT_VERSION3.GetValue()
        version4 = self.TEXT_VERSION4.GetValue()

        if len(version1) == 0 and len(version2) == 0 and len(version3) == 0 and len(version4) == 0:
            self.listdata = worldid + '\t' + desc + '\t' + name + '\t'+ ip + '\t'+ port + '\t'+ state + '\t' \
            + servertype + '\t'+ group
            print self.listdata
            return True

        if len(version1) != 0 and len(version2) != 0 and len(version3) != 0 and len(version4) != 0:
            self.listdata = worldid + '\t' + desc + '\t' + name + '\t'+ ip + '\t'+ port + '\t'+ state + '\t' \
            + servertype + '\t'+ group + '\t'+ version1+ '\t'+ version2+ '\t'+ version3+ '\t'+ version4
            print self.listdata
            return True

        return False

    def OnAddServerClick(self, e):
        if not self.GetData():
            MessageNotice(u"数据设置错误，请检查")
            return
        self.parent.AddList(self.listdata)
        self.Destroy()
        return

    def OnModifyServerClick(self,e):
        if not self.GetData():
            MessageNotice(u"数据设置错误，请检查")
            return

        if self.parent.ModifyList(self.listdata):
            self.Destroy()
            return

        MessageNotice(u"修改的记录不存在")
        return

#操作窗口     
class ModifyFrame(wx.Frame):
    def __init__(self, parent):
        FRAME_SIZE_WIDTH    = 700
        FRAME_SIZE_HEIGHT   = 600
        
        POS_X_BTN_START     = 510
        POS_Y_BTN_START     = 10

        LISTBOXE_IPLIST         = 201
        BTN_NEWSERVER_WORLDID   = 203
        BTN_NEWSERVER_SELF      = 204
        BTN_MODIFYSERVER        = 205
        BTN_SAVE                = 206
        
        wx.Frame.__init__(self, parent,-1,u"IPList工具", size=(FRAME_SIZE_WIDTH, FRAME_SIZE_HEIGHT), style = wx.SYSTEM_MENU|wx.MINIMIZE_BOX|wx.CLOSE_BOX|wx.CAPTION|wx.FRAME_FLOAT_ON_PARENT)
        panel = wx.Panel(self,-1)
        self.FileData = IPListData()
        self.listtype = -1
        noneList = []
        self.ListBox = wx.ListBox(panel, 201, (0, 0), (FRAME_SIZE_WIDTH-200, FRAME_SIZE_HEIGHT-50), noneList, wx.LB_SINGLE)

        
        wx.Button(panel, BTN_NEWSERVER_WORLDID, u"通过WorldID增加服务器", (POS_X_BTN_START, POS_Y_BTN_START + 10))
        wx.EVT_BUTTON(self, BTN_NEWSERVER_WORLDID, self.OnNewServerWorldIDClick)
        
        wx.Button(panel, BTN_NEWSERVER_SELF, u"手动配置新服务器", (POS_X_BTN_START, POS_Y_BTN_START + 40))
        wx.EVT_BUTTON(self, BTN_NEWSERVER_SELF, self.OnNewServerSelfClick)
        
        wx.Button(panel, BTN_MODIFYSERVER, u"修改服务器配置", (POS_X_BTN_START, POS_Y_BTN_START + 160))
        wx.EVT_BUTTON(self, BTN_MODIFYSERVER, self.OnModifyServerClick)

        wx.Button(panel, BTN_SAVE, u"保存修改", (POS_X_BTN_START, POS_Y_BTN_START + 260))
        wx.EVT_BUTTON(self, BTN_SAVE, self.OnSaveServerListClick)
        return


    def OnNewServerWorldIDClick(self,e):
        worldFrame = WorldIDFrame(self)
        worldFrame.Show(True)
        return

    def OnNewServerSelfClick(self, e):
        serverInfoFrame = ServerInfoFrame(self,SERVERINFO_ADD)
        serverInfoFrame.Show(True)
        return

    def OnModifyServerClick(self,e):
        
        selectIndex = self.ListBox.GetSelection()
        if selectIndex < 0 or selectIndex >= len(self.FileData.body):
            MessageNotice(u"选择条目错误" + str(selectIndex) + " " + str(len(self.FileData.body)))
            return
        
        serverInfoFrame = ServerInfoFrame(self,SERVERINFO_MODIFY)
        serverInfoFrame.SetData(self.FileData.body[selectIndex])
        serverInfoFrame.Show(True)

        return

    def OnSaveServerListClick(self,e):
        if self.listtype == LIST_TYPE_ANDROID:
            self.FileData.WriteFile(PATH_IPLIST_ANDROID)
        elif self.listtype == LIST_TYPE_TENCENT:
            self.FileData.WriteFile(PATH_IPLIST_TENCENT)
        elif self.listtype == LIST_TYPE_APPSTORE:
            self.FileData.WriteFile(PATH_IPLIST_APPSTORE)
        else:
            return

        self.Destroy()
        return

    def WorldIDImport(self, listdata):
        serverInfoFrame = ServerInfoFrame(self,SERVERINFO_ADD)
        serverInfoFrame.SetData(listdata)
        serverInfoFrame.Show(True)
        return

    def CheckWorldID(self, worldID):
        for key, value in self.FileData.body.iteritems():
            worldlist = value.split()
            if worldlist[0] == worldID:
                return False 
        return True

    def ImportList(self,listType):
        self.listtype = listType
        loadfilepath = ""
        if listType == LIST_TYPE_ANDROID:
            loadfilepath = PATH_IPLIST_ANDROID
        elif listType == LIST_TYPE_TENCENT:
            loadfilepath = PATH_IPLIST_TENCENT
        else: 
            loadfilepath = PATH_IPLIST_APPSTORE
            
        self.FileData.LoadFile(loadfilepath)
        self.UpdateList(-1)
        return

    def ModifyList(self, listdata):
        worlddata = listdata.split()
        for i in range(0, len(self.FileData.body)):
            curBodyData = self.FileData.body[i]
            worldlist = curBodyData.split()
            if(worldlist[0] == worlddata[0]):
                self.FileData.body[i] = listdata
                self.UpdateList(i)
                return True

        return False

    def AddList(self, listdata):
        worlddata = listdata.split()
        if not self.CheckWorldID(worlddata[0]):
            MessageNotice(u"该WorldID已经存在,无法添加")
            return False

        curBodylen = len(self.FileData.body)
        self.FileData.body[curBodylen] = listdata
        self.UpdateList(curBodylen)
        MessageNotice(u"添加成功")
        return True

    def UpdateList(self,selection):
        self.ListBox.Clear()
        for key, value in self.FileData.body.iteritems():
            worldlist = value.split()
            WorldID = worldlist[0]
            WorldDesc = worldlist[1]
            WorldName = worldlist[2]
            WorldState = u''
            if int(worldlist[5]) == 0:
                WorldState = WORLD_STATE_0
            elif int(worldlist[5]) == 1:
                WorldState = WORLD_STATE_1
            elif int(worldlist[5]) == 2:
                WorldState = WORLD_STATE_2
            elif int(worldlist[5]) == 3:
                WorldState = WORLD_STATE_3
            WorldType = u''
            if int(worldlist[6]) == 0:
                WorldType = WORLD_TYPE_0
            elif int(worldlist[6]) == 1:
                WorldType = WORLD_TYPE_1

            GroupName = worldlist[7]
            VersionInfo = u''
            
            if len(worldlist) == 12:
                VersionInfo = worldlist[8] + u"." + worldlist[9] + u"." + worldlist[10] + u"." + worldlist[11]
                
            itemstr = self.AddSpace(WorldID, 10) + self.AddSpace(WorldDesc, 20) + self.AddSpace(WorldName, 20) +\
                      self.AddSpace(WorldState, 10) + self.AddSpace(WorldType, 20) +self.AddSpace(GroupName, 15) + self.AddSpace(VersionInfo, 10)
            self.ListBox.Append(itemstr)

        if selection > 0 and selection < self.ListBox.GetCount():
            self.ListBox.SetSelection(selection)
        else:
            self.ListBox.SetSelection(self.ListBox.GetCount()-1)
        return

    def AddSpace(self, strText, maxlen):
        retText = strText
        addcount = maxlen - len(strText.encode('utf-8'))
        if addcount > 0:
            for i in range(0, addcount):
                retText += ' '
        return retText

#主界面
class MainFrame(wx.Frame):
    
    def __init__(self, parent):
        wx.Frame.__init__(self, None,-1,u"IPList工具", size=(500, 200))
        panel = wx.Panel(self, -1)
        self.app = parent

        POS_X_MODIFY_START = 10
        POS_Y_MODIFY_START = 10

        GAP_Y_BUTTON = 50
        GAP_X_GROUP = 150
    
        BTN_MODIFY_ANDROID = 100
        BTN_MODIFY_TENCENT = 101
        BTN_MODIFY_APPSTORE = 102
        BTN_GENERATE_ZIP = 103
        BTN_UPLOAD = 104
        
        wx.Button(panel, BTN_MODIFY_ANDROID, u"修改安卓混服", (POS_X_MODIFY_START, POS_Y_MODIFY_START))
        wx.Button(panel, BTN_MODIFY_TENCENT, u"修改腾讯服", (POS_X_MODIFY_START, POS_Y_MODIFY_START + GAP_Y_BUTTON))
        wx.Button(panel, BTN_MODIFY_APPSTORE, u"修改正版服", (POS_X_MODIFY_START, POS_Y_MODIFY_START + GAP_Y_BUTTON*2))

        wx.Button(panel, BTN_GENERATE_ZIP, u"生成压缩文件", (POS_X_MODIFY_START + GAP_X_GROUP, POS_Y_MODIFY_START+ GAP_Y_BUTTON))
        wx.Button(panel, BTN_UPLOAD, u"上传FTP", (POS_X_MODIFY_START + GAP_X_GROUP*2, POS_Y_MODIFY_START+ GAP_Y_BUTTON))

        wx.EVT_BUTTON(self, BTN_MODIFY_ANDROID, self.OnModifyAndroidClick)
        wx.EVT_BUTTON(self, BTN_MODIFY_TENCENT, self.OnModifyTencentClick)
        wx.EVT_BUTTON(self, BTN_MODIFY_APPSTORE, self.OnModifyAppStoreClick)

        wx.EVT_BUTTON(self, BTN_GENERATE_ZIP, self.OnGenerateZip)
        wx.EVT_BUTTON(self, BTN_UPLOAD, self.OnUploadFTP)

    def OnModifyAndroidClick(self, e):
        modifyFrame = ModifyFrame(self)
        modifyFrame.ImportList(LIST_TYPE_ANDROID)
        modifyFrame.Show(True)
        return

    def OnModifyTencentClick(self, e):
        modifyFrame = ModifyFrame(self)
        modifyFrame.ImportList(LIST_TYPE_TENCENT)
        modifyFrame.Show(True)
        return

    def OnModifyAppStoreClick(self, e):
        modifyFrame = ModifyFrame(self)
        modifyFrame.ImportList(LIST_TYPE_APPSTORE)
        modifyFrame.Show(True)
        return

    def OnGenerateZip(self, e):
        argv = ['./dist/MakeServerlist.exe', '../../CDN/tianlong3D/conf/serverlist', './' ,'Tencent' ,'AppStore', 'Android']
        GenerateCDNZip(argv);
        return

    def OnUploadFTP(self,e):
        dlg = wx.MessageDialog(None, u"请确认已经完成以下操作：\n1.已经修改服务器配置，并点击过生成压缩文件\n2.将修改过的文件上传至SVN并且检查无误", u"Notice", wx.OK|wx.CANCEL)
        dlg.SetOKCancelLabels(u"确认上传", u"取消")
        ret = dlg.ShowModal()
        if ret == wx.ID_OK:
            if uploadFTP("./tianlong3D.zip.FTP"):
                MessageNotice(u"上传成功")
        dlg.Destroy()
        
        return
        
class MyApp(wx.App):
    def OnInit(self):
        self.mainFrame = MainFrame(self)
        self.SetTopWindow(self.mainFrame)
        self.mainFrame.Show(True)
        MessageNotice(u"请确认已经将运维目录SVN更新到最新在进行操作")
        return True
    

app = MyApp(0)
app.MainLoop()
