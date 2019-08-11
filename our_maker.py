import bitcoin_core_connection_setup
import key_generator
import string
import connection
import ecdsa

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
#address_multi = connection1.addmultisigaddress()
connection1.generatetoaddress(1,address_lior)
address_lior = "lalla"+address_lior
print("lior address:",address_lior)
print("lior private key:",priv_key_lior)
print("barak address:",address_barak)
print("barak private key:",priv_key_barak)
print(connection1.generate(100))
print("total balance:",connection1.getbalance())
unspent = connection1.listunspent(1,999999,address_lior)
#unspent_txid = get_tx_id(unspent)
print("unspent:",unspent)
txid_lior_block = "a9d4599e15b53f3eb531608ddb31f48c695c3d0b3538a6bda871e8b34f2f430c"
connection1.createrawtransaction([{"txid": txid_lior_block,
                  "vout": 0}],
               {address_barak:40})
print("barak balance:", connection1.getreceivedbylabel("barak",0))
print("unspent:",connection1.listunspent(1,999999))
print("total balance:",connection1.getbalance())
print(connection1.listunspent())
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
