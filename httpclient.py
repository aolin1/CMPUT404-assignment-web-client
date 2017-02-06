#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Vinson Lai, Larin Chen
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
from urlparse import urlparse


def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code, body):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        host = urlparse(url).hostname
        port = urlparse(url).port
        if port == None:
            port = 80
        return host,port

    def connect(self, host, port):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect((host, port))
        return clientsocket

    def get_code(self, data):
        statuscode = data.split()[1]
        return statuscode

    def get_headers(self,data):
        headers = data.split("\r\n\r\n")[0]
        return headers

    def get_body(self, data):
        body = data.split("\r\n\r\n")[1]
        return body
    
    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        urlparsed = urlparse(url)
        host, port= self.get_host_port(url)
        sock = self.connect( host, port)
        sock.send("GET " + urlparsed.path + " HTTP/1.1\r\n")
        sock.send("Host: " + host + "\r\n")
        sock.send("Accept: */*\r\n\r\n")

        response = self.recvall(sock)
        code = self.get_code(response)
        body = self.get_body(response)
        return HTTPResponse(int(code), body)

    def POST(self, url, args=None):
        urlparsed = urlparse(url)
        host, port= self.get_host_port(url)
        if args:
            encoded = urllib.urlencode(args)
            length = len(encoded)
        sockpost = self.connect(host, port)
        sockpost.send("POST %s HTTP/1.1\r\n" % urlparsed.path)
        if args:
            sockpost.send("Content-Length: %d\r\n" % int(length))
        else:
            sockpost.send("Content-Length: 0\r\n")
        sockpost.send("Host: %s\r\n" % host)
        sockpost.send("Accept: */*\r\n")
        sockpost.send("Content-Type: application/x-www-form-urlencoded\r\n")    
        sockpost.send("\r\n")
        if args:
            sockpost.send(encoded)

        response = self.recvall(sockpost)
        print response
        code = self.get_code(response)
        body = self.get_body(response)      
        return HTTPResponse(int(code), body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )  
