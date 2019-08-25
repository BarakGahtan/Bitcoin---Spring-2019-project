import bitcoin_core_connection_setup
import key_generator
import os
import shutil
import subprocess

os.system('TASKKILL /F /IM bitcoind.exe')
myfolder1 = "C:\\Users\\LIORD\\AppData\\Roaming\\Bitcoin\\regtest"
# myfolder2 = "C:\\Users\\gahta\\AppData\\Roaming\\Bitcoin\\regtest"
if os.path.exists(myfolder1):
    shutil.rmtree(myfolder1)
os.popen('C:\Program Files\Bitcoin\daemon\bitcoind.exe -regtest -deprecatedrpc=generate')

lior = key_generator.Person()
lior.key_generator_func()
barak = key_generator.Person()
barak.key_generator_func()
itay = key_generator.Person()
itay.key_generator_func()

connection1 = bitcoin_core_connection_setup.connect_to_node()
connection1.setlabel(lior.address,"lior")
connection1.setlabel(lior.address,"barak")
connection1.setlabel(lior.address,"itay")


print("Block count:", connection1.getblockcount())
multi_public_keys=[]
multi_public_keys.append(lior.public_key)
multi_public_keys.append(barak.public_key)

multi_private_keys=[]
multi_private_keys.append(lior.private_key)
multi_private_keys.append(barak.private_key)

multi_struct = connection1.addmultisigaddress(2,multi_public_keys)
multi_address = multi_struct.get("address")
print(multi_address)
connection1.setlabel(multi_address,"multi")

redeem_script = multi_struct.get("redeemScript")
generate_struct = connection1.generatetoaddress(101,multi_address)
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
signed = connection1.signrawtransactionwithkey(hash_to_be_sent,multi_private_keys,param_input)
print(signed)
signed_hex = signed.get("hex")
send = connection1.sendrawtransaction(signed_hex)
print(send)
print("DONE")
