#!/usr/bin/env python

import cisco
import sys

__author__ = "Sivakumar Sukumar"
__email__ = "sivaksiv@cisco.com"
__copyright__ = "Copyright (c) 2018 Cisco Systems. All rights reserved."
__credits__ = ["Sivakumar Sukumar",]
__license__ = """

################################################################################
# Copyright (c) 2018 Cisco and/or its affiliates.
#
# This software is licensed to you under the terms of the Cisco Sample
# Code License, Version 1.0 (the "License"). You may obtain a copy of the
# License at
#
#                https://developer.cisco.com/docs/licenses
#
# All use of the material herein must be in accordance with the terms of
# the License. All rights not expressly granted by the License are
# reserved. Unless required by applicable law or agreed to separately in
# writing, software distributed under the License is distributed on an "AS
# IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied.
################################################################################
"""

def main(process):

    ptp_cpu = cisco.nxcli.nxcli(str='sh proc cpu | i '+process)
    ptp_mem = cisco.nxcli.nxcli(str='sh proc mem | i '+process)

    for m in ptp_mem:
        if process in str(m):
            mem_line = m
    for c in ptp_cpu:
        if process in str(c):
            cpu_line = c

    msplit = mem_line.split()
    csplit = cpu_line.split()

    mem = msplit[3]
    cpu = csplit[4]

    cisco.nxcli.nxcli(str='syslog priority notifications msg for '+process+' mem: '+mem +' and cpu ' + cpu, do_print=False)
    
    return

if __name__ == "__main__":
   main(sys.argv[1])
