#!/usr/bin/env python

from scapy.all import *
from scapy.utils import rdpcap

pkts=rdpcap("test/http.pcap")  # could be used like this rdpcap("filename",500) fetches first 500 pkts
for pkt in pkts:
     print """____________________________________"""
     pkt.show()
     print ""

