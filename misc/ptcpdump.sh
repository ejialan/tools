#!/bin/sh

ports=`netstat -nap | grep $1 | grep LISTEN | grep tcp | awk '{print $4}' | sed -e s'/://g' | awk '{print "port " $1 " or"}'| tr '\n' ' ' | sed -e 's/ or $//'`
ports="($ports)"
shift
tcpdump -s 0 -X $* "$ports"

