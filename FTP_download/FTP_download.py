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


# 文件下载
def download_file(ftp, local_file, remote_file):
    """
    参数：
        ftp：FTP()创建的对象
        local_file：本地文件
        remote_file：远程文件
    """
    # 判断远端文件是否存在
    if remote_file in ftp.nlst():
        pass
    else:
        print(remote_file + "不存在")      # 若远端文件不存在则打印错误信息
        return
    buf_size = 10240
    # 判断本地文件是否存在
    if not os.path.exists(local_file):
        with open(local_file, 'wb') as f:
            ftp.retrbinary('RETR %s' % remote_file, f.write, buf_size)
        # 判断文件大小是否相等，不相等则重新下载
        if is_same_size(ftp, local_file, remote_file):
            print("%s 下载成功" % remote_file)
        else:
            download_file(ftp, local_file, remote_file)
    else:
        # 如果本地文件已存在，但是不完整，则重新下载
        if not is_same_size(ftp, local_file, remote_file):
            with open(local_file, 'wb+') as f:
                ftp.retrbinary('RETR %s' % remote_file, f.write, buf_size)
            # 下载后再次判断文件大小是否相等
            if is_same_size(ftp, local_file, remote_file):
                print("%s 下载成功" % remote_file)
            else:
                download_file(ftp, local_file, remote_file)
        else:
            print("%s 已存在" % remote_file)


# 下载整个目录下的文件
def download_dir(ftp, remote_path):
    """
    参数：
        ftp：FTP()创建的对象
        remote_path：远程目录
    """
    # 如果目录不存在则创建目录
    if not os.path.exists(remote_path):
        os.mkdir(remote_path)
    os.chdir(remote_path)  # 切换到下载目录
    try:
        ftp.cwd(remote_path)  # 切换到远程目录
    except Exception:
        print("%s 不存在" % remote_path)
    file_list = ftp.nlst()      # 获取下载文件列表
    print("准备下载的文件列表：" + str(file_list))
    for file_name in file_list:
        # 判断列表各项为目录或是文件
        try:        # 是目录，递归下载目录
            ftp.cwd(file_name)      # 判断是否为目录，若是目录则切换到目录下，否则出现异常
            ftp.cwd("..")       # 切换进目录后需要返回上一级
            download_dir(ftp, file_name)        # 递归下载目录
            # 下载后切换到上一级目录
            ftp.cwd("..")
            os.chdir("../..")
        except Exception:       # 是文件，直接下载
            download_file(ftp, file_name, file_name)


# 主函数
def ftp_download(ftp, local_dir, remote_dir):
    """
    参数：
        ftp：FTP()创建的对象
    """
    if not os.path.exists(local_dir):      # 若下载路径不存在则创建目录
        os.mkdir(local_dir)
    os.chdir(local_dir)        # 切换到下载目录
    download_dir(ftp, remote_dir)       # 下载目录下的文件


if __name__ == '__main__':
    Port = 21  # 端口号默认为21
    ip = "10.20.30.40"      # 目标IP地址
    Username = "username"      # 用户名
    Password = "password"      # 密码
    FTP = ftp_connect(ip, Port, Username, Password)  # 连接FTP
    # FTP.encoding = "gbk"        # 传输中文需要更改编码
    local_download_dir = "D://TestFTP//download"      # 下载目录
    remote = strftime("%Y%m%d")     # 远端目录名字以日期命名
    if FTP != "":       # 连接成功
        ftp_download(FTP, local_download_dir, remote)       # 测试FTP连接时只需注释掉ftp_download()方法
        FTP.close()     # 结束FTP服务
