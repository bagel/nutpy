#!/usr/bin/env python

import socket
import os
from optparse import OptionParser

def getser(addr,port):
    s = socket.socket()
    s.connect((addr,port))
    s.send("GET / HTTP/1.0\n\n")
    receive = s.recv(200)
    s.close()
    return receive

def getarg():
    parser = OptionParser()
    parser.add_option("-a", "--address", dest="address", default="localhost", help="IP or Domain", metavar="ADDRESS")
    parser.add_option("-p", "--port", dest="port", type="int", default="80", help="port", metavar="PORT")
    (options, args) = parser.parse_args()
    global address
    global port
    address = options.address
    port = options.port
    print "address:%s, port:%d" % (address, port)

def main():
    getarg()
    print getser(address,port)

if __name__ == '__main__':
    main()
