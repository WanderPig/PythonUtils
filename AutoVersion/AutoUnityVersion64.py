#!/usr/bin/env python
#coding=utf-8

__author__ = 'WD'

import plistlib
import sys
import re
import os
import time
from mod_pbxproj import XcodeProject
import wdutils

reload(sys)
sys.setdefaultencoding('utf-8')

cur_path = os.getcwd()

#各种文件名
plist_config_filepath = "config_build64.plist"
plist_configsdk_filepath = "config_sdk64.plist"

plistConfig = plistlib.readPlist(cur_path +"/config_build64.plist")
plistConfigSDK = plistlib.readPlist(cur_path +"/config_sdk64.plist")

unity_project_path = plistConfig["ClientPath"]
xcode_baseproject_path = unity_project_path + "/Build/MLDJ_IOS"
server_res_path = unity_project_path + "/../Server"
release_path = unity_project_path + "/Release"
release_path_ios = release_path + "/IOS/"
release_path_server_res = release_path + "/ServerRes"
update_res_path = unity_project_path + "/Release/ResData/StreamingAssets"
update_path_root = unity_project_path + "/Release/ResData"
app_resversion_path = unity_project_path + "/Assets/StreamingAssets/VersionData/ResVersion.txt"
xcode_configfile_path = "/Libraries/GameConfig.h"
buid_type_max = 4

global dic_channel_config
global current_channel_name
global dic_commom_config


def read_config():
    #读取配置文件

    global plistConfig
    global plistConfigSDK
    global dic_commom_config

    plistConfig = plistlib.readPlist(cur_path +"/" + plist_config_filepath)
    if len(plistConfig) == 0:
        return False

    plistConfigSDK = plistlib.readPlist(cur_path +"/" +plist_configsdk_filepath)
    if len(plistConfigSDK) == 0:
        return False

    dic_commom_config = plistConfigSDK["CommonSetting"]

    return len(plistConfig) > 0


def build_unity_ios():

    build_type = int(plistConfig["BuildType"])

    if build_type > buid_type_max:
        print "\nnot build unity"
        return True

    wdutils.DeleteFolder(xcode_baseproject_path)
    wdutils.DeleteFolder(update_path_root)

    if build_type == 1:
        return wdutils.CmdUnityScript(plistConfig["UnityPath"], unity_project_path, "CommandBuild.BuildiOSUpdate")
    elif build_type == 2:
        return wdutils.CmdUnityScript(plistConfig["UnityPath"], unity_project_path, "CommandBuild.BuildiOSRapid")
    elif build_type == 3:
        return wdutils.CmdUnityScript(plistConfig["UnityPath"], unity_project_path, "CommandBuild.BuildiOSUpdateRes")
    elif build_type == 4:
        return wdutils.CmdUnityScript(plistConfig["UnityPath"], unity_project_path, "CommandBuild.BuildiOSUpdateTW")
    elif build_type == 0:
        return wdutils.CmdUnityScript(plistConfig["UnityPath"], unity_project_path, "CommandBuild.BuildiOS")

    print "build not define"
    return False


