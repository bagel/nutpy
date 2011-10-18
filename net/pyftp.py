#!/usr/bin/env python

import ftplib
from optparse import OptionParser

def getargs():
    parser = OptionParser()
    parser.add_option("-r", "--remote-address", dest="address", default="localhost", help="remote ftp server host IP or Domain", metavar="REMOTE ADDRESS")
    parser.add_option("-u", "--username", dest="username", default="ftp", help="ftp user name", metavar="USERNAME")
    parser.add_option("-p", "--passwd", dest="passwd", default="", help="ftp password", metavar="PASSWORD")
    (options, args) = parser.parse_args()
    global host, username, passwd
    host = options.address
    username = options.username
    passwd = options.passwd

title = "pyftp>"

def connect():
    getargs()
    global pyftp
    pyftp = ftplib.FTP(host, username, passwd)
    print "Login Successful!"
    print pyftp.getwelcome()

def operate():
    while True:
        print title,
        stdin = raw_input()
        stdarg = stdin.split(" ")
        if stdin == 'ls' or stdin == 'dir':
            pyftp.dir()
        elif stdin == 'pwd':
            print pyftp.pwd()
        elif stdarg[0] == 'cd':
            pyftp.cwd(stdarg[1])
        elif stdarg[0] == 'mkdir':
            pyftp.mkd(stdarg[1])
        elif stdarg[0] == 'rmdir':
            pyftp.rmd(stdarg[1])
        elif stdarg[0] == 'mv' or stdarg[0] == 'rename':
            pyftp.rename(stdarg[1],stdarg[2])
        elif stdarg[0] == 'rm' or stdarg[0] == 'delete':
            pyftp.delete(stdarg[1])
        elif stdarg[0] == 'get':
            local_file = open(stdarg[1], 'wb')
            pyftp.retrbinary('RETR %s' % stdarg[1], local_file.write)
            print "Transfer complete."
        elif stdarg[0] == 'put':
            local_file = open(stdarg[1], 'rb')
            pyftp.storbinary('STOR %s' % stdarg[1], local_file)
            print "Transfer complete."
        elif stdin == 'quit' or stdin == 'exit':
            pyftp.quit()
            print "Goodbye!"
            break
        elif stdin == 'help':
            print "ls\tdir\tpwd\tmkdir\t\nrmdir\tmv\trename\tquit\t\nexit\tdelete\trm\tget\nput\thelp"
        elif stdin == '':
            pass
        else:
            print "Invalid command.Try again.\"help\" for more information."

def cycle():
    try:
        operate()
    except ftplib.error_perm:
        print "550 Permission denied."
        cycle()
    except ftplib.error_temp:
        print "421 Timeout."
        cycle()
    except IndexError:
        cycle()
    except IOError:
        print "local: No such file or directory."
        cycle()
    except KeyboardInterrupt:
        print "\r\nGoodbye!"

def main():
    connect()
    cycle()

if __name__ == '__main__':
    main()
