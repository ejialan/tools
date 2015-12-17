#!/usr/bin/env python

"""
pcap-sim.py
Usage: pcap-sim.py [options]

Options:
  -h, --help
     Help message
  -m, --mode
     The working mode, server mode and client mode are supported.
  -i, --interface
     Define network interface on which the network packets will be sent and received.
  -a, --address
     The IP address 
  -p, --port
     The port
  -f, --file
     The pcap file to be used. 
     Multipe pcap files can assigned, packet matcher will try to match a packet within each pcap file, by the order they appear in the command line.
     Each pcap file can have its own options for packet matching. Refer to <Pakcet mathcing options> for details.
  -r, --replace
     Replace the specified IP address and port in the pcap file with values specified by -a and -p.
  -w, --welcome
     Send a welcome message when a client is connected.
  -t, --protocol
     Protocol to analysis the pcap file and received network packets. By default, raw protocol is applied,
     
Packet matching:
  When a data packet received from client, the packet matcher will match the packet with the packets in the pcap files one by one. 
  If a matched packet found, the matching processing ends. The matcher then return a list of packets as result. The list contains sequential packets which start from the matched packet (not included) to the next packet which is from client (not included too), i.e, all followed sequential packets which are sent from server to client.
  If no matched packet found, an empty list is returned.
  The matcher will record the index of the matched packet. The next matching process will start from this index instead of the begining of the pcap file. This mechanism is desinged to handle the protocol which has control packets mixed up with data packets, for example the Ericsson APG telnet protocol. Each client connection has its own record so as not to impact to each other.

Packet matching options:
  wrap
     Wrap around the pcap file to match a packet. By default, each packet in a pcap file will be matched only once, i.e, if a packet is matched once, it would never be matched again. 

Protocols:
  raw:
     Match the request and response as raw string.
     There is no translation applied to the payload of packets.

  ldap:
     Match the packets as ldap protocol.
     The message id of ldap response is adjusted according to the received ldap request.

  regex:[config]:
     Match the packets according to regular expression.
     The response returned is adjusted according to the given regular expression.
     The regular expression is passed in as configuration following by a ':'. The configuration is json formated: 
       { 
         'match' : 'request match pattern', 
         'adjust' : [ ['request search pattern 1', 'response search pattern 1'], [...] ]
       }
     The request match pattern is used to match the received packet and the packets in pcap file. The pattern must contain more than one group. 
     One received packet is matched only if:
       1) both the received packet and one packet in pcap file match the pattern
       2) the groups from both match are same
     The request search pattern and response search pattern is used to adjust the returned response packet. Both patterns must contain one and only one group. The matched group of the response is replaced by the matched group of the request if both search patterns produce a match of received packet and one returned response packet.
  
  cai3g:
     Match the packets according to cai3g protocol.
     The cai3g is based on regex protcol.

Examples:
   ./pcap-sim.py -p 5761 -i eth0 -a 150.236.225.96 -m server -f test/hlr_login2.pcap -f test/hlr_ordered_single.pcap,wrap -r 172.26.11.61:5000,192.168.67.43:5566 -w "hello"
"""

from scapy.all import *
from scapy.utils import rdpcap
import sys, getopt, os, time
from random import randint
import logging
from matcher.matcher import *
from matcher.misc import *

welcome=None

def revert_tcp_pkt(pkt):
    eth=Ether(src=pkt[Ether].dst, dst=pkt[Ether].src)
    ip=IP(dst=pkt[IP].src, src=pkt[IP].dst)
    tcp=TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags="A", ack=pkt[TCP].seq + load_len(pkt), seq=pkt[TCP].ack)
    return eth/ip/tcp
    

def tcp_syn_handle(pkt):
    eth=Ether(src=pkt[Ether].dst, dst=pkt[Ether].src)
    ip=IP(dst=pkt[IP].src, src=pkt[IP].dst)
    tcp=TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags="SA", options=pkt[TCP].options)
    tcp.ack = pkt[TCP].seq + 1
    tcp.seq = 0
    s=eth/ip/tcp
    s.show()
    ack=srp1(s, iface=interface)
    print "Got ack of SA"
    ack.show()
    if welcome is not None:
        print "send welcome message:", welcome
        ack=revert_tcp_pkt(ack)
        ack[TCP].flags="PA"
        sendp(ack/welcome, iface=interface)

def load_len(pkt):
    if hasattr(pkt, 'load'):
        return len(pkt.load)
    else :
        return 0

def tcp_response_ack(pkt):
    s=revert_tcp_pkt(pkt)
    #s.show()
    sendp(s, iface=interface)
    return s

def handle_tcp_data(pkt):
    print """handle_tcp_data """ 
    if has_load(pkt): print repr(pkt.load)
    #pkt.show()
    ACK=tcp_response_ack(pkt)
    for m in matchers:
      resps=m.match(pkt)
      if len(resps) > 0: break
    if resps is not None:
        print "send pkts num" , len(resps)
        print "load ___"
        for resp in resps: print repr(resp.load)
        print "load done"
        for rsp in resps:
            ACK[TCP].flags="PA"
            ACK = srp1(ACK/rsp.load, iface=interface)
            ACK = revert_tcp_pkt(ACK)
   