def update_ios_config(current_project_path):
    # 更新IOS的配置信息

    proj = XcodeProject.Load(current_project_path + '/Unity-iPhone.xcodeproj/project.pbxproj')

    res_download_url = ""
    serverlist_url = ""
    dic_compileflag = {}


    if len(dic_channel_config) == 0 or len(dic_commom_config) == 0:
        print "channel error"
        return False


    #全局设置
    for current_common_config in dic_commom_config:
        print current_common_config
        if current_common_config == 'Frameworks':
            for framwork_need_add in dic_commom_config[current_common_config]:
                proj.add_file('System/Library/Frameworks/' + framwork_need_add + '.framework', parent='Frameworks', tree='SDKROOT')
        elif current_common_config == 'CopyFiles':
            for file_need_copy in dic_commom_config[current_common_config]:
                local_path = cur_path + '/' + file_need_copy
                target_path = current_project_path + '/' + dic_commom_config[current_common_config][file_need_copy]
                open(target_path, "wb").write(open(local_path, "rb").read())
        elif current_common_config == 'SettingFlags':
            for current_xcode_setting in dic_commom_config[current_common_config]:
                proj.change_setting_flag(current_xcode_setting, dic_commom_config[current_common_config][current_xcode_setting])
        elif current_common_config == 'SDKs':
            for sdk_need_add in dic_commom_config[current_common_config]:
                proj.add_folder(cur_path + "/SDK64/" + sdk_need_add, parent='Class')


    for current_config in dic_channel_config:
        if current_config == 'ResDownloadUrl':
            res_download_url = dic_channel_config[current_config] + "_" + plistConfig["GameVersion"] +  "_" + plistConfig["ProgramVersion"]

        elif current_config == 'SettingFlags':
            for current_xcode_setting in dic_channel_config[current_config]:
                proj.change_setting_flag(current_xcode_setting, dic_channel_config[current_config][current_xcode_setting])

        elif current_config == 'SDKs':
            for sdk_need_add in dic_channel_config[current_config]:
                proj.add_folder(cur_path + "/SDK64/" + sdk_need_add, parent='Class')

        elif current_config == 'dylibs':
            for lib_need_add in dic_channel_config[current_config]:
                proj.add_file('usr/lib/' + lib_need_add + '.dylib', parent='Frameworks', tree='SDKROOT')

        elif current_config == 'Frameworks':
            for framwork_need_add in dic_channel_config[current_config]:
                proj.add_file('System/Library/Frameworks/' + framwork_need_add + '.framework', parent='Frameworks', tree='SDKROOT')

        elif current_config == 'CopyFiles':
            for file_need_copy in dic_channel_config[current_config]:
                local_path = cur_path + '/' + file_need_copy
                target_path = current_project_path + '/' + dic_channel_config[current_config][file_need_copy]
                open(target_path, "wb").write(open(local_path, "rb").read())

        elif current_config == "OtherLDFlags":
            for other_flags in dic_channel_config[current_config]:
                proj.add_other_ldflags(other_flags)

        elif current_config == 'ServerListUrl':
            serverlist_url = dic_channel_config[current_config]

        elif current_config == "CopyFolders":
            for folder_need_copy in dic_channel_config[current_config]:
                local_path = cur_path + '/' + folder_need_copy
                target_path = current_project_path + '/' + dic_channel_config[current_config][folder_need_copy]
                wdutils.CopyFolder(local_path, target_path)
        elif current_config == "compiler_flags":
            current_compile_dic = {}
            for curflag in dic_channel_config[current_config]:
                curList = []
                for curfile in dic_channel_config[current_config][curflag]:
                    curList.append(curfile)
                if len(curList) > 0:
                    current_compile_dic[curflag] = curList
            if len(current_compile_dic) > 0:
                dic_compileflag["compiler_flags"] = current_compile_dic
        elif current_config == "IconFolder":
            wdutils.CopyFolder(cur_path + '/' +"Icons64/" +dic_channel_config[current_config] + "/Unity-iPhone", current_project_path + "/Unity-iPhone")
        elif current_config == "CodeSighEntitlements":
            entitlementPath =  os.path.abspath(cur_path + "/" + dic_channel_config[current_config])
            print entitlementPath
            proj.change_setting_flag("CODE_SIGN_ENTITLEMENTS", entitlementPath)

    if len(dic_compileflag) > 0:
        proj.apply_mods(dic_compileflag)


    proj.save()

    xcode_gameconfig_file = open(current_project_path + xcode_configfile_path, 'r')
    lines = xcode_gameconfig_file.readlines()
    xcode_gameconfig_file.close()

    xcode_gameconfig_file = open(current_project_path + xcode_configfile_path, 'w')
    for curline in lines:

        a = re.sub('''#define GAME_VERSION''',
                   '''#define GAME_VERSION ''' +
                   plistConfig["GameVersion"] + '''//''', curline)

        a = re.sub('''#define PROGRAM_VERSION''',
                   '''#define PROGRAM_VERSION ''' +
                   plistConfig["ProgramVersion"] + '''//''', a)

        a = re.sub('''#define GM_ENABLE''',
                   '''#define GM_ENABLE ''' +
                   plistConfig["EnableGM"] + '''//''', a)

        a = re.sub('''#define UPDATE_ENABLE''',
                   '''#define UPDATE_ENABLE ''' +
                   plistConfig["EnableUpdate"] + '''//''', a)

        a = re.sub('''#define DEBUGMODE_ENABLE''',
                   '''#define DEBUGMODE_ENABLE ''' +
                   plistConfig["EnableDebugMode"] + '''//''', a)

        a = re.sub('''#define SHARECENTER_ENABLE''',
                   '''#define SHARECENTER_ENABLE ''' +
                   plistConfig["EnableShareCenter"] + '''//''', a)

        a = re.sub('''#define RES_DOWNLOAD_URL''',
                   '''#define RES_DOWNLOAD_URL @"''' +
                   res_download_url + '''" //''', a)

        a = re.sub('''#define CHANNEL_STRING''',
                   '''#define CHANNEL_STRING @"''' +
                   current_channel_name + '''" //''', a)

        a = re.sub('''#define CHANNEL_ID''',
                   '''#define CHANNEL_ID @"''' +
                   dic_channel_config["ChannelID"] + '''" //''', a)

        if dic_channel_config.has_key("cyAppKey"):
            a = re.sub('''#define CY_APP_KEY''',
                       '''#define CY_APP_KEY @"''' +
                       dic_channel_config["cyAppKey"] + '''" //''', a)

        if dic_channel_config.has_key("cyAppSecret"):
            a = re.sub('''#define CY_APP_SECRET''',
                       '''#define CY_APP_SECRET @"''' +
                       dic_channel_config["cyAppSecret"] + '''" //''', a)

        if dic_channel_config.has_key("ThirdAppID"):
            a = re.sub('''#define THIRD_APP_ID''',
                       '''#define THIRD_APP_ID @"''' +
                       dic_channel_config["ThirdAppID"] + '''" //''', a)

        if dic_channel_config.has_key("ThirdAppKey"):
            a = re.sub('''#define THIRD_APP_KEY''',
                       '''#define THIRD_APP_KEY @"''' +
                       dic_channel_config["ThirdAppKey"] + '''" //''', a)

        if dic_channel_config.has_key("TalkingDataKey"):
            a = re.sub('''#define TALKINGDATA_KEY''',
                       '''#define TALKINGDATA_KEY @"''' +
                       dic_channel_config["TalkingDataKey"] + '''" //''', a)

        if dic_channel_config.has_key("TalkingDataChannel"):
            a = re.sub('''#define TALKINGDATA_CHANNEL''',
                       '''#define TALKINGDATA_CHANNEL @"''' +
                       dic_channel_config["TalkingDataChannel"] + '''" //''', a)

        a = re.sub('''#define SERVERLIST_URL''',
                   '''#define SERVERLIST_URL @"''' +
                   serverlist_url + '''" //''', a)

        a = re.sub('''#define UPDATEAPP_URL''',
                   '''#define UPDATEAPP_URL @"''' +
                   dic_channel_config["UpdateAppUrl"] + '''" //''', a)

        a = re.sub('''#define MEIDA_CHANNEL''',
                   '''#define MEIDA_CHANNEL @"''' +
                   dic_channel_config["MediaChannel"] + '''" //''', a)

        a = re.sub('''#define GENGXIN_URL''',
                   '''#define GENGXIN_URL @"''' +
                   dic_channel_config["GengxinUrl"] + '''" //''', a)

        a = re.sub('''#define COMMON_GENGXIN_URL''',
                   '''#define COMMON_GENGXIN_URL @"''' +
                   dic_commom_config["CommonUpdateUrl"] + '''" //''', a)

        a = re.sub('''#define UMANALYTICS_KEY''',
                   '''#define UMANALYTICS_KEY @"''' +
                   dic_commom_config["UMAnalyitcsKey"] + '''" //''', a)

        if dic_channel_config.has_key("AppDetailURL"):
            a = re.sub('''#define APP_DETAIL_URL''',
                   '''#define APP_DETAIL_URL @"''' +
                   dic_channel_config["AppDetailURL"] + '''" //''', a)

        a = re.sub('''#endif''',"", a)

        xcode_gameconfig_file.writelines(a)

    cyUrlScheme = '''""'''
    if dic_channel_config.has_key("CyUrlScheme"):
        cyUrlScheme = dic_channel_config["CyUrlScheme"]
    xcode_gameconfig_file.writelines('''\n#define URLSCHEME_CY @"''' + cyUrlScheme + '''"''')

    arrayCommonFlags = dic_commom_config["Flags"]
    arrayChannelFlags = dic_channel_config["Flags"]
    
    for curFlag in arrayCommonFlags:
        xcode_gameconfig_file.writelines("\n#define " + curFlag)
    
    for curFlag in arrayChannelFlags:
         xcode_gameconfig_file.writelines("\n#define " + curFlag)

    xcode_gameconfig_file.writelines("\n\n#endif")
    xcode_gameconfig_file.close()

    generatePlistPath = current_project_path + "/Info.plist"
    open(generatePlistPath, "wb").write(open(dic_channel_config["PlistFile"], "rb").read())
    curInfoPlist = plistlib.readPlist(generatePlistPath)

    versionLastString = ".0.0"
    if "AppStore" in dic_channel_config["PlistFile"]:
        versionLastString = ".0"

    curInfoPlist["CFBundleShortVersionString"] = plistConfig["GameVersion"] + "." + plistConfig["ProgramVersion"] + versionLastString
    curInfoPlist["CFBundleVersion"] = plistConfig["GameVersion"] + "." +  plistConfig["ProgramVersion"]+ versionLastString
    plistlib.writePlist(curInfoPlist, generatePlistPath)
    print generatePlistPath
    return True


