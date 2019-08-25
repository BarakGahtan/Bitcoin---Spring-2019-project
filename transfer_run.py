import bitcoin_core_connection_setup
import key_generator
import os
import shutil
import subprocess
import subprocess
import time
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
    hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {destination:amount,source_address:50-amount})
    param_input = [{"txid": txid_number, "vout": 0,"scriptPubKey": scriptPubKey}]
    signed = connection1.signrawtransactionwithkey(hash_to_be_sent,source_private_key,param_input)
    print(signed)
    signed_hex = signed.get("hex")
    return connection1.sendrawtransaction(signed_hex)


if process_exists('bitcoind.exe'):
    os.system('TASKKILL /F /IM bitcoind.exe')
time.sleep(3)

myfolder1 = "C:\\Users\\gahta\\AppData\\Roaming\\Bitcoin\\regtest"
if os.path.exists(myfolder1):
    shutil.rmtree(myfolder1)
subprocess.Popen(["C:\\Program Files\\Bitcoin\\daemon\\bitcoind.exe", "-regtest","-deprecatedrpc=generate"])
#os.popen('C:\\Program Files\\Bitcoin\\daemon\\bitcoind.exe -regtest -deprecatedrpc=generate &')
time.sleep(7)


A = key_generator.Person()
A.key_generator_func()
B = key_generator.Person()
B.key_generator_func()
D = key_generator.Person()
D.key_generator_func()
connection1 = bitcoin_core_connection_setup.connect_to_node()

##generating blocks for each of A and D, and the enviroment
generate_struct_A = connection1.generatetoaddress(1,A.address)
generate_struct_D = connection1.generatetoaddress(1,D.address)
generate_struct_B = connection1.generatetoaddress(1,B.address)
generate_enviroment = connection1.generate(100)
id_of_block_A = generate_struct_A[0]
id_of_block_D = generate_struct_D[0]
id_of_block_B = generate_struct_B[0]
##generate the address for the multisig
multi_A_D_public_keys=[]
multi_A_D_public_keys.append(A.public_key)
multi_A_D_public_keys.append(D.public_key)

multi_A_D_private_keys=[]
multi_A_D_private_keys.append(A.private_key)
multi_A_D_private_keys.append(D.private_key)
redeem_script_A = []
redeem_script_A.append(generate_struct_A[0])

#send_A_to_A_D = send_to_address(A.address,A.private_key,id_of_block_A,A_D_address,25)
#send_D_to_A_D = send_to_address(D.address,D.private_key,id_of_block_D,A_D_address,25)
send_A_to_B  =  send_to_address(A.address,A.private_key,id_of_block_A,B.address,25)

A_D_struct = connection1.addmultisigaddress(2,multi_A_D_private_keys)
A_D_address = A_D_struct.get("address")

redeem_script = A_D_struct.get("redeemScript")

generate_struct = connection1.generatetoaddress(101,A_D_address)
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
signed = connection1.signrawtransactionwithkey(hash_to_be_sent,multi_A_D_private_keys,param_input)
print(signed)
signed_hex = signed.get("hex")
send = connection1.sendrawtransaction(signed_hex)
print(send)
print("DONE")
