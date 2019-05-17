import bitcoin_core_connection_setup
import connection

connection = bitcoin_core_connection_setup.connect_to_node()
connection.stop()




