import os
import configparser
import sys
import graph_creator

from files_related_functions import *
import tx_db
import block_details
from dependency_knapsack_solvers import *

# weight
MAX_WEIGHT = 4000000

# set paths
config = configparser.ConfigParser()
config.read('sampler_config.ini')
logged_mempool_samples_dir_path = config["paths"]["logged_mempool_samples_dir_path"]
block_analysis_output_dir_path = config["paths"]["block_analysis_output_dir_path"]


def find_sample_files(first_block, last_block):
    filter_function = filter_by_block_number_and_suffix(first_block, last_block, ".log.tar.gz")
    return find_files(logged_mempool_samples_dir_path, filter_function)


# if (str(current_tx_id) == "ce1d7e5bef02bbbdecd3a4b9a2595daa70528a4a5522f7911367153d50af1bce"):
# if (str(current_tx_id) == "65b5e149ec8e2ed2f9f29bef2e47ef4dc30c18c29b9479e9a5d50efd3d4c739a"):


def add_to_tx_dict(all_tx_dict, tx_ids_list, sample_tx_dict):
    for current_tx_id in tx_ids_list:
        if current_tx_id not in all_tx_dict:
            if sample_tx_dict is not None:
                all_tx_dict[current_tx_id] = tx_db.Transaction(current_tx_id,
                                                               mempool_data=sample_tx_dict[current_tx_id])
            else:
                all_tx_dict[current_tx_id] = tx_db.Transaction(current_tx_id)


