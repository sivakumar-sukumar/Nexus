#!/usr/bin/env python

import paramiko
import sys
import time
import re
import json

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

ssh_info_list = []

def commands(ssh_dict, cmdlist,process): 
	#ssh dict should look like {'ip':'192.168.1.1','username':'admin','password':'abc123'}
	with paramiko.SSHClient() as remote_conn_pre:
		remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		remote_conn_pre.connect(ssh_dict['ip'], username=ssh_dict['username'], password=ssh_dict['password'], look_for_keys=False, allow_agent=False)
		remote_conn = remote_conn_pre.invoke_shell()
		if remote_conn.transport.is_alive():
			remote_conn.send("term len 0\n")
			time.sleep(.5)
			
		output = [remote_conn.recv(50000).decode('UTF-8')]	

		for cmd in cmdlist:
			print(cmd)
			if cmd:
				out1 = remote_conn.send("{}\n".format(cmd))
				time.sleep(.2)
				output.append(remote_conn.recv(50000).decode('UTF-8'))
			
			while remote_conn.transport.is_alive():
				time.sleep(.1)
				output.append(remote_conn.recv(50000).decode('UTF-8'))
				parse(output,process)
				#if prompt.search(output[-1]): 
				return {'msg':'completed commands on {}'.format(ssh_dict['ip']),'output':output}

	return {'msg':'session died while gathering commands on {}'.format(ssh_dict['ip']),'output':output}

def parse(output,process):
	result = []
	pid_list = []
	pid_list_clean = []
	for i in output:
		if process in i:
			result.append(i)
	for r in result:
		if 'show processes cpu' not in r:
			pid_list = r.split()
	for item in pid_list:
		pid_list_clean.append(str(item))
	for idx, val in enumerate(pid_list_clean):
		if val == process:
			kill_idx = idx - 5
	if kill_idx != None:
		for idx, val in enumerate(pid_list_clean):
			if kill_idx == idx:
				pid = val
				print("The pid for "+process+" is %s" % val)
				kill_pid(val)
			
def kill_pid(val):
	kill = 'sudo kill -9 '+val
	cmdlist = ['run bash',kill]
	print('killing process on {0} for {1}'.format(info['ip'],cmdlist))
	try:
		print(kill_process(info,cmdlist)['msg'])
		print("SUCCESS")
	except paramiko.ssh_exception.NoValidConnectionsError as e:
		print(e)
		print("PLEASE CHECK IF FEATURE BASH IS ENABLED")
			
def kill_process(ssh_dict, cmdlist):
	#ssh dict should look like {'ip':'192.168.1.1','username':'admin','password':'abc123'}
	with paramiko.SSHClient() as remote_conn_pre:
		remote_conn_pre.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		remote_conn_pre.connect(ssh_dict['ip'], username=ssh_dict['username'], password=ssh_dict['password'], look_for_keys=False, allow_agent=False)
		remote_conn = remote_conn_pre.invoke_shell()
		if remote_conn.transport.is_alive():
			remote_conn.send("term len 0\n")
			time.sleep(.5)
		output = [remote_conn.recv(50000).decode('UTF-8')]	
		for cmd in cmdlist:
			out1 = remote_conn.send("{}\n".format(cmd))
			time.sleep(.2)
		return {'msg':'completed commands on {}'.format(ssh_dict['ip']),'output':output}
			
if __name__ == '__main__':
	
	ip = raw_input("What is the ip address? ")
	user_name = raw_input("What is the username? ")
	password = raw_input("What is the password? ")
	process = raw_input("What is the process name? ")
	
	info = {
			'ip':ip,
			'username':user_name,
			'password':password,
			'enable':'cisco'}
			
	print("Please provide the process name to kill: %s." % process)
	cmdlist = ['show processes cpu | i '+process]
	
	print('running commands on {}'.format(info['ip']))
	try:
		print(commands(info,cmdlist,process)['msg'])
	except paramiko.ssh_exception.NoValidConnectionsError as e:
		print(e)
		time.sleep(5)
