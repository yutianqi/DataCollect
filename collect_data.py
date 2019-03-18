# -*- coding: UTF-8 -*-

# Name:         collect_data.py
# Desc          
# Author:       yutianqi 00290641   <yutianqi@huawei.com>
# Version:      V1.4   2017.09.17   * Initial Version

import paramiko
import ConfigParser
import os
import re



def collect_data(ip, user, passwd, port=22):
    try:
        print '%s on %s, Collecting  data:' % (user, ip),
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, user, passwd,timeout=3)
        #command1 = '#! /bin/bash\nfunction read_dir(){\n    for file in `ls $1`\n    do\n        if [ -d $1"/"$file ]  \n        then\n            read_dir $1"/"$file\n        else\n            ls -alR $1"/"$file\n        fi\n    done\n}\nread_dir ~'        
        command1 = '#! /bin/bash\nls -alR ~'
        ssh.exec_command("echo -e '%s' > ~/collect_data.sh;" % (command1))
        ssh.exec_command("chmod 755 ~/collect_data.sh; ~/collect_data.sh > ~/%s_%s_serverdata.txt" % (ip, user))
        ssh.exec_command("rm ~/collect_data.sh;")
        print '[DONE]'
        ssh.close()
    except:
        print '[FAILED]'
    return 

    
    
def download_data(ip, user, passwd, port=22):
    try:
        print '%s on %s, Downloading data:' % (user, ip),
        t = paramiko.Transport((ip, port))
        t.connect(username = user, password = passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath="%s_%s_serverdata.txt" % (ip, user)
        localpath="data\\%s_%s_serverdata.txt" % (ip, user)
        sftp.get(remotepath, localpath)
        print '[DONE]'
        t.close()
    except:
        print '[FAILED]'
    return 

    
    
def process_data(localDirName):
    try:
        print 'Processing  data:',
        for fileName in os.listdir (localDirName):
            dirName = ''
            newText = ''
            fobj=open(localDirName + fileName, 'r')
            for eachLine in fobj:
                if re.match('/.*', eachLine):
                    dirName = eachLine.split(':')[0]
                    newText += eachLine
                elif re.match('.+ .+ .+ .+ .+ .+ .+ .+ .+', eachLine):
                    fieldList = eachLine.split()
                    eachLine = eachLine[:eachLine.find(fieldList[-2])+6] + dirName+'/' + fieldList[-1]
                    newText += eachLine + '\n'
                else:
                    newText += eachLine
                    
            fobj.close()
            fobj=open(localDirName + fileName, 'w')
            fobj.writelines(newText)
            fobj.close()
        print '[DONE]'
    except:
        print '[FAILED]'
    return 
    
    
    
def main():
    fobj=open('list.csv', 'r')
    for eachLine in fobj:
        m = re.match('(.+),(.+),(.+),(.+)', eachLine)
        if not m:
            print "The format of this line [%s] is incorrect, Please check again." % eachLine
        else:
            hostname = m.group(1)
            ip = m.group(2)
            user = m.group(3)
            passwd = m.group(4)            
            collect_data(ip, user, passwd, 22)
            download_data(ip, user, passwd, 22)
    fobj.close()
    # process_data('data/')
    os.system("pause")		
	
	

    
if __name__== '__main__':
    main()
    
    
    


