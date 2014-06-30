import socket, sys
import os, os.path
import json
import re


def handle(line):
  if "status" not in line:
    return
  event = json.loads(line)
  status = event["status"]
  if "start" == status:
    handleStartEvent(event)

def handleStartEvent(event):
  id = event["id"]
  container = inspect(id)
  print container
  ip = container['NetworkSettings']['IPAddress']
  host = container['Config']['Hostname']
  print "host = ", host, "ip = ", ip
  cmd = "find /var/lib/docker/containers/ -name hosts | xargs -I rep sh -c \"echo \'{0} {1}' >> rep\"".format(ip, host)
  print cmd
  os.system(cmd)

def inspect(id):
  req = "GET /containers/{0}/json HTTP/1.1\r\n\r\n".format(id)
  client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM)
  client.connect("/var/run/docker.sock");
  client.sendall(req)
  res = ""
  content_len = 0
  try:
    while True:
      data = client.recv(1024)
      if not data:
	break
      else:
	res += data
	''' 
	there is not EOF from the socker.sock, so here have to check the content length so as to break out after reading the whole content.
	'''
	if content_len == 0:
	  content_len,res = getContentLength(res)
	if content_len > 0 and len(res) == content_len:
	  break
  finally:     
    client.close()
  return json.loads(res)

def getContentLength(content):
  content_len = 0
  p = "Content-Length: ([0-9]*)\r\n\r\n(.*)"
  m = re.search(p, content, re.M)
  if m:
    content_len = int(m.group(1))
  return content_len, m.group(2)

if os.path.exists("/var/run/docker.sock"):
  client = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM)
  print "Connecting ..."
  client.connect("/var/run/docker.sock");
  '''
  request examples
  GET /images/json\r\n\r\n
  GET /images/json?all=0 HTTP/1.1\r\n\r\n
  '''
  req = 'GET /events HTTP/1.1\r\n\r\n'
  if len(sys.argv) > 1:
    req = sys.argv[1].decode("string_escape")
  print "send: ", repr(req)
  client.sendall(req);
 
  try:
    s = client.makefile()
    while True:
      line = s.readline()
      if not line:
	break
      else:
	print "recv: ", repr(line)
	handle(line)
  finally:
    client.close()
