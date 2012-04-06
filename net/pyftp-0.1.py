#!/usr/bin/env python
# pyftp

import sys
import socket

usage = "Usage: python pyftp.py ftp.example.org"
if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print usage
    sys.exit(0)

title = "pyftp>"

def get_msg(n):
    if n == 0:
        return "Goodbye!"
    elif n == 1:
        return "Error: file name not given or give too more."
    elif n == 2:
        return "Command not found, try 'h' or 'help' for more help."
    elif n == 3:
        return "Error: address can't connect, please check and try again."
    elif n == 4:
        return "Error: please check and try again."
    elif n == 5:
        return "Local Error: no such file or directory"
    elif n == 6:
        return "Task not complete."
    elif n == 7:
        return "Login Error: please check your user or password and try again."

def recive(ftp):
    global ret
    ret = ftp.recv(1024)
    print ret,

def cyc_recive(ftp):
    global cret
    while True:
        cret = ftp.recv(1024)
        if cret == '':
            break
        print cret,

def recv_num(r):
    return int(r.split(' ')[0])
    
def send_cmd(command):
    cftp.send(command + '\n')
    recive(cftp)

def login():
    global cftp
    cftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cftp.connect((sys.argv[1], 21))
    user = raw_input("user(ftp):")
    if user == '':
        user = 'ftp'
    password = raw_input("password:")
    send_cmd("USER %s" % user)
    send_cmd("PASS %s" % password)
    recive(cftp)
    if recv_num(ret) == 530:
        print "%s\n%s" % (get_msg(7), get_msg(0))
        sys.exit(0)

def data_connect(r):
    imin = r.find('(')
    imax = r.find(')')
    imin = imin + 1
    num_list = r[imin:imax].split(',')
    ip = "%s.%s.%s.%s" % (num_list[0], num_list[1], num_list[2], num_list[3])
    port = int(num_list[4]) * 256 + int(num_list[5])
    global dftp
    dftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dftp.connect((ip, port))

def input_cmd():
    global cmd, cmd0, cmd_len, mv_cmd1, mv_cmd2, filename
    cmd = raw_input("%s" % title)
    scmd = cmd.split(' ')
    cmd_len = len(scmd)
    scmd[0] = scmd[0].lower()
    cmd0 = scmd[0]

    if scmd[0] == 'ls':
        scmd[0] = 'list'
    elif scmd[0] == 'cd':
        scmd[0] = 'cwd'
    elif scmd[0] == 'mkdir':
        scmd[0] = 'mkd'
    elif scmd[0] == 'rmdir':
        scmd[0] = 'rmd'
    elif scmd[0] == 'rm':
        scmd[0] = 'dele'
    elif scmd[0] == 'get' and cmd_len == 2:
        scmd[0] = 'retr'
        filename = scmd[1]
    elif scmd[0] == 'put' and cmd_len == 2:
        scmd[0] = 'stor'
        filename = scmd[1]

    if cmd_len == 2:
        cmd = scmd[0] + ' ' + scmd[1]
    else:
        cmd = scmd[0]

    if scmd[0] == 'mv' and cmd_len == 3:
        mv_cmd1 = 'rnfr' + ' ' + scmd[1]
        mv_cmd2 = 'rnto' + ' ' + scmd[2]

def mod_pasv():
    send_cmd('pasv')
    data_connect(ret)
    send_cmd(cmd)
#    recive(cftp)

def get_file(filename):
    mod_pasv()
    if recv_num(ret) == 550:
        return 0
    fd = open(filename, 'wb+')
    print "Downloading..."
    while True:
        data = dftp.recv(1024)
        if data == '':
            break
        fd.write(data)
    fd.close()
    return 1

def put_file(filename):
    fp = open(filename, 'rb+')
    mod_pasv()
    while True:
        data = fp.readline()
        if not data:
            break
        dftp.send(data)
    fp.close()

cmd_list = ['ls', 'cd', 'pwd', 'rm', 'rmdir', 'mkdir', 'mv', 'get', 'put', 'help', 'quit']
def put_help():
    cmd_len = len(cmd_list)
    i = 0
    while (i < cmd_len):
        print "%s " % cmd_list[i],
        i = i + 1
    print


def cyc_run():
    while True:
        input_cmd()

        if cmd == "q" or cmd == "quit" or cmd == "exit":
            print get_msg(0)
            sys.exit(0)
        elif cmd == '':
            continue
        elif cmd == 'help' or cmd == 'h':
            put_help()
            continue
        elif cmd0 == 'mv':
            if cmd_len != 3:
                print get_msg(1)
                continue
            send_cmd(mv_cmd1)
            send_cmd(mv_cmd2)
            continue
        elif cmd0 == 'ls':
            mod_pasv()
            cyc_recive(dftp)
            recive(cftp)   #cmd complete server send msg
            continue
        elif cmd0 == 'get':
            if cmd_len != 2:
                print get_msg(1)
                continue
            if get_file(filename):
                recive(cftp)
            continue
        elif cmd0 == 'put':
            if cmd_len != 2:
                print get_msg(1)
                continue
            put_file(filename)
        #    recive(cftp)
            continue
        elif cmd0 not in cmd_list:
            print get_msg(2)
            continue

        send_cmd(cmd)

def main():
    try:
        login()
        while True:
            try:
                cyc_run()
            except KeyboardInterrupt:
                print "\n%s\n%s" % (get_msg(6),get_msg(0))
                sys.exit(0)
            except IndexError:
                print get_msg(4)
            except IOError:
                print "%s: '%s'" % (get_msg(5), filename)
    except socket.gaierror:
        print "%s\n%s" % (get_msg(3), usage)

if __name__ == "__main__":
    main()
