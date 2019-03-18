# -*- coding: UTF-8 -*-
# Name:         collect_data.py
# Desc          
# Author:       yutianqi 00290641   <yutianqi@huawei.com>
# Version:      V1.4   2017.09.17   * Initial Version
import paramiko
import configparser
import os
import re
def collect_data(ip, user, passwd, port=22):
    try:
        print('%s on %s, Collecting  data:' % (user, ip), end=' ')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, user, passwd,timeout=3)
        command1 = '#! /bin/bash\nls -alR ~'
        command1 = ''
        with open('test.sh') as f:
            command1 = f.read()

        ssh.exec_command("echo -e '%s' > ~/collect_data.sh;" % (command1))
        ssh.exec_command("chmod 755 ~/collect_data.sh; ~/collect_data.sh > ~/%s_%s_serverdata.txt" % (ip, user))
        ssh.exec_command("rm ~/collect_data.sh;")
        # ssh.exec_command("rm ~/%s_%s_serverdata.txt" % (ip, user))
        print('[DONE]')
        ssh.close()
    except:
        print('[FAILED]')
    return 
    
def download_data(ip, user, passwd, port=22):
    try:
        print('%s on %s, Downloading data:' % (user, ip), end=' ')
        t = paramiko.Transport((ip, port))
        t.connect(username = user, password = passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath="%s_%s_serverdata.txt" % (ip, user)
        localpath="data\\%s_%s_serverdata.txt" % (ip, user)
        sftp.get(remotepath, localpath)
        print('[DONE]')
        t.close()
    except:
        print('[FAILED]')
    return 
    
def main():
    fobj=open('list.csv', 'r')
    for eachLine in fobj:
        m = re.match('(.+),(.+),(.+),(.+)', eachLine)
        if not m:
            print("The format of this line [%s] is incorrect, Please check again." % eachLine)
        else:
            hostname = m.group(1)
            ip = m.group(2)
            user = m.group(3)
            passwd = m.group(4)            
            collect_data(ip, user, passwd, 22)
            download_data(ip, user, passwd, 22)
    fobj.close()
    os.system("pause")		
if __name__== '__main__':
    main()
    
    
    


