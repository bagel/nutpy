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

def login():
    getargs()
    try:
        pyftp = ftplib.FTP(host, username, passwd)
        print "Login successful"
        print "pyftp>",
        stdin = raw_input()
        pyftp.dir()
        print "pyftp>",
    except ftplib.all_errors:
        print "ftp error"

def main():
    login()

if __name__ == '__main__':
    main()
