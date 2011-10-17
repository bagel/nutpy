#!/usr/bin/env python

import ftplib
from optparse import OptionParser

def getargs():
    parser = OptionParser()
    parser.add_option("-r", "--remote-address", dest="address", default="localhost", help="Remote ftp server host IP or Domain", metavar="REMOTE ADDRESS")
    parser.add_option("-u", "--username", dest="username", default="ftp", help="Ftp user name", metavar="USERNAME")
    parser.add_option("-p", "--passwd", dest="passwd", default="", help="Ftp password", metavar="PASSWORD")
    (options, args) = parser.parse_args()
    global host, username, passwd
    host = options.address
    username = options.username
    passwd = options.passwd

title = "pyftp>"

def login():
    getargs()
    try:
        global pyftp
        pyftp = ftplib.FTP(host, username, passwd)
        print "Login Successful"
        pyftp.getwelcome()
        print title,
        while True:
            stdin = raw_input()
            stdarg = stdin.split(" ")
            if stdin == 'ls' or stdin == 'dir':
                pyftp.dir()
            elif stdin == 'pwd':
                pyftp.pwd()
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
                break
            elif stdin == 'help':
                print "ls\tdir\tpwd\tmkdir\t\nrmdir\tmv\trename\tquit\t\nexit\tdelete\trm\tget"
            elif stdin == '':
                pass
            else:
                print "Invalid command.Try again.\"help\" for more information."
            print title,
    except ftplib.all_errors:
        print ftplib.all_errors
        print "Error\r\nLogout"

def main():
    login()

if __name__ == '__main__':
    main()
