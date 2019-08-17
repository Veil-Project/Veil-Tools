#!/usr/bin/python3
import json, requests, pprint, pickle, logging, sys, os

def get_block(blockhash):
    response = os.popen(veild_path+' getblock '+blockhash).read()
    return(response)

def get_tx(tx_id):
    response = os.popen(veild_path+' getrawtransaction '+tx_id+' true').read()
    return(response)

def parse_transaction(transaction):
    denoms = []
    outputs = []
    if 'coinbase' in transaction['vin'][0]:
        #print(str(tx)+' is a coinbase transaction')
        pass
    
    elif 'type' not in transaction['vin'][0]:
        #print(str(tx)+' is a basecoin or stealth spend')
        pass
    
    elif transaction['vin'][0]['type'] == 'anon':
        #print(str(tx)+' is a RingCT spend')
        pass
    
    elif transaction['vin'][0]['type'] == 'zerocoinspend':
        #print(str(tx)+' is a Zerocoin spend of some kind')

        if len(transaction['vout']) > 1:
            if transaction['vout'][1]['scriptPubKey']['type'] == 'zerocoinmint':
                #print(str(tx)+' is a Zerocoin stake, ignoring')
                pass
                return([], [])
        
        if transaction['vout'][0]['type'] == 'standard':
            #print(str(tx)+' is a Zerocoin spend to basecoin')
            for vinput in transaction['vin']:
                if 'denomination' in vinput:
                    denoms.append(vinput['denomination'])
            for output in transaction['vout']:
                if 'scriptPubKey' in output:
                    if len(output['scriptPubKey']['addresses']) > 1:
                        logging.error(str(tx)+' has more than 1 output per vout')
                    outputs.append(output['scriptPubKey']['addresses'][0])
                
        elif transaction['vout'][0]['type'] == 'data':
            #print(str(tx)+' is a Zerocoin spend to stealth')
            for vinput in transaction['vin']:
                if 'denomination' in vinput:
                    denoms.append(vinput['denomination'])
            for output in transaction['vout']:
                if 'scriptPubKey' in output:
                    if len(output['scriptPubKey']['addresses']) > 1:
                        logging.error(str(tx)+' has more than 1 output per vout')
                    outputs.append(output['scriptPubKey']['addresses'][0])
        else:
            logging.error(str(tx)+' is an unknown Zerocoin spend type')
            
    else:
        logging.error(str(tx)+' is a an unknown spend type')

    #print(outputs)
    return(denoms, outputs)


veild_path = '~/Downloads/veil-1.0.3.1/bin/veil-cli'
current_hash = ''
next_hash = ''
blockchain = []
transaction_list = []
outputs = []
zcspends = []

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



#Get first block
#response = get_block('a4063911700f37629bef105f66c088002bca439a2a2f009eadd9988aa9361a7f') # Block 100,000
response = get_block('2fbff4d1d89649c1949c90b894a9187cb64250a6c0b5cf3dc4c432c2d668a62c') # Block custom
#response = get_block('5ce8fa0eb598022b0c4f70969c28845df1261a9c3c1e984781985825656ffdbe') # Block custom
#response = get_block('76402912b3c88deb9493413d3195309a48c116ea37bfabe47deb306fff4eef84') # Block 318,224

#block = json.loads(response.text)
block = json.loads(response)

blockchain.append(block)

pp.pprint(block)
logging.info(block['height'])
print('block has this many transactions: '+str(len(block['tx'])))

for tx in block['tx']:
    print(tx)
    denoms = []
    outputs = []
    try:
        response = get_tx(tx)
        transaction = json.loads(response)
        #pp.pprint(transaction)
        denoms, outputs = parse_transaction(transaction)
        if len(outputs) > 0:
            print(str(block['height'])+'|'+str(tx)+'|'+str(denoms)+'|'+str(outputs))
            zcspends.append(str(block['height'])+'|'+str(tx)+'|'+str(denoms)+'|'+str(outputs))
    except Exception as e:
        print(e) 


#Get subsequent blocks
try:
    while 'nextblockhash' in block:
        #break
    #while block['height'] > 318860:
        denoms = []
        outputs = []
        response = get_block(block['nextblockhash'])
        block = json.loads(response)
        #logging.info(block['height'])
        for tx in block['tx']:
            #print(tx)
            try:
                response = get_tx(tx)
                transaction = json.loads(response)
                #pp.pprint(transaction)
                denoms, outputs = parse_transaction(transaction)
                if (len(denoms) > 0) or (len(outputs) > 0):
                    print(str(block['height'])+'|'+str(tx)+'|'+str(denoms)+'|'+str(outputs))
                    zcspends.append(str(block['height'])+'|'+str(tx)+'|'+str(denoms)+'|'+str(outputs))
                    
            except Exception as e:
                print(e) 
except Exception as e:
    print(e)    

logging.info('end')

##try:
##    with open('zcspends.obj', "wb") as f:
##        pickle.dump(zcspends, f)
##except Exception as e:
##    print(e)

with open('zcspends.txt', 'w') as f:
    for item in zcspends:
        f.write("%s\n" % item)
