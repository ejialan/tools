#!/usr/bin/env python


from scapy.all import *
from scapy.utils import rdpcap
import sys, getopt, os, time, thread
from random import randint
import logging

tcp_flag_vals = {"F":0x1, "S":0x2, "R":0x4, "P":0x8,
                 "A":0x10, "U":0x20, "E":0x40, "C":0x80 }
conf={}
conns = {}

def parse_opts():
  if len(sys.argv) == 1:
    print __doc__
    exit(0)

  try:
    cmdlineOptions, args= getopt.getopt(sys.argv[1:],'hp:i:a:t:',
          ["help","port","interface","address"])
  except getopt.GetoptError, e:
    sys.exit("Error in a command-line option:\n\t" + str(e))
  for (optName,optValue) in cmdlineOptions:
    if  optName in ("-h","--help"):
      print __doc__
      exit(0)
    elif  optName in ("-p","--port"):
      conf['port'] = int(optValue)
    elif  optName in ("-i","--interface"):
      interface = optValue
      conf['interface'] = interface
    elif  optName in ("-a","--address"):
      address = optValue
      conf['address'] = address
    elif  optName in ("-t","--timeout"):
      conf['timeout'] = int(optValue) 

def get_link_name(pkt):
  return (pkt[IP].dst + '_' + str(pkt[TCP].dport)) if (conf['port'] == pkt[TCP].sport and conf['address'] == pkt[IP].src ) else (pkt[IP].src + '_' + str(pkt[TCP].sport))

def handle_tcp_pkt(pkt):
  if (pkt[TCP].flags & tcp_flag_vals["F"]) or (pkt[TCP].flags & tcp_flag_vals["R"]) :
      handle_tcp_fin(pkt)
  else :
      handle_tcp_data(pkt)

def handle_tcp_fin(pkt):
  print "handle tcp fin from " + get_link_name(pkt)
  if get_link_name(pkt) in conns:
    del(conns[get_link_name(pkt)])

def handle_tcp_data(pkt):
  #print """handle_tcp_data """ 
  #if has_load(pkt): print repr(pkt.load)
  link = get_link_name(pkt)
  conns[link] = {'time':int(time.time()*1000), 'pkt':pkt, 'conn':link}
   
def monitor_callback(pkt):
  #print """receive ____________________________________"""
  #pkt.show()
  #print pkt[TCP].flags
  if TCP in pkt:
    handle_tcp_pkt(pkt)
  else :
    print """Unsupported packet!!!!!!!!!!!!!"""
    pkt.show()

def scan_conns():
  while True:
    time.sleep(0.5)
    now  = int(time.time()*1000)
    for conn in conns.keys():
      if now - conns[conn]['time'] > conf['timeout']:
        print conns[conn]

def main():
  parse_opts()
  thread.start_new( scan_conns, ())

  print "monitor port %d and host %s on %s" % (conf['port'], conf['address'], conf['interface'])
  #sniff(prn=lambda x : monitor_callback(x), filter="port %d" % (port), iface=interface, store=0)
  sniff(prn=lambda x : monitor_callback(x), filter="port %d and host %s" % (conf['port'], conf['address']), iface=conf['interface'], store=0)

if __name__ == "__main__":
  main()
