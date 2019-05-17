import os
import bitcoin_core_connection_setup
import os.path
import pickle

# exception handling
from bitcoinrpc.exceptions import _wrap_exception
import traceback
import platform
import time

tx_db_base_path = "/media/hdd/itay/transactions/"
bitcoin_core_rpc_connection = bitcoin_core_connection_setup.get_connection()


def is_coinbase_tx(bitcoin_raw_transaction):
    return (len(bitcoin_raw_transaction['vin']) == 1) and \
           ('coinbase' in bitcoin_raw_transaction['vin'][0]) and \
           ('txid' not in bitcoin_raw_transaction['vin'][0])


def input_amount(vin_list):
    if len(vin_list) == 1:
        assert ("coinbase" not in vin_list[0])
    inputs_sum = 0
    for current_vin in vin_list:
        input_transaction_txid = current_vin['txid']
        input_transaction_vout = current_vin['vout']
        input_tx_data = bitcoin_core_rpc_connection.getrawtransaction(input_transaction_txid, verbose=True)
        inputs_sum = inputs_sum + input_tx_data['vout'][input_transaction_vout]['value']
    return inputs_sum


def get_direct_dependencies(vin_list):
    if len(vin_list) == 1:
        assert ("coinbase" not in vin_list[0])
    return [input_tx['txid'] for input_tx in vin_list if 'txid' in input_tx]


def get_all_in_block_dependencies(bitcoin_raw_transaction, block_num):
    # print "\n\n    START OF CALL FOR    ", bitcoin_raw_transaction['txid'],"\n\n"

    in_block_dependencies_list = []

    # print "calling get_all_in_block_dependencies with",  bitcoin_raw_transaction['txid']

    direct_dependencies_ids = [input_tx['txid'] for input_tx in bitcoin_raw_transaction['vin'] if 'txid' in input_tx]

    # for current_input_tx_id in direct_dependencies_ids:
    # input_raw_transaction = bitcoin_core_rpc_connection.getrawtransaction(current_input_tx_id, verbose=True)
    # input_tx_block = get_including_block(input_raw_transaction)
    # print current_input_tx_id,"of block",input_tx_block,"is an input for",
    # bitcoin_raw_transaction['txid'],"of block",block_num

    # if (str(bitcoin_raw_transaction['txid']) == "6f929f5d61694b0439f107127409114dcc60f2732011e10db30ca8eeac2fcc11"):
    # pass
    # print len(direct_dependencies_ids)
    # assert(False)

    # for current_input_tx_id in direct_dependencies_ids:
    # input_raw_transaction = bitcoin_core_rpc_connection.getrawtransaction(current_input_tx_id, verbose=True)
    # input_tx_block = get_including_block(input_raw_transaction)
    # print current_input_tx_id,"of block",input_tx_block,"is an input for",bitcoin_raw_transaction['txid'],
    # "of block",block_num

    for current_input_tx_id in direct_dependencies_ids:
        # print "dependant tx id:",current_input_tx_id
        empty_input_transaction = Transaction(current_input_tx_id, fill_fields_flag=False)
        if empty_input_transaction.does_file_exist():
            # input transaction is in the db
            updated_input_transaction = Transaction(current_input_tx_id, fill_fields_flag=True)

            if updated_input_transaction.get_block() == block_num:
                in_block_ancestors_list = updated_input_transaction.get_total_in_block_ancestors()
                in_block_dependencies_list.append(current_input_tx_id)
                in_block_dependencies_list.extend(in_block_ancestors_list)
                in_block_dependencies_list = list(set(in_block_dependencies_list))
            continue
        else:
            # input transaction is NOT in the db

            input_raw_transaction = bitcoin_core_rpc_connection.getrawtransaction(current_input_tx_id, verbose=True)
            input_tx_block = get_including_block(input_raw_transaction)

            if input_tx_block is None:
                assert (block_num is None)
            else:
                if block_num is not None:
                    assert (int(block_num) >= int(input_tx_block))

            if (input_tx_block is None and block_num is None) or \
                    (block_num is not None and (int(block_num) == int(input_tx_block))):
                # print bitcoin_raw_transaction['txid'],"of block",block_num,"requires",
                # current_input_tx_id,"of block",input_tx_block
                # print "in_block_dependencies_list size is",len(in_block_dependencies_list)
                in_block_dependencies_list.append(current_input_tx_id)
                # print "in_block_dependencies_list size is",len(in_block_dependencies_list)

                additional_dependencies_list = get_all_in_block_dependencies(input_raw_transaction, block_num)
                # print "additional_dependencies_list size is",len(additional_dependencies_list)
                in_block_dependencies_list.extend(additional_dependencies_list)
                in_block_dependencies_list = list(set(in_block_dependencies_list))
                # print "in_block_dependencies_list size is",len(in_block_dependencies_list)

    # print "    END OF CALL FOR    ", bitcoin_raw_transaction['txid'],"\n\n"
    return list(set(in_block_dependencies_list))


