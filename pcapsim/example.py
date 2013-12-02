#!/usr/bin/env python

from scapy.all import *
from scapy.utils import rdpcap

global pkts, index
index=1

def tcp_syn_handle(pkt): 
    eth=Ether(src=pkt[Ether].dst, dst=pkt[Ether].src)
    ip=IP(dst=pkt[IP].src, src=pkt[IP].dst)
    tcp=TCP(sport=pkt[TCP].dport, dport=pkt[TCP].sport, flags="SA", options=pkt[TCP].options)
    tcp.ack = pkt[TCP].seq + 1
    tcp.seq = 0
    s=eth/ip/tcp
    s.show()   
    ack=sr1(s)
    ack.show

def monitor_callback(pkt):
     global index, pkts
     print """receive ____________________________________"""
     pkt.show()

     print """____________________________________"""
     print pkt[TCP].flags
     if pkt[TCP].flags == 0x2 :
         print """handle tcp syn"""
         tcp_syn_handle(pkt)

     
     """
     print "send ____________________________________"
     print index
     s=pkts[index]
     s[Ether].src=pkt[Ether].dst
     s[Ether].dst=pkt[Ether].src

     s[IP].src=pkt[IP].dst
     s[IP].dst=pkt[IP].src

     s[TCP].sport=pkt[TCP].dport
     s[TCP].dport=pkt[TCP].sport
     s[TCP].ack=pkt[TCP].seq
     s.show()
     sendp(s)

     index+=2
     """

pkts=rdpcap("test/http.pcap")  # could be used like this rdpcap("filename",500) fetches first 500 pkts
for pkt in pkts:
     print """____________________________________"""
     #pkt.show()
     #pkt[Ether].src= new_src_mac  # i.e new_src_mac="00:11:22:33:44:55"
     #pkt[Ether].dst= new_dst_mac
     #pkt[IP].src= new_src_ip # i.e new_src_ip="255.255.255.255"
     #pkt[IP].dst= new_dst_ip
     #sendp(pkt) #sending packet at layer 2

sniff(prn=lambda x : monitor_callback(x), filter="dst port 3080 and dst host 127.0.0.1", iface="lo", store=0)
