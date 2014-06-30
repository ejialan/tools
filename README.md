tools
=============
== docker/hosts_hack.py ==
This tool is used to hack the /etc/hosts of docker containers.
The docker container linking only provides an one-way hostname resolve.
It is not inconvenient to build a cluster in which hosts need to know each others either via hostname or IP address.

This tool will listen on the docker container events. When it detects a container starts, it inspect the container to 
get the host name and IP address of the container. Then the tool add the IP and host pair into every hosts file under 
/var/lib/docker/containers.

The hack is stupid and violent. It directly change the content of hosts file outside docker container, and it is not through
docker deamon. Not sure if it does harm to the docker containers. So do not use it in product environment.

It is easy to use, just start the tool before you start any docker containers.
python hosts_hack.py
