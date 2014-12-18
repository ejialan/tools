pcapsim is a tool to simulate a sever or a client based on previously captured packets.
It aims to provide the capability to quick reprocedure network issue, no need
on real network devices and no need to configure network services.
Run the tool to see detail manual.

NOTE:
1. The tool is based on scapy, a powerful interactive packet manipulation
program. Follow the instruction to install scapy,
http://www.secdev.org/projects/scapy
To be simple:
wget http://www.secdev.org/projects/scapy/files/scapy-latest.tar.gz

2. Before run this tool, you need to configure iptables as following.
# iptables -A OUTPUT -p tcp --tcp-flags RST RST -s 150.236.225.96 -j DROP
Refer to
http://stackoverflow.com/questions/9058052/unwanted-rst-tcp-packet-with-scapy
 for details.