def output_amount(vout_list):
    return sum([x['value'] for x in vout_list])


def get_including_block(bitcoin_raw_transaction):
    if "blockhash" in bitcoin_raw_transaction:
        block_hash = bitcoin_raw_transaction["blockhash"]
        get_block = bitcoin_core_rpc_connection.getblock(block_hash, verboseLevel=1)
        assert ("height" in get_block)
        return get_block["height"]
    else:
        return None


class Transaction:
    _txid = None
    _version = 1
    _weight = None
    _is_coin_base = None
    _inputs_sum = None
    _outputs_sum = None
    _fees = None
    _block = None
    _direct_ancestors = None
    _total_in_block_ancestors = None

    def to_string(self):
        ret_str = ""
        ret_str = ret_str + str(self._txid) + ","
        ret_str = ret_str + str(self._version) + ","
        ret_str = ret_str + str(self._weight) + ","
        ret_str = ret_str + str(self._is_coin_base) + ","
        ret_str = ret_str + str(self._inputs_sum) + ","
        ret_str = ret_str + str(self._outputs_sum) + ","
        ret_str = ret_str + str(self._fees) + ","
        ret_str = ret_str + str(self._block) + ","
        return ret_str

    def get_is_coin_base(self):
        return self._is_coin_base

    def get_txid(self):
        return self._txid

    def get_weight(self):
        return self._weight

    def get_block(self):
        return self._block

    def get_fees(self):
        return self._fees

    def get_direct_ancestors(self):
        return self._direct_ancestors

    def get_total_in_block_ancestors(self):
        return self._total_in_block_ancestors

    def get_inputs_sum(self):
        return self._inputs_sum

    def get_path_and_file_names(self):
        assert (self._txid is not None)
        file_path = self._txid[:4]
        file_name = self._txid[4:]
        return tx_db_base_path + file_path, file_name

    def get_full_path(self):
        file_path, file_name = self.get_path_and_file_names()
        return os.path.join(file_path, file_name)

    def does_file_exist(self):
        return os.path.isfile(self.get_full_path())

    def write_to_file(self):
        file_path, _ = self.get_path_and_file_names()
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        with open(self.get_full_path(), 'wb') as output:
            pickle.dump(self, output, pickle.HIGHEST_PROTOCOL)

    def delete_file(self):
        if self.does_file_exist():
            os.remove(self.get_full_path())

    def read_from_file(self):
        with open(self.get_full_path(), 'rb') as input_file:
            read_transaction = pickle.load(input_file)
            self.__dict__ = read_transaction.__dict__.copy()

    def fill_fields(self, mempool_data):
        if self.does_file_exist():
            self.read_from_file()
            if self._block is None:
                bitcoin_raw_transaction = bitcoin_core_rpc_connection.getrawtransaction(self._txid, verbose=True)
                updated_block_num = get_including_block(bitcoin_raw_transaction)
                if updated_block_num is not None:
                    self._block = updated_block_num
                    self.delete_file()
                    self.write_to_file()
        else:

            try:
                # blockPrint()
                bitcoin_raw_transaction = bitcoin_core_rpc_connection.getrawtransaction(self._txid, verbose=True)
                # enablePrint()
            except Exception as e:
                # this indicates the transaction only existed in the mempool and didn't end up being in a block
                # we can therefore recont
                # print "caught exception {} at time {}".format(traceback.print_exc(e), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()))
                assert (mempool_data is not None)
                self._weight = int(mempool_data['size']) * 4  # this is actually the "virtual size" or "weight"
                self._is_coin_base = False  # was included in the mempool, hence can't be a coinbase tx
                self._inputs_sum = None  # no knowledge of inputs sum
                self._outputs_sum = None  # no knowledge of outputs sum
                self._fees = mempool_data['modifiedfee']  # fees
                self._block = -1
                self._direct_ancestors = mempool_data['depends']
                self._total_in_block_ancestors = mempool_data['depends']
                self.write_to_file()
                return

            # transaction weight
            self._weight = bitcoin_raw_transaction["weight"]

            # tx outputs
            vout_list = bitcoin_raw_transaction['vout']
            self._outputs_sum = output_amount(vout_list)

            # inputs and outputs
            vin_list = bitcoin_raw_transaction['vin']

            # block number
            self._block = get_including_block(bitcoin_raw_transaction)
            # print "block is", self._block, "coinbase", is_coinbase_tx(bitcoin_raw_transaction)
            if is_coinbase_tx(bitcoin_raw_transaction):
                # a coinbase tx
                self._is_coin_base = True
                self._inputs_sum = None

                self._fees = None

                # a coinbase tx must be included in a block
                assert (self._block is not None)

                # no ancestors to a coinbase tx
                self._direct_ancestors = None
                self._total_in_block_ancestors = None

            else:
                # not a coinbase tx
                self._is_coin_base = False
                self._inputs_sum = input_amount(vin_list)

                self._fees = float(self._inputs_sum) - float(self._outputs_sum)
                # print "fees",self._fees
                self._direct_ancestors = get_direct_dependencies(vin_list)
                # print "fees",self._direct_ancestors
                self._total_in_block_ancestors = get_all_in_block_dependencies(bitcoin_raw_transaction, self._block)

            self.write_to_file()
            # assert(False)

    def __init__(self, txid, fill_fields_flag=True, mempool_data=None):
        self._txid = txid
        if fill_fields_flag:
            self.fill_fields(mempool_data)


