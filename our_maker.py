import bitcoin_core_connection_setup
import key_generator
A = key_generator.Person()
A.key_generator_func()
B = key_generator.Person()
B.key_generator_func()

connection1 = bitcoin_core_connection_setup.connect_to_node()
print(connection1.getblockcount())


address_lior = connection1.getnewaddress("lior")
priv_key_lior = connection1.dumpprivkey(address_lior)
address_barak = connection1.getnewaddress("barak")
priv_key_barak = connection1.dumpprivkey(address_barak)
itay_address = connection1.getnewaddress("itay")
priv_itay = connection1.dumpprivkey(itay_address)

array_addresses=[]
array_addresses.append(address_barak)
array_addresses.append(address_lior)
multi_address = connection1.addmultisigaddress(2,array_addresses).get("address")
multi_key = connection1.dumpprivkey(multi_address)
print(multi_address)
connection1.generatetoaddress(1,multi_address)

list = [multi_address]
print("lior address:",address_lior)
print("lior private key:",priv_key_lior)
print("barak address:",address_barak)
print("barak private key:",priv_key_barak)
print(connection1.generate(100))
print("total balance:",connection1.getbalance())
unspent = connection1.listunspent(1,999999,list)
unspent_txid = unspent[0]
txid_multi_block = unspent_txid[0].get("txid")
print("unspent:",txid_multi_block)


hash_to_be_sent = connection1.createrawtransaction([{"txid": txid_multi_block, "vout": 0}], {itay_address:40})
signed = connection1.signrawtransactionwithkey(hash_to_be_sent,multi_key)
print(signed)
print("itay balance:", connection1.getreceivedbylabel("itay",0))
#print("unspent:",connection1.listunspent(1,999999))
print("total balance:",connection1.getbalance())
#print(connection1.listunspent())
print("txid of transaction:",connection1.sendtoaddress(address_barak,8))
print("barak balance:", connection1.getreceivedbylabel("barak",0))

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