def get_timestamp():
    return time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time()))


def generate_res_zip(zipFilePath):
    #生成客户端资源zip

    print "version path" + update_path_root + "/ResVersion.txt"

    version_file = file(update_path_root + "/ResVersion.txt", "w")
    version_file.write(plistConfig["ResVersion"])
    version_file.close()

    #app_version_file = file(app_resversion_path, "w")
    #app_version_file.write(dic_channel_config["ResVersion"])
    #app_version_file.close()

    wdutils.ZipFolder(update_path_root, zipFilePath)

    return


def generate_iospacket(curBuildRootPath):
    # 更新IOS工程配置

    projectsPath = curBuildRootPath + "/Projects"
    archivePath = curBuildRootPath + "/Archives"
    packetPath = curBuildRootPath  + "/Packets"

    current_project_path = projectsPath  + "/" + current_channel_name
    current_archive_path = archivePath  + "/" + current_channel_name + ".xcarchive"
    current_packet_path = packetPath  + "/" + current_channel_name + ".ipa"

    wdutils.DeleteFolder(current_project_path)
    wdutils.CopyFolder(xcode_baseproject_path, current_project_path)

    print "\nstep:update xcode setting......"
    if not update_ios_config(current_project_path):
        print "update ios config error stop"
        return

    wdutils.DeleteFile(current_archive_path)
    print "\nstep:archive xcode project"
    if not wdutils.CmdXcodeArchive(current_project_path + "/Unity-iPhone.xcodeproj" , "Unity-iPhone", current_archive_path):
        return

    wdutils.DeleteFile(current_packet_path)
    print "\nstep:generate ipa"
    if not wdutils.CmdXcodeExportArchive(current_archive_path, current_packet_path,dic_channel_config["iOSCodeSign"]):
        return

    return


