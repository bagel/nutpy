#!/usr/bin/env python
# pyftp

import sys
import socket

usage = "Usage: python pyftp.py ftp.example.org"
if len(sys.argv) != 2 or sys.argv[1] == '-h' or sys.argv[1] == '--help':
    print usage
    sys.exit(0)

MODE = 1   #'1' use pasv mode, else use port mode.

title = "pyftp>"

inf = ("Goodbye!",
       "Error: file name not given or give too more.",
       "Command not found, try 'h' or 'help' for more help.",
       "Error: address can't connect, please check and try again.",
       "Error: please check and try again.",
       "Local Error: no such file or directory",
       "Task not complete.")

def get_msg():
    global msg
    ref = cftp.makefile('rb')
    msg = ref.readline()
    rn = msg[:3]
    if msg[3:4] == '-':
        while True:
            next_msg = ref.readline()
            msg = msg + '\n' + next_msg
            if next_msg[:3] == rn and next_msg[3:4] != '-':
                break
    print msg,
    return msg

def get_data(s):
    while True:
        data = s.recv(4096)
        if data == '':
            break
        print data,

def send_cmd(command):
    cftp.send(command + '\n')
    get_msg()

def ln_connect():
    global cftp
    cftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cftp.connect((sys.argv[1], 21))
    get_msg()

def login():
    user = raw_input("user(ftp):")
    if user == '':
        user = 'ftp'
    send_cmd("USER %s" % user)
    if msg[0] == '3':
        password = raw_input("password:")
        send_cmd("PASS %s" % password)
#    if recv_num(msg) != 230:
#        get_msg()
    if msg[:3] == '530':
        login()

def pasv_connect():
    imin = msg.find('(')
    imax = msg.find(')')
    imin = imin + 1
    num_list = msg[imin:imax].split(',')
    ip = "%s.%s.%s.%s" % (num_list[0], num_list[1], num_list[2], num_list[3])
    port = int(num_list[4]) * 256 + int(num_list[5])
    global sftp
    sftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sftp.connect((ip, port))

def input_cmd():
    global cmd, cmd0, cmd_len, mv_cmd1, mv_cmd2, filename
    cmd = raw_input("%s" % title)
    scmd = cmd.split(' ')
    cmd_len = len(scmd)
    cmd0 = scmd[0]

    if scmd[0] == 'get' or scmd[0] == 'put' and cmd_len == 2:
        filename = scmd[1]

    cmd_dict = {'ls':'list', 'cd':'cwd', 'mkdir':'mkd', 'rmdir':'rmd',
                'rm':'dele', 'get':'retr', 'put':'stor'}
    if scmd[0] in cmd_dict.keys():
        scmd[0] = cmd_dict[scmd[0]]

    cmd = scmd[0]
    for i in range(1, cmd_len):
        cmd = cmd + ' ' + scmd[i]

    if scmd[0] == 'mv' and cmd_len == 3:
        mv_cmd1 = 'rnfr' + ' ' + scmd[1]
        mv_cmd2 = 'rnto' + ' ' + scmd[2]

def mod_pasv():
    send_cmd('pasv')
    if msg[:3] == '227':
        pasv_connect()
        send_cmd(cmd)
        return 1
    return 0
#    get_msg(cftp)

def make_port():
    import random
    global port, port1, port2
    port = random.randint(1024,65535)
    port1 = port/256
    port2 = port%256

def port_connect():
    global port_cmd, tftp
#    loip = socket.gethostbyname(socket.gethostname())
    hostip = '10.217.86.123'     #replace to your host ip here
    ipn = hostip.split('.')
    port_cmd = "PORT %s,%s,%s,%s,%s,%s" % (ipn[0], ipn[1], ipn[2], ipn[3], port1, port2)
    tftp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock_ip, sock_port = tftp.getsockname()
    tftp.bind((sock_ip, port))
    tftp.listen(1)

def mod_port():
    global tftp_sock
    make_port()
    port_connect()
    send_cmd(port_cmd)
    if msg[0] == '2':
        send_cmd(cmd)
        while True:
            tftp_sock, addr = tftp.accept()
            if tftp_sock:
                break
        return 1
    return 0

def chs_mod():
    global sock
    if MODE == 1:
        if mod_pasv():
            sock = sftp
            return 1
    else:
        if mod_port():
            sock = tftp_sock
            return 1
    return 0

def get_file(filename):
    if not chs_mod():
        return 0
    if msg[:3] == '550':
        return 0
    fd = open(filename, 'wb+')
    print "Downloading..."
    while True:
        data = sock.recv(1024)
        if data == '':
            break
        fd.write(data)
    fd.close()
    return 1

def put_file(filename):
    fp = open(filename, 'rb+')
    if not chs_mod():
        return 0
    while True:
        data = fp.readline()
        if not data:
            break
        sock.send(data)
        print data
    fp.close()

cmd_list = ('!', 'ls', 'cd', 'pwd', 'rm', 'rmdir', 'mkdir', 'mv', 'get', 'put', 'help', 'quit')
def put_help():
    cmd_len = len(cmd_list)
    for i in range(cmd_len):
        print "%s " % cmd_list[i],
    print

def cyc_run():
    while True:
        input_cmd()

        if cmd == "q" or cmd == "quit" or cmd == "exit":
            print inf[0]
            sys.exit(0)
        elif cmd == '':
            continue
        elif cmd == 'help' or cmd == 'h':
            put_help()
            continue
        elif cmd0 == 'mv':
            if cmd_len != 3:
                print inf[1]
                continue
            send_cmd(mv_cmd1)
            send_cmd(mv_cmd2)
            continue
        elif cmd0 == 'ls':
            if chs_mod():
                get_data(sock)
                get_msg()    #server send complete msg
            continue
        elif cmd0 == 'get':
            if cmd_len != 2:
                print inf[1]
                continue
            if get_file(filename):
                get_msg()
            continue
        elif cmd0 == 'put':
            if cmd_len != 2:
                print inf[1]
                continue
            put_file(filename)
        #    get_msg()
            continue
        elif cmd0[0] is '!':
            import os
            os.system('%s' % cmd[1:])
            continue
        elif cmd0 not in cmd_list:
            print inf[2]
            continue

        send_cmd(cmd)

def main():
    try:
        ln_connect()
        login()
        while True:
            try:
                cyc_run()
#            except KeyboardInterrupt:
#                print "\n%s\n%s" % (inf[6],inf[0])
#                sys.exit(0)
            except IndexError, NameError:
                print inf[4]
    except socket.gaierror:
        print "%s\n%s" % (inf[3], usage)
#    except KeyboardInterrupt:
#        print "\n%s\n%s" % (inf[6], inf[0])
#    except:
#        sys.exit(0)

if __name__ == "__main__":
    main()
