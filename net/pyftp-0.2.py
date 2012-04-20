#!/usr/bin/env python
# pyftp, ftp client

import sys
import socket

usage = '''Usage: pyftp [-m mode] [-r host] ftp.example.org
       -m, --mode  PASV or PORT
       -r, --host  Host to connect
       -h, --help  Get this help'''

err_help = "Try '-h' or '--help' for more help."
file_err = "File name not given or give too more."

def get_opt():
    import getopt
    global host, mode
    host = " "
    mode = "PASV"
    if len(sys.argv) == 1:
        print err_help
        sys.exit(0)
    if sys.argv[1][0] != '-':   #if first arg not opt, then i think it's host
        host = sys.argv[1]
        argvs = sys.argv[2:]
    else:
        argvs = sys.argv[1:]

    try:
        opts, args = getopt.getopt(argvs, "hm:r:", ["help", "mode=", "host="])
    except getopt.GetoptError, err:
        print "Error: %s" % str(err)
        print err_help
        sys.exit(0)
    for opt, val in opts:
        if opt in ("-h", "--help"):
            print usage
            sys.exit(0)
        elif opt in ("-m", "--mode"):
            mode = val
        elif opt in ("-r", "--host"):
            host = val

    mode = mode.upper()
    if len(args) >= 1:
        host = args[0]
    if host == " " or mode not in ("PASV", "PORT"):
        print "Error: not give host or mode."
        print err_help
        sys.exit(0)

get_opt()

def get_msg():
    global msg
    ref = cftp.makefile('rb')
    msg = ref.readline()
    rn = msg[:3]
    if msg[3:4] == '-':
        while True:
            next_msg = ref.readline()
            msg = msg + next_msg
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
    cftp.connect((host, 21))
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
    if msg[:3] == '530':   #if login incorrect repeat
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
    cmd = raw_input("pyftp>")
    scmd = cmd.split(' ')
    cmd_len = len(scmd)

    j = 0
    while j < cmd_len:
        if scmd[j] == '':   #space not give right way
            scmd.pop(j)
            cmd_len = cmd_len - 1
        else:
            j = j + 1

    if cmd_len == 0:   #input spaces
        return 0

    cmd0 = scmd[0]

    if (scmd[0] == 'get' or scmd[0] == 'put') and cmd_len == 2:
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

    return 1

#functions in this, return 0 False, return 1 Success

def mod_pasv():
    send_cmd('pasv')
    if msg[:3] == '227':
        pasv_connect()
        send_cmd(cmd)
        if msg[:3] != '550':
            return 1
    return 0
#    get_msg(cftp)

def make_port():
    import random
    global port, port1, port2
    port = random.randint(32768,61000)
    port1 = port/256
    port2 = port%256

def get_ip():
    import re
    import commands
    global localip
    ipStr = commands.getoutput('ip addr show')
    ipList = re.findall('\d+\.\d+\.\d+\.\d+', ipStr)
    k = 0
    while k < len(ipList):
        if ipList[k] == '127.0.0.1' or '255' in ipList[k]:
            ipList.pop(k)
        else:
            k = k + 1
    localip = ipList[0]     #if more than one ethernet, the first one use
    if host in ('localhost', '127.0.0.1', socket.gethostname()):
        localip = '127.0.0.1'

def port_connect():
    global port_cmd, tftp
#    loip = socket.gethostbyname(socket.gethostname())
    get_ip()
    ipn = localip.split('.')
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
        if msg[:3] == '550':
            return 0
        while True:
            tftp_sock, addr = tftp.accept()
            if tftp_sock:
                break
        return 1
    return 0

def chs_mod():
    global sock
    if mode == "PASV":
        if mod_pasv():
            sock = sftp
            return 1
    elif mode == "PORT":
        if mod_port():
            sock = tftp_sock
            return 1
    return 0

def get_file(filename):
    if not chs_mod():
        return 0
    #if msg[:3] == '550':
    #    return 0
    fd = open(filename, 'wb+')
    print "Downloading..."
    while True:
        data = sock.recv(4096)
        if data == '':
            break
        fd.write(data)
    fd.close()
    sock.close()
    return 1

def put_file(filename):
    try:
        fp = open(filename, 'rb+')
    except IOError:
        print "%s: '%s'" % (inf[4], filename)
        return 0
    if not chs_mod():
        return 0
    #if msg[:3] == '550':
    #    return 0
    print "Uploading..."
    while True:
        data = fp.readline()
        if not data:
            break
        sock.send(data)
    fp.close()
    sock.close()
    return 1

cmd_list = ('!', 'ls', 'cd', 'pwd', 'rm', 'rmdir', 'mkdir', 'mv', 'get', 'put', 'help', 'quit')
def put_help():
    cmd_len = len(cmd_list)
    for i in range(cmd_len):
        print "%s " % cmd_list[i],
    print

def cyc_run():
    while True:
        if not input_cmd():
            continue

        if cmd in ("q", "quit", "exit"):
            send_cmd("quit")
            #print file_err
            sys.exit(0)
        elif cmd == '':
            continue
        elif cmd == 'help' or cmd == 'h':
            put_help()
            continue
        elif cmd0 == 'cd':
            if cmd_len != 2:
                print file_err
                continue
        elif cmd0 == 'mv':
            if cmd_len != 3:
                print file_err
                continue
            send_cmd(mv_cmd1)
            send_cmd(mv_cmd2)
            continue
        elif cmd0 == 'ls':
            if chs_mod():
                get_data(sock)
                sock.close()
                get_msg()    #server send complete msg
            continue
        elif cmd0 == 'get':
            if cmd_len != 2:
                print file_err
                continue
            if get_file(filename):
                get_msg()
            continue
        elif cmd0 == 'put':
            if cmd_len != 2:
                print file_err
                continue
            if put_file(filename):
                get_msg()
            continue
        elif cmd0[0] is '!':
            import os
            os.system('%s' % cmd[1:])
            continue
        #elif cmd0 not in cmd_list:
        #    print inf[1]
        #    continue

        send_cmd(cmd)
        if msg[:3] == '500':
            print "Try 'h' or 'help' for more help"

def main():
    try:
        ln_connect()
        login()
        while True:
            try:
                cyc_run()
            except KeyboardInterrupt:
                print
                send_cmd("quit")
                break
            except IndexError, NameError:
                print "Error: please check and try again."
            except socket.error:
                print "Connection time out."
                break
    except socket.gaierror:
        print "Error: address can't connect.\n%s" % err_help
    except KeyboardInterrupt:
        print
    finally:
        cftp.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
