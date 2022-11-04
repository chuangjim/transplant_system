# coding: utf-8
import paramiko
import re
import os
from time import sleep
import time
 
# reference: https://www.cnblogs.com/haigege/p/5517422.html
class Linux(object):
    # initialize
    def __init__(self, ip, username, password, pkey, timeout=3000):
        self.ip = ip
        self.username = username
        self.password = password
        self.pkey_str = pkey
        self.timeout = timeout
        # retry times
        self.try_times = 3
 
    # connect to server
    def connect(self):
        self.key=paramiko.RSAKey.from_private_key_file(self.pkey_str)
        while True:
            try:
                self.t = paramiko.Transport(sock=(self.ip, 1450))
                # self.ssh = paramiko.SSHClient()
                # self.ssh.set_missing_host_key_policy(
                            # paramiko.AutoAddPolicy())
                # self.ssh.connect(hostname=self.ip, port=1450, username=self.username)
                # self.sftp = self.ssh.open_sftp()
                self.t.connect(username=self.username, pkey=self.key)
                self.chan = self.t.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                print (u'connect to %s' % self.ip)
                # data to string
                print (self.chan.recv(65535).decode('utf-8'))
                return
            # catch all of the exceptions
            except Exception as e1:
                if self.try_times != 0:
                    print (u'connect to %s failed, retry connection ...' %self.ip)
                    self.try_times -= 1
                else:
                    print (u'retry three times, exit connection')
                    exit(1)
 
    # close connection
    def close(self):
        self.chan.close()
        self.t.close()
 
    # send command
    def send(self, cmd):
        cmd += '\n'
        # check if command is done
        result = ''
        # send command
        self.chan.send(cmd)
        # get response
        while True:
            sleep(0.5)
            ret = self.chan.recv(65535).decode('utf-8')
            print(ret)
            p = r"result:\[(.*)\]end"
            result = re.findall(p, ret)
            if result:
                result = result[0].split(', ')
                break
        time.sleep(1)
        # print('delete image...')
        # self.chan.send('/usr/bin/zsh /home/jim/Documents/lacewing/transferlearning/delete_pridict_img.sh\n')
        # print('receive:',self.chan.recv(1024).decode('utf-8'))
        return result
	# ------get derectories and files------
    def __get_all_files_in_local_dir(self, local_dir):
        # create list to safe derctories
        all_files = list()
 
        # get all directories
        files = os.listdir(local_dir)
        for x in files:
            # get absolute path of local_dir
            filename = os.path.join(local_dir, x)
            # handle event if path is a dir
            if os.path.isdir(x):
                all_files.extend(self.__get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files
 
    def sftp_put_dir(self, local_dir, remote_dir):
        t = paramiko.Transport(sock=(self.ip, 1450))
        t.connect(username=self.username, pkey=self.key)
        # t.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(t)

        # remove '/' if exist
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
 
        all_files = self.__get_all_files_in_local_dir(local_dir)

        # put every files
        for x in all_files:
            filename = os.path.split(x)[-1]
            remote_filename = remote_dir + '/' + filename
            # print (x)
            # print (remote_filename)
            # print (u'Put file %s to %s ...' % (filename,self.ip))
            sftp.put(x, remote_filename)