def generateBuildDir(curRootPath):

    wdutils.MakePath(curRootPath + "/Res/")
    wdutils.MakePath(curRootPath + "/Projects/")
    wdutils.MakePath(curRootPath + "/Archives/")
    wdutils.MakePath(curRootPath + "/Packets/")
    return curRootPath


def main():

    print "current working dir:" + plistConfig["ClientPath"]

    # 读取配置文件
    print "\nstep:reading config...."
    if not read_config():
        print "read config fail"
        return

    build_type = int(plistConfig["BuildType"])



    # 编译UNITY工程
    print "\nstep:building unity project......"
    if not build_unity_ios():
        print "build unity project fail"
        return

    # 建立目录结构,Build/timestamp
    curBuildDir = xcode_baseproject_path + "/../" + get_timestamp()
    isUnityBuild = build_type <= buid_type_max
    generateBuildDir(curBuildDir)

    if isUnityBuild:
        # 打包备份服务器资源
        print "\nstep:ziping server res...."
        wdutils.ZipFolder(server_res_path, curBuildDir + "/Res/server.zip")
        # 生成更新文件
        if build_type == 1 or build_type == 3:
            print "\nstep:ziping client res....."
            resZipPath = curBuildDir + "/Res/" + plistConfig["ResVersion"] + "/clientRes.zip"
            wdutils.DeleteFile(resZipPath)
            generate_res_zip(resZipPath)

        if build_type == 3:
            return

        # 打包备份服务器资源
        print "\nperpare xcode project"
        wdutils.DoCmd("open " + xcode_baseproject_path + "/Unity-iPhone.xcodeproj")
        time.sleep(20)
        wdutils.DoCmd('''killall TERM Xcode''')
        time.sleep(5)

    #配置具体工程
    for current_buildchannel in plistConfig["ChannelList"]:
        #遍历所有要打包的渠道，读取渠道配置
        isFindChannel = False
        print current_buildchannel
        for current_channel in plistConfigSDK["ChannelConfig"]:
            if current_channel == current_buildchannel:
                global  dic_channel_config
                global  current_channel_name
                dic_channel_config = plistConfigSDK["ChannelConfig"][current_channel]
                current_channel_name = current_buildchannel
                isFindChannel = True

        if not isFindChannel:
            print current_buildchannel + " not found"
            continue

        #根据当前配置打包
        print "build channel:" + current_channel_name
        generate_iospacket(curBuildDir)


    print "\nfinish"
    return


if __name__ == '__main__':
    main()
