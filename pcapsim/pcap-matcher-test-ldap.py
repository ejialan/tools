#!/usr/bin/env python

import unittest
from scapy.all import *
from scapy.utils import rdpcap
from pcap.matcher import *

protocol = __import__('pcap.ldap', fromlist=['*'])

class TestPcapMatcher(unittest.TestCase):
  def setUp(self):
    c = "192.168.56.100"
    s = "150.236.225.96"
    cp = 52962
    sp = 5000

    pc = IP(src=c,dst=s)/TCP(sport=cp,dport=sp)
    ps = IP(src=s,dst=c)/TCP(sport=sp,dport=cp)
    c_ack = IP(src=c,dst=s)/TCP(sport=cp,dport=sp,flags="A")
    s_ack = IP(src=s,dst=c)/TCP(sport=sp,dport=cp,flags="A")

    '''ldap login sequence, the message id is 1'''
    pkts = [pc/"\x30\x28\x02\x01\x01\x60\x23\x02\x01\x03\x04\x14cn=Directory Manager\x80\x08password",
            ps/"\x30\x0c\x02\x01\x01\x61\x07\n\x01\x00\x04\x00\x04\x00",
           ]
    self.conf = {'address':s, 'port':sp, 'protocol':'ldap'}
    self.matcher = PcapMatcher(pkts, self.conf, protocol) 

  def test_match(self):
    '''ldap login request, the message id is 2'''
    recevied="\x30\x28\x02\x01\x02\x60\x23\x02\x01\x03\x04\x14cn=Directory Manager\x80\x08password"
    pkt=IP(src='192.56.118.76', dst=self.conf['address'])/TCP(sport=1234, dport=self.conf['port'])/recevied
    res=self.matcher.match(pkt)
    self.assertEqual(1, len(res))
    self.assertEqual("\x30\x0c\x02\x01\x02\x61\x07\n\x01\x00\x04\x00\x04\x00", res[0].load)

if __name__ == '__main__':
  unittest.main()
