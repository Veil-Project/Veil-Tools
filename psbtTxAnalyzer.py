#!/usr/bin/python3
import os, json, sys

try:
	txjson = str(sys.argv[1])
except:
	print('Usage: python3 psbtTxAnalyzer.py sb.json')
	print('1 string argument required for this script.  Exiting...')
	sys.exit(2)

with open(txjson, "r") as read_file:
    data = json.load(read_file)

outs = data['tx']['vout']

for i in outs:
        addr = str(i['scriptPubKey']['addresses'])
        addr = addr[2:-2] # Trim special chars from address string
        #print(str(i['value']))
        print(addr+':'+str(int(i['value'])))


print()
print('You can paste the above data into a spreadsheet and use Data > Split to Columns')
