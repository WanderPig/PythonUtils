#!/usr/bin/env python
#coding=utf-8

__author__ = 'WD'

import sys
import os
from xml.dom import minidom
from hashlib import md5


reload(sys)
sys.setdefaultencoding('utf-8')

cur_path = os.getcwd()

def read_resinfo_file(file_path):

    doc = minidom.parse(file_path)
    root = doc.documentElement

    list_fileinfo = root.getElementsByTagName("FileInfo")
    dic = {}

    for node_fileinfo in list_fileinfo:
        path = node_fileinfo.getElementsByTagName("path")[0].childNodes[0].nodeValue
        md5 = node_fileinfo.getElementsByTagName("md5")[0].childNodes[0].nodeValue
        size = node_fileinfo.getElementsByTagName("size")[0].childNodes[0].nodeValue
        level = node_fileinfo.getElementsByTagName("level")[0].childNodes[0].nodeValue
        dic[path] = {"path": path, "md5": md5, "size": size, "level": level}

    return dic


def generate_resinfo_files(info_dic, path_output):

    doc = minidom.Document()
    doc.appendChild(doc.createComment("mllbb update file"))
    file_root = doc.createElement("FileList")
    doc.appendChild(file_root)

    for current_key in info_dic.keys():
        file_info = doc.createElement("FileInfo")

        file_path = doc.createElement("path")
        file_path.appendChild(doc.createTextNode(current_key))
        file_info.appendChild(file_path)

        file_md5 = doc.createElement("md5")
        file_md5.appendChild(doc.createTextNode(info_dic[current_key]["md5"]))
        file_info.appendChild(file_md5)

        file_size = doc.createElement("size")
        file_size.appendChild(doc.createTextNode(info_dic[current_key]["size"]))
        file_info.appendChild(file_size)

        file_level = doc.createElement("level")
        file_level.appendChild(doc.createTextNode(info_dic[current_key]["level"]))
        file_info.appendChild(file_level)

        file_root.appendChild(file_info)

    xml_file = file(path_output, "w")
    xml_file.write(doc.toprettyxml())
    xml_file.close()


def get_md5(file_path):
    m = md5()
    a_file = open(file_path, 'rb')
    m.update(a_file.read())
    a_file.close()
    return m.hexdigest()


def get_res_file(top_path, rel_path):
    return (cur_path + '/' + top_path + '/StreamingAssets/' + rel_path).strip('\n').strip('\r')


def main():
    try:
        file_config = open("CopyResConfig.txt", 'rb')
        path_new_res = file_config.readline().strip('\n').strip('\r')
        path_target_res = file_config.readline().strip('\n').strip('\r')

        lines_config = file_config.readlines()
        file_config.close()

        dic_new_res = {}
        for cur_line in lines_config:
            cur_line = cur_line.strip('\n').strip('\r')
            newfile_fullpath = get_res_file(path_new_res, cur_line)
            dic_new_res[cur_line] = {"path": cur_line, "md5": get_md5(newfile_fullpath), "size": str(os.path.getsize(newfile_fullpath))}

        path_target_updateinfo = cur_path + '/' + path_target_res + "/update.info"
        path_new_updateinfo = cur_path + '/' + path_new_res + "/update.info"

        dic_target_info = read_resinfo_file(path_target_updateinfo)
        dic_new_info = read_resinfo_file(path_new_updateinfo)

        for cur_dic in dic_new_res:
            if dic_new_res.has_key(cur_dic):
                dic_target_info[cur_dic] = {"md5": dic_new_info[cur_dic]['md5'], "size": dic_new_info[cur_dic]['size'], "path": dic_new_info[cur_dic]['path'], "level": dic_new_info[cur_dic]['level']}
            else:
                print "cur file not exist in new info file" + cur_dic

        for cur_dic in dic_new_res:
            open(get_res_file(path_target_res, cur_dic), "wb").write(open(get_res_file(path_new_res, cur_dic), "rb").read())

        generate_resinfo_files(dic_target_info, path_target_updateinfo)
        os.system("pause")
    except Exception, e:
        print e
        os.system("pause")
        raise

if __name__ == '__main__':
    main()