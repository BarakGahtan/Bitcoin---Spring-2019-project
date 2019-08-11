import bitcoin_core_connection_setup
import key_generator
import connection
import ecdsa

man = key_generator.Person()
man.key_generator_func()

connection1 = bitcoin_core_connection_setup.connect_to_node()

connection1.createrawtransaction([{"txid": "a9d4599e15b53f3eb531608ddb31f48c695c3d0b3538a6bda871e8b34f2f430c",
                  "vout": 0}],
                {"mkZBYBiq6DNoQEKakpMJegyDbw2YiNQnHT":50})

print(connection1.setgenerate(101))