def send_packet(pkt):
    print """send ____________________________________"""
    ack = sr1(pkt, iface=interface)

def is_tcp(pkt):
    return pkt.haslayer(TCP) == 1

def handle_tcp_fin(pkt):
    s=revert_tcp_pkt(pkt)
    s[TCP].flags="FA"
    s[TCP].ack+=1
    s.show()
    sendp(s, iface=interface)

def handle_tcp_pkt(pkt):
    if pkt[TCP].flags == tcp_flag_vals["S"] :
        print """handle tcp syn"""
        tcp_syn_handle(pkt)
    elif pkt[TCP].flags == tcp_flag_vals["A"] :
        print """handle tcp ack"""
    elif pkt[TCP].flags & tcp_flag_vals["F"] :
        print """handle tcp fin"""
        handle_tcp_fin(pkt)
    elif pkt[TCP].flags & tcp_flag_vals["R"] :
        print """Ignore tcp RST"""
    else :
        handle_tcp_data(pkt)

def monitor_callback(pkt):
    print """receive ____________________________________"""
    #pkt.show()
    #print pkt[TCP].flags
    if is_tcp(pkt):
       handle_tcp_pkt(pkt)
    else :
       print """not support packet!!!!!!!!!!!!!"""

def play(pkts):
    ip=IP(dst=address)
    sport=randint(1025,65535)
    SYN=ip/TCP(sport=sport, dport=port, flags="S", seq=42)
    SYNACK=sr1(SYN)
    ACK=ip/TCP(sport=SYNACK.dport, dport=port, flags="A", seq=SYNACK.ack, ack=SYNACK.seq + 1)
    seq = ACK.seq
    ack = ACK.ack
    send(ACK)

    for index, p in enumerate(pkts):
        if [p[IP].src, p[TCP].sport] == ['192.168.56.1', 33688]:
            if has_load(p): 
              print p.load
              '''
              p[IP].src='150.236.225.96'
              p[TCP].sport=23456
              p[IP].dst=address
              p[TCP].dport=port
              '''
              s = IP(dst=address)/TCP(dport=port,sport=sport, seq=seq, ack=ack, flags="PA")/p.load
              s.show()
              ACK = sr1(s, timeout=30)
              ACK.show()
              seq = ACK.ack
              ack = ACK.seq
              for a in ACK:
                if has_load(a): print 'Got response:', a.load

def replace_pkt_header(pkt, tobes, to):
    for tobe in tobes:
        ori = tobe.split(":")
        if (pkt[IP].src == ori[0] and pkt[TCP].sport == int(ori[1])):
            pkt[IP].src = to[0]
            pkt[TCP].sport = to[1]
        elif (pkt[IP].dst == ori[0] and pkt[TCP].dport == int(ori[1])):
            pkt[IP].dst = to[0]
            pkt[TCP].dport = to[1]
    return pkt 

conf={}
caps=[]
matchers=[]

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print __doc__
        exit(0)

    try:
        cmdlineOptions, args= getopt.getopt(sys.argv[1:],'hp:i:a:m:f:r:w:t:',
            ["help","port","interface","address","mode","file","replace","welcome","protocol"])
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
        elif  optName in ("-m","--mode"):
            mode = optValue
            conf['mode'] = mode
        elif  optName in ("-f","--file"):
            caps.append(optValue.split(','))
        elif  optName in ("-r","--replace"):
            replace = optValue.split(",")
        elif  optName in ("-w","--welcome"):
            welcome = optValue.decode("string_escape")
        elif  optName in ("-t","--protocol"):
            if ':' in optValue:
              [p, pconf] = optValue.split(':', 1)
              protocol = __import__('matcher.' + p, fromlist=['*'])
              protocol.config(pconf)
            else:
              protocol = __import__('matcher.' + optValue, fromlist=['*'])
            
    if 'protocol' not in locals():
      protocol = __import__('pcap.raw', fromlist=['*'])

    print 'Run as', mode, 'mode'
    print 'Decode packet as ', protocol
    print "replace ", replace, "to", [address,port]

    for cap in caps:
        f,opts = cap[0],cap[1:]
        m_conf = conf.copy()
        for opt in opts:
          if opt == "wrap":
            m_conf["wrap"] = True
        pkts = [replace_pkt_header(pkt, replace, [address,int(port)]) for pkt in rdpcap(f)]
        print "pcap file :", f, "contains", len(pkts), "packets"
        for index, pkt in enumerate(pkts):
          if has_load(pkt):
            print index, [pkt[IP].src,pkt[TCP].sport], "->", [pkt[IP].dst,pkt[TCP].dport], " load:", repr(pkt.load)
        matchers.append(PcapMatcher(pkts, m_conf, protocol))

    if mode == "server":
        sniff(prn=lambda x : monitor_callback(x), filter="dst port %d and dst host %s" % (port, address), iface=interface, store=0)
    elif mode == "client":
        play(pkts)

