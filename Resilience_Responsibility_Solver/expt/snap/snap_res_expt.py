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
from src.utils import performSemijoinReduction
from expt.snap.snap_utils import load_snap_data

OVERWRITE_DATA = False
DATA_SAVE_FILE = 'data/snap/expt-data-case-{}.csv'
DATA_INSTANCE_PICKLE_FOLDER = 'data/data_instances_pickle_dump/'
EXPT_CASE_DETAILS_FILE = 'expt/snap/snap_data_expt_cases.csv'

def runCase(case_no):
    """
     Read the details of the experiment from a file with specifications, and run it

    Args:
        case_no (int): The case number to be run
    """
    
    expt_case_details =  pd.read_csv(EXPT_CASE_DETAILS_FILE)
    case_details = expt_case_details[expt_case_details['case_no'] == case_no].iloc[0].to_dict()
    
    
    runARunOfExperiments(case_details['query_name'], case_details['sample_log_base'], case_details['sample_log_start'], case_details['sample_log_end'], case_details['sample_points'], output_filename=DATA_SAVE_FILE.format(case_no), overwrite_data = OVERWRITE_DATA)
    print('Experiment Data Generation complete. Data is stored in', DATA_SAVE_FILE.format(case_no))


def runARunOfExperiments(query_name, sample_log_base, sample_log_start, sample_log_end, sample_points, bag_semantics = False, max_bag_size = 10, output_filename='data/synthetic_expt/unknown_query_data.csv', overwrite_data = False):
    """
    Calculates resilience over a monotonically bigger data instance and tracks details 

    Args:
        query_name (str): query_name as defined in snap_queries
        sample_log_base (float): The base of the exoponent used to calculate sample percent
        sample_log_start (float): The start value of the exponent in the data run
        sample_log_end (float): The final value of the exponent in the data run
        sample_points (int): The number of points in the data run 
        output_filename (str, optional): Output storage csv
        overwrite_data (bool, optional): Indicates if output csv is overwritten. Defaults to False.
    """
    
    run_id = datetime.now().timestamp()
    query = queries[query_name]

    for sample_exponent in np.linspace(sample_log_start, sample_log_end, sample_points):

        sample_percent = sample_log_base ** sample_exponent
        database_instance, tuple_weights = load_snap_data(sample_percent = sample_percent)

        instance_id = datetime.now().timestamp()
        instance_data = (database_instance, tuple_weights)

        pickle_filename = DATA_INSTANCE_PICKLE_FOLDER+str(instance_id)+'-r-'+str(run_id)+'.pkl'
        with open(pickle_filename, 'wb') as f:
            pickle.dump(instance_data, f)

        output = {}

        output['instance timestamp'] = instance_id
        output['query'] = query_name
        output['run id'] = run_id
        output['sample percent'] = sample_percent
        output['sample log base'] = sample_log_base
        output['sample log start'] = sample_log_start
        output['sample log interval'] = sample_log_end
        output['sample points'] = sample_points
        output['bag semantics'] = bag_semantics 
        output['max bag size'] = max_bag_size if bag_semantics else 0
        output['processor'] = platform.processor()
        
        pruned_database_instance = performSemijoinReduction(query, database_instance)
        expt_results = {}
        
        expt_results["lp_results"] = resilience(query, database_instance, tuple_weights = tuple_weights, lp_type = "LP")
        if len(expt_results["lp_results"]) == 0:
            
            continue
        expt_results["ilp_results"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP")
        expt_results["ilp_results_600"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 600)
        expt_results["ilp_results_60"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 60)
        expt_results["ilp_results_10"] = resilience(query, pruned_database_instance, tuple_weights = tuple_weights, lp_type = "ILP", time_limit = 10)
        
        if query_name == "5Cycle":
            
            expt_results["flow_tuple_linearization_networkx_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_tuple")
            expt_results["flow_tuple_linearization_lp_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_tuple")
            expt_results["flow_witness_linearization_networkx_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "NetworkX", linearization_method = "constant_witness")
            expt_results["flow_witness_linearization_lp_results"] = resilience_with_flow_nonlinear_query(query, pruned_database_instance, tuple_weights = tuple_weights, method = "LP", linearization_method = "constant_witness")

        else:
            
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