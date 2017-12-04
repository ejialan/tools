#!/usr/bin/env python

from scapy.all import *
from scapy.utils import rdpcap

def monitor_callback(pkt):
     print """receive ____________________________________"""
     pkt.show()

sniff(prn=lambda x : monitor_callback(x), filter="port 3080 and host 127.0.0.1", iface="any", store=0)
