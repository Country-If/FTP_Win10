#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
from ftplib import FTP
from time import strftime


__author__ = "Maylon"


# ftp连接
def ftp_connect(ip_addr, port, username, password):
    """
    参数：
        ip_addr：ip地址
        port：端口号
        username：用户名
        password：密码
    """
    ftp = FTP()
    try:
        print("正在连接 %s" % ip_addr)
        ftp.connect(ip_addr, port)  # 连接FTP服务器
        print("成功连接 %s" % ip_addr)
        print("正在登录...")
        ftp.login(username, password)  # 登录
        print("登录成功")
        return ftp
    except Exception as e:
        print("%s", e)
        return ""       # 连接失败，返回""


# 判断远程文件和本地文件大小是否一致
def is_same_size(ftp, local_file, remote_file):
    """
    参数:
        ftp：FTP()创建的对象
        local_file：本地文件
        remote_file：远程文件
    """
    # 获取远程文件的大小
    try:
        remote_file_size = ftp.size(remote_file)
    except Exception as e:
        print("%s" % e)
        remote_file_size = -1
    # 获取本地文件的大小
    try:
        local_file_size = os.path.getsize(local_file)
    except Exception as e:
        print("%s" % e)
        local_file_size = -2
    # 比较文件大小，大小相等返回True，否则返回False
    if remote_file_size == local_file_size:
        result = True
    else:
        result = False
    return result


# 文件上传
def upload_file(ftp, local_file, remote_file):
    """
    参数：
        ftp：FTP()创建的对象
        local_file：本地文件
        remote_file：远程文件
    """
    if not os.path.isfile(local_file):      # 判断本地文件是否存在
        print('%s 不存在' % local_file)
        return
    buf_size = 10240        # 设置缓冲区大小
    file_handler = open(local_file, 'rb')
    ftp.storbinary('STOR %s' % remote_file, file_handler, buf_size)
    file_handler.close()
    # 判断文件大小是否相等，不相等则重新上传
    if is_same_size(ftp, local_file, remote_file):
        print('上传 %s' % local_file + " 成功!")
    else:
        upload_dir(ftp, local_file, remote_file)


# 上传整个目录下的文件
def upload_dir(ftp, local_path, remote_path):
    """
        参数：
            ftp：FTP()创建的对象
            local_path：本地目录
            remote_path：远程目录
        """
    # 打开远程目录，目录不存在则创建
    try:
        ftp.cwd(remote_path)
    except Exception:
        ftp.mkd(remote_path)
        ftp.cwd(remote_path)        # 目录创建后切换到远程目录下
    # 切换到本地目录，在FTP递归创建目录和上传文件
    try:
        os.chdir(local_path)    # 切换到本地目录
        file_list = os.listdir(os.getcwd())      # 获取文件列表
        for file_name in file_list:
            # 判断列表中各项是文件还是目录
            if not os.path.isdir(file_name):    # 若是文件，直接上传
                upload_file(ftp, file_name, file_name)
            else:   # 若是目录，在远程创建目录，递归上传
                upload_dir(ftp, file_name, file_name)
                # 上传后切换到上一级目录
                os.chdir("../..")
                ftp.cwd("..")
    except Exception as e:
        print("Error: " + str(e))


# 主函数
def ftp_upload(ftp, local_dir, remote_dir):
    """
    参数：
        ftp：FTP()创建的对象
    """
    if not os.path.exists(local_dir):        # 若上传路径不存在则提示错误信息
        print("上传失败")
        print("上传路径: " + local_dir + " 不存在")
        print("请重新选择正确的上传路径")
        return
    upload_dir(ftp, local_dir, remote_dir)       # 上传目录下的文件


if __name__ == '__main__':
    Port = 21  # 端口号默认为21
    ip = "10.20.30.40"      # 目标IP地址
    Username = "username"      # 用户名
    Password = "password"      # 密码
    FObj = ftp_connect(ip, Port, Username, Password)  # 连接FTP，获取FTP对象
    # FTP.encoding = "gbk"        # 传输中文需要更改编码
    local_upload_dir = ".//upload"      # 上传目录，选定在项目的upload目录下，该路径必须存在
    remote = strftime("%Y%m%d")     # 远端目录名字以日期命名
    if FObj != "":       # 连接成功
        ftp_upload(FObj, local_upload_dir, remote)       # 测试FTP连接时只需注释掉ftp_upload()方法
        FObj.close()     # 结束FTP服务