def analyze_block_file_list(block_file_list):
    if len(block_file_list) == 0:
        return

    all_tx_dict = {}

    # data from block
    block_num, _ = block_count_and_time_stamp_from_file_name(block_file_list[0])
    block_tx_id_set = block_details.block_tx_list(block_num)
    add_to_tx_dict(all_tx_dict, block_tx_id_set, None)

    # solve for block
    block_transaction_set = [all_tx_dict[current_tx_id] for current_tx_id in block_tx_id_set
                             if not all_tx_dict[current_tx_id].get_is_coin_base()]
    block_graph = graph_creator.create_graph(block_transaction_set)
    block_fees, block_selected_tx_id_set = get_fees_and_txs(block_graph, MAX_WEIGHT)

    assert (len(block_tx_id_set) - 1 == len(block_selected_tx_id_set))  # -1 is due to the coinbase transaction
    print "block fees", block_fees, "selected", len(block_selected_tx_id_set) - 1, "of", \
        len(block_tx_id_set), "available tx"

    last_sample_fees = None
    last_sample_selected_tx_id_set = None
    last_sample_tx_id_set = None
    last_combined_fees = None
    last_combined_selected_tx_id_set = None
    last_combined_tx_id_set = None

    analysis_output_str_list = []

    for current_sample_file in block_file_list:
        sample_block_num, sample_timestamp = block_count_and_time_stamp_from_file_name(current_sample_file)
        assert (block_num == sample_block_num)

        # extract data from sample
        create_untarred_file(current_sample_file)
        sample_tx_dict = read_dict_from_file(current_sample_file)
        delete_untarred_file(current_sample_file)

        # data from sample
        sample_tx_id_set = sample_tx_dict.keys()
        add_to_tx_dict(all_tx_dict, sample_tx_id_set, sample_tx_dict)

        # solve for sample
        sample_transaction_set = [all_tx_dict[current_tx_id] for current_tx_id in sample_tx_id_set
                                  if not all_tx_dict[current_tx_id].get_is_coin_base()]
        sample_graph = graph_creator.create_graph(sample_transaction_set)
        sample_fees, sample_selected_tx_id_set = get_fees_and_txs(sample_graph, MAX_WEIGHT)

        # solve for sample + block
        combined_tx_id_set = set(block_tx_id_set)
        combined_tx_id_set.update(sample_tx_id_set)
        combined_tx_id_set = list(combined_tx_id_set)

        combined_transaction_set = [all_tx_dict[current_tx_id] for current_tx_id in combined_tx_id_set
                                    if not all_tx_dict[current_tx_id].get_is_coin_base()]
        combined_graph = graph_creator.create_graph(combined_transaction_set)
        combined_fees, combined_selected_tx_id_set = get_fees_and_txs(combined_graph, MAX_WEIGHT)

        if current_sample_file == block_file_list[0]:
            last_sample_fees = sample_fees
            last_sample_selected_tx_id_set = sample_selected_tx_id_set
            last_sample_tx_id_set = sample_tx_id_set

            last_combined_fees = combined_fees
            last_combined_selected_tx_id_set = combined_selected_tx_id_set
            last_combined_tx_id_set = combined_tx_id_set

        assert (last_sample_fees is not None)
        assert (last_sample_selected_tx_id_set is not None)
        assert (last_sample_tx_id_set is not None)
        assert (last_combined_fees is not None)
        assert (last_combined_selected_tx_id_set is not None)
        assert (last_combined_tx_id_set is not None)

        print "sample fees", sample_fees, "selected", len(sample_selected_tx_id_set), "of", \
            len(sample_tx_id_set), "available tx"
        print "combined fees", combined_fees, "selected", len(combined_selected_tx_id_set), "of", \
            len(combined_tx_id_set), "available tx"

        sample_summary_str = ""
        sample_summary_str = sample_summary_str + str(sample_timestamp) + ","
        sample_summary_str = sample_summary_str + str(block_num) + ","

        # ----- tx prints -----
        sample_summary_str = sample_summary_str + str(len(sample_tx_id_set)) + ","
        sample_summary_str = sample_summary_str + str(len(sample_selected_tx_id_set)) + ","
        sample_summary_str = sample_summary_str + str(len(combined_tx_id_set)) + ","
        sample_summary_str = sample_summary_str + str(len(combined_selected_tx_id_set)) + ","
        sample_summary_str = sample_summary_str + str(len(last_combined_tx_id_set)) + ","
        sample_summary_str = sample_summary_str + str(len(last_combined_selected_tx_id_set)) + ","

        # how many txs of the sample are present at the  last_combined_selected_tx_id_set
        sample_summary_str = sample_summary_str + \
                             str(len(last_combined_selected_tx_id_set.intersection(sample_tx_id_set))) + ","
        # how many txs of the combined are present at the  last_combined_selected_tx_id_set
        sample_summary_str = sample_summary_str + \
                             str(len(last_combined_selected_tx_id_set.intersection(combined_tx_id_set))) + ","

        # ----- fee prints -----
        sample_summary_str = sample_summary_str + str(sample_fees) + ","
        sample_summary_str = sample_summary_str + str(combined_fees) + ","
        sample_summary_str = sample_summary_str + str(last_combined_fees) + "\n"

        analysis_output_str_list.append(sample_summary_str)

    return analysis_output_str_list


def create_block_analysis_file(output_file_path, block_num):
    block_file_list = find_sample_files(block_num, block_num)
    block_file_list.sort(reverse=True)

    analysis_output_str_list = analyze_block_file_list(block_file_list)
    analysis_output_str_list.reverse()

    mkdir_p(os.path.dirname(output_file_path))
    fh = open(output_file_path, 'w+')
    fh.writelines(analysis_output_str_list)
    fh.close()


def analyze_one_block(block_num):
    output_file_path = get_output_file_path(output_dir_path=block_analysis_output_dir_path,
                                            time_stamp=None, block_count=block_num, suffix="_block_analysis.csv")
    function_to_create_file = lambda: create_block_analysis_file(output_file_path, block_num)
    create_file(output_file_path, function_to_create_file)


if __name__ == "__main__":

    assert (len(sys.argv) == 3), "please provide start and end block numbers"

    first_block = sys.argv[1]
    last_block = sys.argv[2]

    blocks_range = range(int(first_block), int(last_block) + 1)

    for current_block in blocks_range:
        # print current_block
        analyze_one_block(current_block)
