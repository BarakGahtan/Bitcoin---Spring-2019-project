import bitcoin_core_connection_setup
import key_generator

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
print(connection1.getblockcount())
multi_public_keys=[]
multi_public_keys.append(lior.public_key)
multi_public_keys.append(barak.public_key)
multi_private_keys=[]
multi_private_keys.append(lior.private_key)
multi_private_keys.append(barak.private_key)
multi_struct = connection1.addmultisigaddress(2,multi_public_keys)
redeem_script = multi_struct.get("redeemScript")
multi_address = multi_struct.get("address")
connection1.setlabel(multi_address,"multi")
print(multi_address)

generate_struct = connection1.generatetoaddress(101,multi_address)
first_txid = generate_struct[0]
list = [multi_address]
print("total balance:",connection1.getbalance())
unspent = connection1.listunspent(1,999999,list)

#unspent_txid = unspent[0]
block_struct = connection1.getblock(first_txid,2)
txid_struct = block_struct.get("tx")
txid_number = txid_struct[0].get("txid")
txid_scriptPubKey = txid_struct[0].get("scriptPubKey")
#txid_multi_block = unspent_txid[0].get("txid")
#print("unspent:",txid_multi_block)
hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_number, "vout": 0}], {itay.address:40})
param_input = [{"txid": txid_number, "vout": 1,"scriptPubKey": txid_scriptPubKey, "redeemScript": redeem_script }]
signed = connection1.signrawtransactionwithkey(hash_to_be_sent,param_input,multi_private_keys)
print(signed)
print("fff")

#print("itay balance:", connection1.getreceivedbylabel("itay",0))

"""
address_lior = connection1.getnewaddress("lior")
address_barak = connection1.getnewaddress("barak")
connection1.generatetoaddress(1,address_lior)
print("lior address:",address_lior)
print("barak address:",address_barak)
print(connection1.generate(100))
print("total balance:",connection1.getbalance())
print("unspent:",connection1.listunspent(1,999999))
print("txid of transaction:",connection1.sendtoaddress(address_barak,40))
print("barak balance:", connection1.getreceivedbylabel("barak",0))
print("unspent:",connection1.listunspent(1,999999))
print("total balance:",connection1.getbalance())
print(connection1.listunspent())
print("txid of transaction:",connection1.sendtoaddress(address_barak,8))
print("barak balance:", connection1.getreceivedbylabel("barak",0))
"""




#(connection1.getbalance("mkZBYBiq6DNoQEKakpMJegyDbw2YiNQnHT"))
print(connection1.getblockcount())
