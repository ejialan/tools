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
rt = {}

def parse_opts():
  if len(sys.argv) == 1:
    print __doc__
    exit(0)

  try:
    cmdlineOptions, args= getopt.getopt(sys.argv[1:],'hp:a:t:f:',
          ["help","port","address"])
  except getopt.GetoptError, e:
    sys.exit("Error in a command-line option:\n\t" + str(e))
  for (optName,optValue) in cmdlineOptions:
    if  optName in ("-h","--help"):
      print __doc__
      exit(0)
    elif  optName in ("-p","--port"):
      conf['port'] = int(optValue)
    elif  optName in ("-a","--address"):
      address = optValue
      conf['address'] = address
    elif  optName in ("-t","--timeout"):
      conf['timeout'] = int(optValue) 
    elif  optName in ("-f","--file"):
      conf['file'] = optValue 

def get_link_name(pkt):
  return (pkt[IP].dst + '_' + str(pkt[TCP].dport)) if (conf['port'] == pkt[TCP].sport and conf['address'] == pkt[IP].src ) else (pkt[IP].src + '_' + str(pkt[TCP].sport))

def handle_tcp_pkt(pkt):
  if (pkt[TCP].flags & tcp_flag_vals["F"]) or (pkt[TCP].flags & tcp_flag_vals["R"]) :
      handle_tcp_fin(pkt)
  else :
      handle_tcp_data(pkt)

def handle_tcp_fin(pkt):
  #print "handle tcp fin from " + get_link_name(pkt)
  if get_link_name(pkt) in conns:
    del(conns[get_link_name(pkt)])

def handle_tcp_data(cur_pkt):
  #print """handle_tcp_data """ 
  #if has_load(pkt): print repr(pkt.load)
  link = get_link_name(cur_pkt)
  if link not in conns:
    conns[link] = {'pkt':cur_pkt, 'conn':link}
    rt[link] = []
    return

  pre_pkt = conns[link]['pkt']
  conns[link] = {'pkt':cur_pkt, 'conn':link}

  if hasattr(pre_pkt, 'load') \
        and pre_pkt[IP].dst == conf['address']: 
    t = (cur_pkt.time - pre_pkt.time)*1000
    rt[link].append(float(format(t, '.2f')))

    if t > conf['timeout']:
      print t, pre_pkt 

   
def parse_pkt(pkt):
  if TCP in pkt:
    handle_tcp_pkt(pkt)
  else :
    print """Unsupported packet!!!!!!!!!!!!!"""
    pkt.show()

def main():
  parse_opts()
  reader = PcapReader(conf['file'])
  p = reader.read_packet()
  while p is not None:
    parse_pkt(p)
    p = reader.read_packet()

  for r in rt:
    print r, rt[r]

  for r in rt:
    print r, len(rt[r])

if __name__ == "__main__":
  main()
  

