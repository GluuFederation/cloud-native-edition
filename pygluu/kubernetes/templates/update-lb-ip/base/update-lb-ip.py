#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Update the IP of the load balancer automatically

"""
 License terms and conditions for Gluu Cloud Native Edition:
 https://www.apache.org/licenses/LICENSE-2.0
"""

import socket
import os
import logging
import time

logger = logging.getLogger("update-lb-ip")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fmt = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
ch.setFormatter(fmt)
logger.addHandler(ch)


def backup(hosts):
    timenow = time.strftime("%c")
    timestamp = "Backup occurred %s \n" % timenow
    logger.info("Backing up hosts file to /etc/hosts.back ...")
    with open('/etc/hosts.back', 'a+') as f:
        f.write(timestamp)
        for line in hosts:
            f.write(line)


def get_hosts(lb_addr, domain):
    ip_list = []
    hosts_list = []
    ais = socket.getaddrinfo(lb_addr, 0, 0, 0, 0)
    for result in ais:
        ip_list.append(result[-1][0])
    ip_list = list(set(ip_list))
    for ip in ip_list:
        add_host = ip + " " + domain
        hosts_list.append(add_host)

    return hosts_list


def main():
    try:
        while True:
            lb_addr = os.environ.get("LB_ADDR", "")
            domain = os.environ.get("DOMAIN", "demoexample.gluu.org")
            host_file = open('/etc/hosts', 'r').readlines()
            hosts = get_hosts(lb_addr, domain)
            stop = []
            for host in hosts:
                for i in host_file:
                    if host.replace(" ", "") in i.replace(" ", ""):
                        stop.append("found")
            if len(stop) != len(hosts):
                backup(host_file)
                logger.info("Writing new hosts file")
                with open('/etc/hosts', 'w') as f:
                    for line in host_file:
                        if domain not in line:
                            f.write(line)
                    for host in hosts:
                        f.write(host)
                        f.write("\n")
                    f.write("\n")
            time.sleep(300)
    except KeyboardInterrupt:
        logger.warning("Canceled by user; exiting ...")


if __name__ == "__main__":
    main()
