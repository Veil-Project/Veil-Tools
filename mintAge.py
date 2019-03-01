#!/usr/bin/python3
import os, json, sys

# !!!This file operates against an unlocked wallet!!! Did you read the every line?  
# You'll probably need to update the binary paths

try:
        confirms = int(sys.argv[1])
except:
        print('Usage: python3 mintAge.py 20000')
        print('1 integer argument required for this script.  Exiting...')
        sys.exit(2)

block = os.popen('~/Downloads/veil-1.0.2/bin/veil-cli getblockcount').read()
var = os.popen('~/Downloads/veil-1.0.2/bin/veil-cli listmintedzerocoins true').read()

if block:
    if var:
        print("Mints found")
    else:
        print("Mints not found.  Is the wallet unlocked?")
        sys.exit()
else:
    print("Veil daemon is not responding")
    sys.exit()

mints = json.loads(var)

#print(mints)

# Filter python objects with list comprehensions
output_dict = [x for x in mints if x['confirmations'] > confirms]

# Transform python object back into json
output_json = json.dumps(output_dict)

print("Here are the serial hashes for your mints with over "+str(confirms)+" confirmations")
for mint in output_dict:
    print(mint['serial hash'])

print(mintList)

print("finished")
