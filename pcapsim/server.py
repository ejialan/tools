#!/usr/bin/env python

import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('192.168.56.102', 3080)
sock.bind(server_address)
sock.listen(1)

while True : 
    sock.accept()

