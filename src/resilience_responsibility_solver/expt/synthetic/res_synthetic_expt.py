import argparse
import csv
import os
import pickle
import platform

import numpy as np
import pandas as pd

from datetime import datetime
from src.constants import queries
from src.resilience import resilience, resilience_with_flow, resilience_with_flow_nonlinear_query
from src.utils import addTuples, performSemijoinReduction

CREATE_DATA = True
OVERWRITE_DATA = False
DATA_SAVE_FILE = '../../data/expt_output/expt-data-case-{}.csv'
DATA_INSTANCE_PICKLE_FOLDER = '../../data/data_instances_pickle_dump/'
EXPT_CASE_DETAILS_FILE = 'expt/synthetic/synthetic_res_data_expt_cases.csv'

def runCase(case_no):
    """
     Read the details of the experiment from a file with specifications, and run it

    Args:
        case_no (int): The case number to be run
    """
    
    expt_case_details =  pd.read_csv(EXPT_CASE_DETAILS_FILE)
    case_details = expt_case_details[expt_case_details['case_no'] == case_no].iloc[0].to_dict()
    runTestCase(case_no, case_details['query_name'], case_details['domain_size'] , case_details['itr_log_base'], \
        case_details['itr_log_start'], case_details['itr_log_end'], case_details['num_itr'], bag_semantics = case_details['bag_semantics'],
        max_bag_size = case_details['max_bag_size'])


def runTestCase(case_no, query_name, domain_size, itr_log_base, itr_log_start, itr_log_end, itr_num, bag_semantics = False, max_bag_size = 10):
    """ 
    Given the test case parameters, run the experiment to compare times of all algorithms

    Args:
        case_no (int): The case number that is running
        query_name (str): query_name as defined in tst.constants
        domain_size (int): domain size of the database instance
        itr_log_base (float): the base that gets a higher exponent each iteration
        itr_log_start (float): starting exponent of itr_log_base
        itr_log_end (float): final exponent of itr_log_base
        itr_num (int): The number of iterations in this data run
        bag_semantics (bool, optional). Indicates if bag semantics or set semantics is used. Defaults to False.
        max_bag_size (bool, optional). Indicates max bag size under bag semantics. Defaults to 10.
    """
    if CREATE_DATA:
        runMonotoneRunOfExperiments(query_name, domain_size, itr_log_base, itr_log_start, itr_log_end, itr_num, bag_semantics = bag_semantics, max_bag_size = max_bag_size, output_filename=DATA_SAVE_FILE.format(case_no), overwrite_data = OVERWRITE_DATA)
        print('Experiment Data Generation complete. Data is stored in', DATA_SAVE_FILE.format(case_no))
    
    


def runMonotoneRunOfExperiments(query_name, domain_size, itr_log_base, itr_log_start, itr_log_end, itr_num, bag_semantics = False, max_bag_size = 10, output_filename='data/synthetic_expt/unknown_query_data.csv', overwrite_data = False):
    """
    Calculates resilience over a monotonically bigger data instance and tracks details 

    Args:
        query_name (str): query_name as defined in tst.constants
        domain_size (int): domain size of the database instance
        itr_log_base (float): the base that gets a higher exponent each iteration
        itr_log_start (float): starting exponent of itr_log_base
        itr_log_end (float): final exponent of itr_log_base
        itr_num (int): The number of iterations in this data run
        bag_semantics (bool, optional). Indicates if bag semantics or set semantics is used. Defaults to False.
        max_bag_size (bool, optional). Indicates max bag size under bag semantics. Defaults to 10.
        output_filename (str, optional): Output storage csv
        overwrite_data (bool, optional): Indicates if output csv is overwritten. Defaults to False.
    """
    
    run_id = datetime.now().timestamp()
    query = queries[query_name]
    database_instance = None
    tuple_weights = None

    tuples_added = 0
    
    for itr_exponent in np.linspace(itr_log_start, itr_log_end, itr_num):

        tuples_to_be_added = int(itr_log_base ** itr_exponent) - tuples_added

        if database_instance == None:
            database_instance, tuple_weights = addTuples(query,  tuples_to_be_added, domain_size, None, bag_semantics = bag_semantics)
        else:
            database_instance, tuple_weights = addTuples(query, tuples_to_be_added, domain_size, (database_instance, tuple_weights), bag_semantics = bag_semantics)

        tuples_added += tuples_to_be_added
        instance_id = datetime.now().timestamp()
        instance_data = (database_instance, tuple_weights)
        pruned_database_instance = performSemijoinReduction(query, database_instance)

        pickle_filename = DATA_INSTANCE_PICKLE_FOLDER+str(instance_id)+'-r-'+str(run_id)+'.pkl'
        with open(pickle_filename, 'wb') as f:
            pickle.dump(instance_data, f)

        output = {}

        output['instance timestamp'] = instance_id
        output['query'] = query_name
        output['domain size'] = domain_size
        output['run id'] = run_id
        output['itr exponent'] = itr_exponent
        output['itr start'] = itr_log_start
        output['itr end'] = itr_log_end
        output['itr num'] = itr_num
        output['tuples added'] = tuples_added
        output['bag semantics'] = bag_semantics 
        output['max bag size'] = max_bag_size if bag_semantics else 0
        output['processor'] = platform.processor()
        
        expt_results = {}
        
        expt_results["lp_results"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "LP")
        if len(expt_results["lp_results"]) == 0:
            
            continue
        expt_results["ilp_results"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP")
        expt_results["ilp_results_600"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 600)
        expt_results["ilp_results_60"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 60)
        expt_results["ilp_results_10"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 10)
        
        if query_name == "3Star" or query_name == "Triangle" or (query_name == "TriangleUnary" and bag_semantics):
            
            expt_results["flow_tuple_linearization_networkx_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_tuple")
            expt_results["flow_tuple_linearization_lp_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_tuple")
            expt_results["flow_witness_linearization_networkx_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_witness")
            expt_results["flow_witness_linearization_lp_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_witness")

        elif query_name == "TriangleUnary" or query_name == "TriangleBinary":
            
            expt_results["flow_witness_linearization_networkx_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_witness", ptime_linearization = True)
            expt_results["flow_witness_linearization_lp_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_witness", ptime_linearization = True)
 
        elif not query_name.startswith("SJ"):
            
            expt_results["flow_networkx_results"] = resilience_with_flow(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX")
            expt_results["flow_lp_results"] = resilience_with_flow(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP")

        for expt_name in expt_results:
            output.update({expt_name+': ' + str(key): val for key, val in expt_results[expt_name].items()})

        
        if not os.path.exists(output_filename) or overwrite_data:
            
            with open(output_filename, 'w', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=output.keys())
                writer.writeheader()
                writer.writerow(output)
            overwrite_data = False
        else:            
            
            with open(output_filename, 'a', newline='') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=output.keys())
                writer.writerow(output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a synthetic experiment')
    parser.add_argument('case', type=int, help="The case number to be run (Details specified in $EXPT_CASE_DETAILS_FILE)")
    args = parser.parse_args()
    runCase(args.case)