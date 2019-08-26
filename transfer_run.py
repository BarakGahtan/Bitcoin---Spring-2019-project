import bitcoin_core_connection_setup
import key_generator
import os
import shutil
import subprocess
import time

#helper functions#

def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call)
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def send_to_address(source_address,privateArray,block_id,destination,amount):
    block_struct = connection1.getblock(block_id,2)
    txid_struct = block_struct.get("tx")
    txid_number = txid_struct[0].get("txid")
    vout_struct = txid_struct[0].get("vout")
    txid_scriptPubKey = vout_struct[0].get("scriptPubKey")
    scriptPubKey = txid_scriptPubKey.get("hex")
    hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {destination:25,source_address:24.95})
    param_input = [{"txid": txid_number, "vout": 1,"scriptPubKey": scriptPubKey}]
    signed = connection1.signrawtransactionwithkey(hash_to_be_sent, privateArray,param_input)
    hex_hash_sign = signed.get("hex")
    result = connection1.sendrawtransaction(hex_hash_sign)
    return result

def send_from_multisig(source_address,privateArray,block_id,destination,amount):
    block_struct = connection1.getblock(block_id,2)
    txid_struct = block_struct.get("tx")
    txid_number = txid_struct[0].get("txid")
    vout_struct = txid_struct[0].get("vout")
    txid_scriptPubKey = vout_struct[0].get("scriptPubKey")
    scriptPubKey = txid_scriptPubKey.get("hex")
    hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {destination:25,source_address:24.95})
    param_input = [{"txid": txid_number, "vout": 1,"scriptPubKey": scriptPubKey, "redeemScript": redeem_script }]
    signed = connection1.signrawtransactionwithkey(hash_to_be_sent, privateArray,param_input)
    hex_hash_sign = signed.get("hex")
    result = connection1.sendrawtransaction(hex_hash_sign)
    return result

##intialize system
if process_exists('bitcoind.exe'):
    os.system('TASKKILL /F /IM bitcoind.exe')
time.sleep(3)
myPath = "C:\\Users\\gahta\\AppData\\Roaming\\Bitcoin\\regtest"
if os.path.exists(myPath):
    shutil.rmtree(myPath)
subprocess.Popen(["C:\\Program Files\\Bitcoin\\daemon\\bitcoind.exe", "-regtest","-deprecatedrpc=generate"])
time.sleep(7)

#generate key for players
A = key_generator.Person()
A.key_generator_func()
B = key_generator.Person()
B.key_generator_func()
D = key_generator.Person()
D.key_generator_func()
connection1 = bitcoin_core_connection_setup.connect_to_node()

##generating blocks for each of A and D, and the enviroment
structA = connection1.generatetoaddress(1,A.address)
structD = connection1.generatetoaddress(1,D.address)
structB = connection1.generatetoaddress(1,B.address)
generate_enviroment = connection1.generate(100)
idBlockA = structA[0]
idBlockD = structD[0]
idBlockB = structB[0]

##generate the address for the multisig - the joint account
ADpublic_keys=[]
ADpublic_keys.append(A.public_key)
ADpublic_keys.append(D.public_key)
ADPrivateKeys=[]
ADPrivateKeys.append(A.private_key)
ADPrivateKeys.append(D.private_key)
redeem_script_A = []
redeem_script_A.append(structA[0])
AprivateArray = []
AprivateArray.append(A.private_key)
info1 = connection1.getmininginfo()
send_A_to_B  =  send_to_address(A.address,AprivateArray,idBlockA,B.address,25)
info2 = connection1.getmininginfo()
print("sign")