if __name__ == "__main__":
    #   assert (len(sys.argv)==3) , "please provide run id"
    # new_tx = Transaction("e2dc4addf287ba915591152ced49ddf09a135d9cd64485d0427a3370e7956f75")
    # new_tx = Transaction("6f929f5d61694b0439f107127409114dcc60f2732011e10db30ca8eeac2fcc11")
    # new_tx = Transaction("0ebd4e33f84cd39c284d6d4fec991a7e3b932bbdf20ffcbcd67264b798a05f7a")
    new_tx = Transaction("b87f218de6186ad202a6ca8b069f0a47376f0860d5f88fe64d0f0adfed12622c")
    print new_tx.get_inputs_sum()
    print new_tx.get_fees()
    print new_tx.does_file_exist()
    for tx in new_tx.get_direct_ancestors():
        # print tx
        pass
    print "\n\n"
    print len(new_tx.get_total_in_block_ancestors())
    ret_list = list(new_tx.get_total_in_block_ancestors())
    ret_list.sort()
    for tx in ret_list:
        print tx

    new_tx2 = Transaction("77f07768a496b33c484f339130fc6f50a0f9b5780dc610d0495ca4c00c913ccf")
    print "\n\n"
    ret_list = list(new_tx2.get_total_in_block_ancestors())
    print len(new_tx2.get_total_in_block_ancestors())
    ret_list.sort()
    for tx in ret_list:
        print tx
