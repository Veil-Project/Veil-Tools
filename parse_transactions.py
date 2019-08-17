#!/usr/bin/python3
import json, requests, pprint, pickle, logging, sys, os

def get_block(blockhash):
    response = os.popen(veild_path+' getblock '+blockhash).read() # Block 318,879
    return(response)

def get_tx(tx_id):
    response = os.popen(veild_path+' getrawtransaction '+tx_id+' true').read()
    return(response)

def parse_transaction(transaction):
    if 'coinbase'  in transaction['vin'][0]:
        print(str(tx)+' is a coinbase transaction')
    elif 'type' not in transaction['vin'][0]:
        print(str(tx)+' is a basecoin or stealth spend')
    elif transaction['vin'][0]['type'] == 'anon':
        print(str(tx)+' is a RingCT spend')
    elif transaction['vin'][0]['type'] == 'zerocoinspend':
        #Check for CoinStake in output 0
        if transaction['vout'][1]['scriptPubKey']['type'] == 'zerocoinmint':
            print(str(tx)+' is a Zerocoin stake')
        elif transaction['vout'][0]['type'] == 'standard':
            print(str(tx)+' is a Zerocoin spend to basecoin')
        elif transaction['vout'][0]['type'] == 'data':
            print(str(tx)+' is a Zerocoin spend to stealth')
        else:
            logging.error(str(tx)+' is an unknown Zerocoin spend type')
    else:
        logging.error(str(tx)+' is a an unknown spend type')

veild_path = '~/Downloads/veil-1.0.3.1/bin/veil-cli'
current_hash = ''
next_hash = ''
blockchain = []

pp = pprint.PrettyPrinter(indent=4)

#print logging output to file
logging.basicConfig(level=logging.INFO,
                    filename='/home/max/logs/maxbot/parse_blocks.log',
                    format='%(asctime)s - %(levelname)s - %(message)s')

#print logging output to console
root = logging.getLogger()
root.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logging.info('Start')

response = get_block('5ce8fa0eb598022b0c4f70969c28845df1261a9c3c1e984781985825656ffdbe') # Block 318,879

#block = json.loads(response.text)
block = json.loads(response)

blockchain.append(block)

pp.pprint(block)
logging.info(block['height'])
print('block has this many transactions: '+str(len(block['tx'])))

for tx in block['tx']:
    #print(tx)
    try:
        response = get_tx(tx)
        transaction = json.loads(response)
        #pp.pprint(transaction)
        parse_transaction(transaction)
                    
    except Exception as e:
        print(e) 




try:
    while block['nextblockhash']:
    #while block['height'] > 318860:
        response = get_block(block['nextblockhash'])
        block = json.loads(response)
        logging.info(block['height'])
        for tx in block['tx']:
            #print(tx)
            try:
                response = get_tx(tx)
                transaction = json.loads(response)
                #pp.pprint(transaction)
                parse_transaction(transaction)
                            
            except Exception as e:
                print(e) 
except Exception as e:
    print(e)    

logging.info('end')

