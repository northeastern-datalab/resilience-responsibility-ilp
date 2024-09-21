import argparse
import csv
import os
import pickle
import platform
import pandas as pd
import timeit

from datetime import datetime 
from pandas.api.types import is_string_dtype

from src.constants import queries
from src.responsibility import responsibility, responsibility_with_flow, responsibility_with_flow_nonlinear_query
from src.utils import pickRandomResponsibilityTuple, performSemijoinReduction
from expt.tpch.tpch_data_details import tpch_query_tables, tpch_schema

CREATE_DATA = True
OVERWRITE_DATA = False
DATA_SAVE_FILE = '../../data/expt_output/tpch-resp-case-{}.csv'
EXPT_CASE_DETAILS_FILE = 'expt/tpch/tpch_data_expt_cases.csv'
TPCH_DATA_FOLDER = '../../data/tpch/data/tpch-sf{}/'
TPCH_PICKLE_FILE = '../../data/tpch/data/tpch-sf{}/query-{}-pruned-database-instance.pkl'

def load_tpch_data(table_name, table_columns, sf, bag_semantics = False):
    """
    Load the tpch data from .tbl files to in-memory lists

    Args:
        table_name (str): name of the table to be loaded
        table_columns (list): columns of the table to be loaded
        sf (str): Scale-factor of tpch data to be loaded

    Returns:
        (list): The data from the tpch file
    """
    
    tbl = pd.read_table(TPCH_DATA_FOLDER.format(sf)+table_name+'.tbl', delimiter = '|', 
        names = tpch_schema[table_name], index_col = False, usecols = table_columns)[table_columns]
    
    
    
    
    
    
    tbl_bag = tbl.groupby(table_columns).size().reset_index(name = 'count')
    tbl_data_instance = tbl.drop_duplicates().values.tolist()
    
    return tbl_data_instance
    

def runCase(case_no):
    """
     Read the details of the experiment from a file with specifications, and run it

    Args:
        case_no (int): The case number to be run
    """
    
    expt_case_details =  pd.read_csv(EXPT_CASE_DETAILS_FILE)
    case_details = expt_case_details[expt_case_details['case_no'] == case_no].iloc[0].to_dict()
    resp_table = "R1"
    runTestCase(case_no, case_details['query_name'], resp_table, case_details['scale_factors'], bag_semantics = case_details['bag_semantics'])


def runTestCase(case_no, query_name, resp_table, sf_factors, bag_semantics = False):
    """ 
    Given the test case parameters, run the experiment to compare times of all algorithms

    Args:
        case_no (int): The case number that is running
        query_name (str): query_name as defined in tst.constants
        resp_table (str): The table from which to select tuple to find resp of 
        scale_factors (float): space seperated list of scale factors
        bag_semantics (bool, optional). Indicates if bag semantics or set semantics is used. Defaults to False.
    """
    if CREATE_DATA:
        runExperiment(query_name, resp_table, sf_factors, bag_semantics = bag_semantics, output_filename=DATA_SAVE_FILE.format(case_no), overwrite_data = OVERWRITE_DATA)
        print('Experiment Data Generation complete. Data is stored in', DATA_SAVE_FILE.format(case_no))

