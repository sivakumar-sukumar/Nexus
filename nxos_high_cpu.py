#!/usr/bin/env python

import sys
from cisco import cli as nxos_cli
import cisco
from datetime import datetime
import re
import time
from threading import Thread as thr
import _strptime

def main():
    print("Initializing script...")
    folder = "high-cpu"
    file_list = []
    dev_name = nxos_cli("show hostname").strip()

    try:
        nxos_cli("mkdir bootflash:{}".format(folder))
        print("Folder 'bootflash:{}' created for this instance...".format(folder))
    except cisco.cli_execution_error as exc:
        print("Folder already exists, skipping...")
    print("Removing EEM...")
    nxos_cli("conf ; no event manager applet high_cpu")
    print("Grabbing commands...")
    grab_commands(folder, file_list, dev_name)
    print("Running Ethanalyzer...")
    i = 0
    while i < 5:
        ethanalyze_inband(folder, file_list, i)
        i += 1
    print("Zipping all output...")
    create_tar(folder, file_list, dev_name)
    print("Created bootflash:///{}_{}.tar".format(folder, dev_name))
    print("Deleting unzipped files...")
    delete_files(folder, file_list)
    sys.exit()

def ethanalyze_inband(folder, file_list, i):
    filename = "ethanalyzer_inband_{}.pcap".format(i)
    nxos_cli("ethanalyzer local interface inband limit-captured-frames 100000 write bootflash:{}/{}".format(folder, filename))
    file_list.append(filename)

def create_tar(folder, file_list, hostname):
    cmd_string = "tar create bootflash:{1}_{0}.tar bootflash:{1}/{2}".format(hostname, folder, file_list[0])
    #print("[TAR] Running command: {}".format(cmd_string))
    nxos_cli(cmd_string)
    for filename in file_list[1:]:
        print("Adding {} to tar".format(filename))
        cmd_string = "tar append bootflash:{1}_{0}.tar bootflash:{1}/{2}".format(hostname, folder, filename)
        #print("[TAR] Running command: {}".format(cmd_string))
        nxos_cli(cmd_string)

def delete_files(folder, file_list):
    for file in file_list:
        print("\tDeleting {}".format(file))
        nxos_cli("delete bootflash:{}/{} no-prompt".format(folder, file))

def grab_commands(folder, file_list, hostname):
    cmd_list = [
        "show logging log",
        "show logging nvram",
        "show accounting log",
        "show span det | i ieee|occur|exec|from",
        "show spanning-tree internal event-history all brief",
        "show spanning-tree detail",
        "show cdp neigh",
        "show port-c sum",
        'sh clock ; sh int counter err | egrep "Port|--|\B [1-9]" | egrep -v "\ 0\ *--\ *0\ *0\ *0\ *0"',
        "show interface | i i rx|tx|unicast|rate|is.up|Eth|port-channel|vlan",
        "show interface",
        "show hardware internal errors all",
        "show hardware internal statistics module-all device all",
        'show system internal pktmgr internal vdc inband | ex "In VDC"',
        "show mac add",
        "show ip route vrf all",
        "show ip arp vrf all",
        "show processes cpu sort | ex 0.0",
        "show processes cpu history",
        "show system internal mts buff detail",
        "show processes memory sort",
        "show policy-map interface control-plane | i i mod|class|violate",
        "show hardware internal cpu-mac inband stats | i i pps",
        "show hardware internal cpu-mac inband events",
        "show hardware rate-limiter",
        "show sockets connection detail",
        "show sockets connection udp detail",
        "show hardware internal eobcsw stats",
    ]
    with open("/bootflash/{}/{}-sh_cmds".format(folder, hostname), "w") as outfile:
        for cmd in cmd_list:
            outfile.write("`{}`\n".format(cmd))
            try:
                print("\tRan command: {}".format(cmd))
                cmd_output = nxos_cli(cmd)
            except cisco.cli_syntax_error:
                print("\t\tThis command did not execute due to a syntax error!")
                continue
            except cisco.cli_execution_error as exc:
                print("Exception encountered! Writing exception to file")
                for line in str(exc).splitlines():
                    outfile.write("{}\n".format(line))
                continue
            for line in cmd_output.splitlines():
                outfile.write("{}\n".format(line))
            outfile.write("\n")
    file_list.append("{}-sh_cmds".format(hostname))

if __name__ == "__main__":
    main()
