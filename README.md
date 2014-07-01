# tools


## docker/hosts_hack.py
This tool is used to hack the /etc/hosts outside of docker containers.

The docker container linking only provides an one-way hostname resolve.
It is not inconvenient to build a cluster in which hosts need to know each other both via hostname and via IP address.

And the /etc/hosts of docker container is **read-only**. There is some ways to made it writable, but it will mess the docker container itself. 

This tool will listen on the docker container events. When it detects a container starts, it inspects the container to 
get the host name and IP address of the container. Then the tool add the IP and host pair into every hosts file under 
/var/lib/docker/containers. The hosts files under /var/lib/docker/containers are mapped to each docker container. If the content of the those hosts files changes, it will reflect to the /etc/hosts in docker container.

The hack is stupid and violent. It directly change the content of hosts file outside docker container, and it is not through
docker deamon. ***Not sure if it does harm to the docker containers***, so do not use it in product environment.

It is easy to use, just start the tool before you start any docker container.<br>
```
python hosts_hack.py
```