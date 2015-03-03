#coding=utf8

import os
import commands
import time
from Tkinter import *
import Tkinter, tkFileDialog

xcodeProjPath = ""
provisionPath = ""
schemeName = ""
codesignName = ""
#主界面
msgValue = ""

def get_timestamp():
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))

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


class MainFrame(Tkinter.Frame):

  def __init__(self, root):

    Tkinter.Frame.__init__(self, root)

    Tkinter.Button(self, text=u'选择工程文件', command=self.chooseXCodeProjectPath).grid(row = 0, sticky=W)
    Tkinter.Button(self, text=u'生成IPA', command=self.OnGenerateIPA).grid(row = 1, sticky=W)


    self.labelProjPath = Label(self, text = xcodeProjPath)
    self.labelProjPath.grid(row = 0, column = 1, sticky=W,columnspan = 2)

    self.logText = Tkinter.Text(self)
    self.logText.insert(END, u'选择XCODE工程路径')
    self.logText.bind("<KeyPress>", lambda e : "break")
    self.logText.grid(row = 5, columnspan = 2, column = 0)


  def AddMsg(self, msg):
      self.logText.insert(END, "\n" + msg)
      print msg

  def chooseXCodeProjectPath(self):
        global xcodeProjPath
        options = {}
        options['defaultextension'] = '.xcodeproj'
        options['filetypes'] = [('xcode project', '.xcodeproj')]
        options['initialdir'] = os.getcwd()
        options['parent'] = root
        options['title'] = u'选择工程路径'
        xcodeProjPath= tkFileDialog.askopenfilename(**options)
        self.labelProjPath['text'] = xcodeProjPath
        self.logText.delete(0.0, END)
        print xcodeProjPath


  def OnGenerateIPA(self):
        options = {}
        options['initialdir'] = os.getcwd()
        options['mustexist'] = False
        options['parent'] = root
        options['title'] = u'选择输入路径'
        userChoosePath = tkFileDialog.askdirectory(**options)
        if len(userChoosePath) == 0:
            return

        self.logText.delete(0.0, END)
        self.AddMsg(u"打包工程路径：" + xcodeProjPath)
        self.AddMsg("generating app please wait....")
        curScheme = schemeName
        if len(curScheme) == 0:
            curProjname = os.path.basename(xcodeProjPath)
            curScheme = curProjname.replace(".xcodeproj", "")
            print curScheme

        curPath = userChoosePath + "/" + get_timestamp()
        MakePath(curPath)
        curArchive = curPath + '/' + curScheme + ".xcarchive"
        archiveCMD = "xcodebuild -project '" + xcodeProjPath + '''' -scheme "''' + curScheme + '''" archive -archivePath ''' + curArchive
        packetCMD = "xcodebuild -exportArchive -exportFormat ipa -archivePath " + curArchive + " -exportPath " + curPath + '/' + curScheme + '.ipa' + ''' -exportWithOriginalSigningIdentity '''

        self.AddMsg("generating archive....")

        (status, output) = commands.getstatusoutput(archiveCMD)
        if status != 0:
            self.AddMsg("\ncmd fail:\n" + output)
            return

        self.AddMsg("generating ipa....")

        (status, output) = commands.getstatusoutput(packetCMD)

        if status != 0:
            self.AddMsg("\ncmd fail:\n" + output)
            return
        else:
            self.AddMsg("Build Success: file output path: " + curPath)


if __name__=='__main__':
  root = Tkinter.Tk()
  MainFrame(root).grid()
  root.mainloop()