def runExperiment(query_name, resp_table, scale_factors, bag_semantics = False, output_filename='data/tpch_expt/unknown_query_data.csv', overwrite_data = False, time_limit = 6000):
    """
    Calculates resilience over tpch instance specified and tracks details 

    Args:
        query_name (str): query_name as defined in tst.constants
        resp_table (str): The table from which to select tuple to find resp of 
        scale_factors (float): space seperated list of scale factors
        bag_semantics (bool, optional). Indicates if bag semantics or set semantics is used. Defaults to False.
        output_filename (str, optional): Output storage csv
        overwrite_data (bool, optional): Indicates if output csv is overwritten. Defaults to False.
    """
    
    run_id = datetime.now().timestamp()
    print(run_id)

    
    query = queries[query_name]
    
    tpch_tables = tpch_query_tables[query_name]

    expt_headers = []
    tle = {x: False for x in ['flow_tuple_linearization_networkx_results', 'flow_tuple_linearization_lp_results', 'flow_witness_linearization_networkx_results', 'flow_witness_linearization_lp_results', 'flow_networkx_results', 'flow_lp_results']}

    for sf in scale_factors.split():

        
        pickle_filename = TPCH_PICKLE_FILE.format(sf, query_name)
        load_from_file = False
        data_load_start_time = timeit.default_timer()
        if os.path.exists(pickle_filename):
            with open(pickle_filename, 'rb') as f:
                pruned_database_instance = pickle.load(f)
                load_from_file = True
        else:
            print('not found'+pickle_filename)
            database_instance = dict()

            for tbl in tpch_tables:
                tpch_table = tpch_tables[tbl][0]
                tpch_table_columns = tpch_tables[tbl][1]
                database_instance[tbl] = load_tpch_data(tpch_table, tpch_table_columns, sf)
            
            pruned_database_instance = performSemijoinReduction(query, database_instance)
            with open(pickle_filename, 'wb') as f:
                pickle.dump(pruned_database_instance, f)

        
        output = {}        
        data_load_time = timeit.default_timer() - data_load_start_time
        print('Data loaded')
        tuple_weights = {}

        instance_id = datetime.now().timestamp()

        output['instance timestamp'] = instance_id
        output['query'] = query_name
        output['scale factor'] = sf
        output['load from file'] = load_from_file
        output['data load time'] = data_load_time
        output['run id'] = run_id
        output['bag semantics'] = bag_semantics 
        output['processor'] = platform.processor()
        
        expt_results = {}
        
        resp_tuple = pickRandomResponsibilityTuple(query, pruned_database_instance, resp_table)
        if resp_tuple is not None:
            
            expt_results["lp_results"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "LP")
            if len(expt_results["lp_results"]) == 0:
                
                continue
            expt_results["ilp_results"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "ILP")
            expt_results["ilp_results_600"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 600)
            expt_results["ilp_results_60"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 60)
            expt_results["ilp_results_10"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 10)
            expt_results["milp_results"] = responsibility(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, lp_type = "MILP")
            
            if query_name == "5Cycle":
                
                if not tle['flow_tuple_linearization_networkx_results']:
                    expt_results["flow_tuple_linearization_networkx_results"] = responsibility_with_flow_nonlinear_query(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_tuple")
                if not tle['flow_tuple_linearization_lp_results']:
                    expt_results["flow_tuple_linearization_lp_results"] = responsibility_with_flow_nonlinear_query(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_tuple")
                if not tle['flow_witness_linearization_networkx_results']:
                    expt_results["flow_witness_linearization_networkx_results"] = responsibility_with_flow_nonlinear_query(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_witness")
                if not tle['flow_witness_linearization_lp_results']:
                    expt_results["flow_witness_linearization_lp_results"] = responsibility_with_flow_nonlinear_query(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_witness")

            else:
                
                if not tle['flow_networkx_results']:
                    expt_results["flow_networkx_results"] = responsibility_with_flow(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "NetworkX")
                if not tle['flow_lp_results']:
                    expt_results["flow_lp_results"] = responsibility_with_flow(query, pruned_database_instance, resp_tuple, tuple_weights = tuple_weights, method = "LP")

            for expt_name in expt_results:
                output.update({expt_name+': ' + str(key): val for key, val in expt_results[expt_name].items()})

            for x in tle.keys():
                if x+': Solve Time' in output:
                    if output[x+': Solve Time'] > time_limit:
                        tle[x] = True

            if len(expt_headers) == 0:
                expt_headers = output.keys()

        else:
            continue
        
        if not os.path.exists(output_filename) or overwrite_data:
        
            with open(output_filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=expt_headers, restval='')
                writer.writeheader()
                writer.writerow(output)
                overwrite_data = False
        else:            
            
            with open(output_filename, 'a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=expt_headers, restval='')
                writer.writerow(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a tpch experiment')
    parser.add_argument('case', type=int, help="The case number to be run (Details specified in $EXPT_CASE_DETAILS_FILE)")
    args = parser.parse_args()
    runCase(args.case)
