#!/usr/bin/env python

import socket
from optparse import OptionParser

def getser(addr,port):
    s = socket.socket()
    s.settimeout(10)
    try:
        s.connect((addr,port))
        s.send("GET / HTTP/1.0\n\n")
        receive = s.recv(500)
    except (KeyboardInterrupt, socket.error):
        receive = "Server: Timeout"
    finally:
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

def server():
    getarg()
    mesg = getser(address,port).splitlines()
    num = len(mesg)
    j = -1
    for i in range(num):
        if mesg[i][0:6] == "Server":
            j = i
            break
    if j == -1:
        print "Server: Unknown"
    else:
        print mesg[i]

def main():
    server()

if __name__ == '__main__':
    main()
