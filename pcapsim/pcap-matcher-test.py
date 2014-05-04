#!/usr/bin/env python

import unittest
from scapy.all import *
from scapy.utils import rdpcap
from pcap.matcher import *

protocol = __import__('pcap.raw', fromlist=['*'])

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

    pkts = [ps/"USERCODE:",
            pc/"\xff\xfe\x01",
            ps/"\xff\xfc\x01",
            pc/"\xff\xfb\x03ema\r\n",
            ps/"\r\n",
            ps/"PASSWORD : ",
            pc/"ema001\r\n",
            s_ack,
            ps/"\r\n",
            c_ack,
            ps/"DOMAIN: ",
            c_ack,
            pc/"\r\n",
            ps/"\r\n",
            ps/"WO      PAGE 1\r\n\x03<",
            pc/"\r\n",
            ps/"\r\n",
            pc/"last one to test wrap option",
           ]
    self.conf = {'address':s, 'port':sp}
    self.matcher = PcapMatcher(pkts, self.conf, protocol) 

  def test_match_multi_conn(self):
    #first connection
    pkt=IP(src='192.56.118.76', dst=self.conf['address'])/TCP(sport=1234, dport=self.conf['port'])/"ema001\r\n"
    res=self.matcher.match(pkt)
    self.assertEqual(2, len(res))
    self.assertEqual("\r\n", res[0].load)
    self.assertEqual("DOMAIN: ", res[1].load)

    #second connection
    pkt=IP(src='127.0.0.1', dst=self.conf['address'])/TCP(sport=4567, dport=self.conf['port'])/"ema001\r\n"
    res=self.matcher.match(pkt)
    self.assertEqual(2, len(res))
    self.assertEqual("\r\n", res[0].load)
    self.assertEqual("DOMAIN: ", res[1].load)

  def test_match_till_end(self):
    pkt=IP(src='192.56.118.76', dst=self.conf['address'])/TCP(sport=1234, dport=self.conf['port'])/"\r\n"
    res=self.matcher.match(pkt)
    self.assertEqual(2, len(res))
    self.assertEqual("\r\n", res[0].load)
    self.assertEqual("WO      PAGE 1\r\n\x03<", res[1].load)

    #second requet from same connection
    res=self.matcher.match(pkt)
    self.assertEqual(1, len(res))
    self.assertEqual("\r\n", res[0].load)

  def test_match_wrap(self):
    self.matcher.conf['wrap']=True
    
    self.test_match_till_end()
    self.test_match_till_end()

if __name__ == '__main__':
  unittest.main()
