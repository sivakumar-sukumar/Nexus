#!/usr/bin/python
# -*- coding: utf-8 -*-
 
import sys
from cli import *
import cisco

def main(argv):
    if (len(argv)) != 2:
        print("Not enough arguments")
        return
    if argv[0]:
         process = argv[0]
    if argv[1]:
         mem_lim = argv[1]
     
    ptp_mem = cisco.nxcli.nxcli(str='sh proc mem | i '+process)

    for m in ptp_mem:
        if process in str(m):
            print(process)
            mem_line = m

    msplit = mem_line.split()

    mem = int(msplit[3])
    print(mem)
    pid = get_pid(process)
    pid = pid.replace("'",'')
    print(pid)
    if mem != 0:
        if int(mem) > int(mem_lim):
            print("KILLING PROCESS")
            #cisco.nxcli.nxcli(str='syslog priority notifications msg for '+process+' mem: '+mem +' and cpu ' + cpu, do_print=False)
            cisco.nxcli.nxcli(str='syslog priority notifications msg Killing '+str(process)+' mem: '+str(mem), do_print=False)
            cli('run bash sudo kill -6 '+pid)
            return

    return

def get_pid(process):
    cpu = cisco.nxcli.nxcli(str='sh proc cpu | i '+str(process))
    cpu1 = str(cpu).replace('\\n',' ')
    cpu2 = " ".join(cpu1.split())
    cpu2 = cpu2.split()
    print(cpu2)
    for idx, val in enumerate(cpu2):
        if val == process:
            kill_idx = idx - 5
    if kill_idx != None:
        for idx, val in enumerate(cpu2):
            if kill_idx == idx:
                return val

if __name__ == '__main__':
 
    # exclude script name from the argumemts list and pass it to main()
    main(sys.argv[1:])
