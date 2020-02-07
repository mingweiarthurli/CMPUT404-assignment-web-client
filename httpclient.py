#!/usr/bin/env python3
# coding: utf-8
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
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

def parse_url(url):
    parsed = re.findall(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?([^:\/?\n]+)?(?:\:)?([0-9]+)?(?:\/?)([a-z0-9\-._~%!$&'()*+,;=:@\/]+)*\/?", url, re.I)
    host = parsed[0][0]
    port = parsed[0][1]
    path = '/' + parsed[0][2]

    if port == '':
        port = '80'     # use port 80 to deal with unspecified port

    return host, port, path

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = re.findall(r'^(?:HTTP/[1-2]\.[0-1]\ )([0-9]+)(?:\ )', data)
        return int(code[0])

    def get_headers(self,data):
        headers = re.findall(r'(?:\r\n)([\w\W]*)(?:\r\n\r\n)', data)
        headers = headers[0].split('\r\n')
        return headers

    def get_body(self, data):
        body = re.findall(r'(?:\r\n\r\n)([\w\W]*)$', data)
        return body[0]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

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
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port, path = parse_url(url)
        # if has no port, then omit port in the body
        if port == '80':
            payload = 'GET ' + path + ' HTTP/1.1\r\nHOST: ' + host + '\r\n\r\n'
        else:
            payload = 'GET ' + path + ' HTTP/1.1\r\nHOST: ' + host + ':' + port + '\r\n\r\n'

        self.connect(host, int(port))
        self.sendall(payload)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        print(body)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host, port, path = parse_url(url)

        form = ''
        # concatenate form vars
        if args != None:
            for key in args:
                form = form + key + '=' + args[key] + '&'
            form = form[:-1]        # delete the last '&'

        # if has no port, then omit port in the body
        if port == '80':
            payload = ('POST ' + path + ' HTTP/1.1\r\nHOST: ' + host + '\r\n' + 
                'Content-Type: application/x-www-form-urlencoded\r\nContent-Length: ' + 
                str(len(form.encode('utf-8'))) + '\r\n\r\n' + form)
        else:
            payload = ('POST ' + path + ' HTTP/1.1\r\nHOST: ' + host + ':' + port + '\r\n' + 
                'Content-Type: application/x-www-form-urlencoded\r\nContent-Length: ' + 
                str(len(form.encode('utf-8'))) + '\r\n\r\n' + form)

        self.connect(host, int(port))
        self.sendall(payload)
        response = self.recvall(self.socket)
        self.close()

        code = self.get_code(response)
        body = self.get_body(response)
        print(body)

        return HTTPResponse(code, body)

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
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
