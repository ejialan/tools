#!/usr/bin/env python


from scapy.all import *
from scapy.utils import rdpcap
import sys, getopt, os, time
from random import randint
import logging

conf={}
conns = {}

def load_len(pkt):
    if hasattr(pkt, 'load'):
        return len(pkt.load)
    else :
        return 0

def get_peer_address(pkt):
    return (pkt[IP].dst + '_' + str(pkt[TCP].dport)) if (conf['port'] == pkt[TCP].sport and conf['address'] == pkt[IP].src ) else (pkt[IP].src + '_' + str(pkt[TCP].sport))

def is_tcp(pkt):
    return pkt.haslayer(TCP) == 1

def handle_tcp_pkt(pkt):
    if (pkt[TCP].flags & tcp_flag_vals["F"]) or (pkt[TCP].flags & tcp_flag_vals["R"]) :
        print """handle tcp fin"""
        handle_tcp_fin(pkt)
    else :
        handle_tcp_data(pkt)

def handle_tcp_fin(pkt):
    del(conns[get_peer_address(pkt)])

def handle_tcp_data(pkt):
    #print """handle_tcp_data """ 
    #if has_load(pkt): print repr(pkt.load)
    #pkt.show()
    peer = get_peer_address(pkt)
    conns[peer] = {'time':int(time.time()*1000), 'pkt':pkt}
   
def monitor_callback(pkt):
    print """receive ____________________________________"""
    #pkt.show()
    #print pkt[TCP].flags
    if is_tcp(pkt):
       handle_tcp_pkt(pkt)
    else :
       print """not supported packet!!!!!!!!!!!!!"""

def scan_conns():
    now  = int(time.time()*1000)
    for conn in conns.keys():
        if now - conns[conn]['time'] > conf['timeout']:
            print conn

if __name__ == "__main__":
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
            port = int(optValue)
            conf['port'] = port
        elif  optName in ("-i","--interface"):
            interface = optValue
            conf['interface'] = interface
        elif  optName in ("-a","--address"):
            address = optValue
            conf['address'] = address
        elif  optName in ("-t","--timeout"):
            conf['timeout'] = int(optValue) 

    sniff(prn=lambda x : monitor_callback(x), filter="dst port %d and dst host %s" % (port, address), iface=interface, store=0)

