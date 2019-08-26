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

def send_to_address(source_address,source_private_key,block_id,destination,amount):
    block_struct = connection1.getblock(block_id,2)
    txid_struct = block_struct.get("tx")
    txid_number = txid_struct[0].get("txid")
    vout_struct = txid_struct[0].get("vout")
    txid_scriptPubKey = vout_struct[0].get("scriptPubKey")
    scriptPubKey = txid_scriptPubKey.get("hex")
    hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {destination:25,source_address:24.95})
    param_input = [{"txid": txid_number, "vout": 1,"scriptPubKey": scriptPubKey}]
    private_keys =[]
    private_keys.append(source_private_key)
    signed = connection1.signrawtransactionwithkey(hash_to_be_sent, private_keys,param_input)
    print(signed)
    hex_hash_sign = signed.get("hex")
    result = connection1.sendrawtransaction(hex_hash_sign)
    return result


if process_exists('bitcoind.exe'):
    os.system('TASKKILL /F /IM bitcoind.exe')
time.sleep(3)

myfolder1 = "C:\\Users\\gahta\\AppData\\Roaming\\Bitcoin\\regtest"
if os.path.exists(myfolder1):
    shutil.rmtree(myfolder1)
subprocess.Popen(["C:\\Program Files\\Bitcoin\\daemon\\bitcoind.exe", "-regtest","-deprecatedrpc=generate"])
time.sleep(7)





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

#send_A_to_A_D = send_to_address(A.address,A.private_key,id_of_block_A,A_D_address,25)
#send_D_to_A_D = send_to_address(D.address,D.private_key,id_of_block_D,A_D_address,25)
send_A_to_B  =  send_to_address(A.address,A.private_key,idBlockA,B.address,25)

structAD = connection1.addmultisigaddress(2,ADPrivateKeys)
addressAD = structAD.get("address")

redeem_script = structAD.get("redeemScript")

generate_struct = connection1.generatetoaddress(101,addressAD)
id_of_block = generate_struct[0]
print("total balance:",connection1.getbalance())

block_struct = connection1.getblock(id_of_block,2)
txid_struct = block_struct.get("tx")
txid_number = txid_struct[0].get("txid")
vout_struct = txid_struct[0].get("vout")
txid_scriptPubKey = vout_struct[0].get("scriptPubKey")
scriptPubKey = txid_scriptPubKey.get("hex")

hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {itay.address:49.95})
param_input = [{"txid": txid_number, "vout": 1,"scriptPubKey": scriptPubKey, "redeemScript": redeem_script }]
signed = connection1.signrawtransactionwithkey(hash_to_be_sent,ADPrivateKeys,param_input)
print(signed)
signed_hex = signed.get("hex")
send = connection1.sendrawtransaction(signed_hex)
print(send)
print("DONE")
