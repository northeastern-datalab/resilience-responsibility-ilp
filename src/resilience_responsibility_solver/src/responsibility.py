"""
Find responsibility of a set of witnesses under a query
"""

import pulp
import timeit

import networkx as nx
import pandas as pd
import src.constants as constants
from src.resilience import buildFlowGraphForResilience, min_cut_flow_lp
from src.utils import computeWitnesses, addLPVariable, nx_minimum_cut_with_timeout
from src.utils import constant_tuple_linearization_of_query, constant_witness_linearization_of_query


def responsibility(query, database_instance, responsibility_tuples, tuple_weights = {}, time_limit = None,\
                        lp_type = "ILP", verbosity = constants.VERBOSITY_LOW, fraction_preserved = None):
    """
    Calculates the responsibility of given database instance using an ILP

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        responsibility_tuples (str or list): A single responsibility tuple key or a list of tuples for which we find responsibility
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        lp_type (str, optional): Whether to perform an ILP, MILP or LP optimization. Defaults to "ILP".
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        fraction_preserved (float, optional). Proposes a variant of responsibility where a fraction of witnesses is preserved instead of at least 1.

    Returns:
        result: A dictionary with result and problem parameters -> responsibility, solve time etc
    """

    result = {}

    witness_computation_start_time = timeit.default_timer()
    witnesses = computeWitnesses(query, database_instance)
    result['witness computation time'] = timeit.default_timer() - witness_computation_start_time
    result['number of witnesses'] = len(witnesses)

    if len(witnesses) == 0:
        return {}
    
    
    witnesses_map = []
    for i in range(len(witnesses.index)):
        w_map = {}
        for col in witnesses:
            w_map[col] = "_"+str(witnesses[col].loc[i])
        witnesses_map.append(w_map)

    
    tuple_variables = {}
    witnesses_to_be_destroyed = []
    witnesses_to_be_preserved = []

    for w in witnesses_map:
        witness_tuples = []
        for (table_name, table_columns) in query:
            witness_tuples.append(table_name +''.join([w[variable] for variable in table_columns]))
        
        if (type(responsibility_tuples) != list and responsibility_tuples not in witness_tuples) or \
            ((type(responsibility_tuples) == list) and (len((set(responsibility_tuples) & set(witness_tuples))) == 0)) :

            for variableKey in witness_tuples:
                var_type = "ILP" if lp_type == "ILP" else "LP"
                addLPVariable(variableKey, tuple_variables, lp_type = var_type)
            witnesses_to_be_destroyed.append(w)
        else:
            witnesses_to_be_preserved.append(w)
    
    result['witnesses of responsibility tuple'] = len(witnesses_to_be_preserved)

    if len(witnesses_to_be_destroyed) == 0:
        result['Solve Time'] = 0
        result['Responsibility'] = 0
        return result
    
    
    prob = pulp.LpProblem("Resp", pulp.LpMinimize)

    
    prob += pulp.lpSum((tuple_weights[t] if t in tuple_weights else 1)*tuple_variables[t] for t in tuple_variables)

    
    for w in witnesses_to_be_destroyed:
        tuples = []
        for (table_name, table_columns) in query:
            t = tuple_variables[table_name + ''.join([w[variable] for variable in table_columns])]
            tuples.append(t)

        tuples = set(tuples) 
        prob += pulp.lpSum(tuples) >= 1


    
    witness_variables = {}
    for (i,w) in enumerate(witnesses_to_be_preserved):
        witness_key = "W_"+str(i)
        var_type = "ILP" if (lp_type == "ILP" or lp_type == "MILP") else "LP"
        addLPVariable(witness_key, witness_variables, lp_type = var_type)

    if fraction_preserved is None:
        prob += pulp.lpSum(witness_variables) <= len(witness_variables) -1 
    else:
        witnesses_to_be_preserved = int(fraction_preserved * len(witness_variables))
        prob += pulp.lpSum(witness_variables) <= len(witness_variables) - witnesses_to_be_preserved
        result['witnesses to be preserved'] = witnesses_to_be_preserved


    
    for (i,w) in enumerate(witnesses_to_be_preserved):
        witness_key = "W_"+str(i)
        for (table_name, table_columns) in query:
            t = table_name + ''.join([w[variable] for variable in table_columns])
            if t in tuple_variables:
                prob += witness_variables[witness_key] >= tuple_variables[t]

    

    if verbosity >= constants.VERBOSITY_HIGH:
        print(prob)

    try:
        
        ilp_solve_begin_time = timeit.default_timer()
        if time_limit is None:
            prob.solve(pulp.GUROBI_CMD())
        else:
            prob.solve(pulp.GUROBI_CMD(options=[('TimeLimit',time_limit)]))  
        result['Solve Time'] = timeit.default_timer() - ilp_solve_begin_time
        result['Solver Solution Time'] = prob.solutionTime

        if verbosity >= constants.VERBOSITY_HIGH:
            print("Status:", pulp.LpStatus[prob.status])

        
        if lp_type == 'LP':
            k = len(query)
            approx_obj = 0
            for v in prob.variables():
                if v.varValue >= (1/k):
                    if v.name in tuple_weights:
                        approx_obj += 1 * tuple_weights[v.name]
                    else:
                        approx_obj += 1
        
            result['responsibility lp approximation'] = approx_obj

        result['Responsibility'] = pulp.value(prob.objective) 
        result['error'] = None

        
        if verbosity >= constants.VERBOSITY_HIGH:
            for v in prob.variables():
                if v.varValue == 1:
                    print(v.name, "=", v.varValue)
    except Exception as e:
        print('Error!')
        print(e)
        result['Solve Time'] = -1
        result['Solver Solution Time'] = -1
        result['Responsibility'] = -1 
        result['error'] = str(e)
    
    if verbosity >= constants.VERBOSITY_LOW:
        print('Objective ', result['Responsibility'])

    return result

def responsibility_with_flow(query, database_instance, responsibility_tuples, tuple_weights = {}, time_limit = None,\
                    method = "NetworkX", exogenous_tables = []):
    """
    Calculates the responsibility of given database instance using Flow algorithm 

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        responsibility_tuples (str or list): A single responsibility tuple key or a list of tuples for which we find responsibility
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        lp_type (str, optional): Whether to perform an ILP, MILP or LP optimization. Defaults to "ILP".
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        fraction_preserved (float, optional). Proposes a variant of responsibility where a fraction of witnesses is preserved instead of at least 1.

    Returns:
        result: A dictionary with result and problem parameters -> responsibility, solve time etc
    """

    result = {}

    witness_computation_start_time = timeit.default_timer()
    witnesses = computeWitnesses(query, database_instance)
    result['witness computation time'] = timeit.default_timer() - witness_computation_start_time
    result['number of witnesses'] = len(witnesses)

    if len(witnesses) == 0:
        return {}

    if type(responsibility_tuples) != list:
        responsibility_tuples = [responsibility_tuples]

    base_graph = buildFlowGraphForResilience(query, database_instance, tuple_weights, exogenous_tables = exogenous_tables, domination_applied = 'fully')
    
    for r in responsibility_tuples:
        if base_graph.has_edge(r+'_start', r+'_end'):
            base_graph[r+'_start'][r+'_end']['capacity'] = 0

    
    
    resp_tuple_arrays = []
    for r in responsibility_tuples:        
        resp_tuple_array = r.split('_')
        resp_tuple_table = resp_tuple_array[0]
        resp_tuple_arrays.append(resp_tuple_array)
        
        resp_table_var = []
        for t,v in query:
            if t == resp_tuple_table:
                resp_table_var = v
    
    
    witnesses_to_be_preserved = pd.DataFrame(columns = witnesses.columns)
    for resp_tuple_array in resp_tuple_arrays:
        z = list(zip(resp_table_var, resp_tuple_array[1:]))
        pruned_witnesses = witnesses.copy()
        for i in range(len(z)):
            pruned_witnesses = pruned_witnesses.loc[ pruned_witnesses[ z[i][0] ].apply(str) == str(z[i][1]) ]
        witnesses_to_be_preserved = witnesses_to_be_preserved._append(pruned_witnesses, ignore_index = True)

    if len(witnesses_to_be_preserved) == len(witnesses):
        result['Responsibility'] = 0
        result['Solve Time'] = 0
        return result


    responsibility = float('inf')
    solve_time = 0
    
    for _,w in witnesses_to_be_preserved.iterrows():

        
        flow_graph = base_graph.copy()
        
        for (table_name, table_columns) in query:
            t = table_name + '_' +'_'.join([str(w[variable]) for variable in table_columns])
            if t not in responsibility_tuples:
                
                if flow_graph.has_edge(t+'_start', t+'_end'):
                    flow_graph[t+'_start'][t+'_end']['capacity'] = float('inf')

        
        if method == 'NetworkX':
            solve_begin_time = timeit.default_timer()
            cut_value, _ = nx.minimum_cut(flow_graph, 'source', 'target')
            
            cut_value = nx_minimum_cut_with_timeout(flow_graph, time_limit - solve_time if time_limit is not None else None) 
            if cut_value is None:
                solve_time = time_limit + 1
                responsibility = None 
                break
            solve_time += timeit.default_timer() - solve_begin_time
            responsibility = min(responsibility, cut_value)

        elif method == "LP":
            lp_result = min_cut_flow_lp(flow_graph, time_limit = time_limit)
            solve_time += lp_result['Solve Time']
            responsibility = min(responsibility, lp_result['Resilience'])

    result['Responsibility'] = responsibility
    result['Solve Time'] = solve_time

    return result

def responsibility_with_flow_nonlinear_query(query, database_instance, responsibility_tuples, tuple_weights = {}, exogenous_tables=[], time_limit = None, method = 'NetworkX', linearization_method = "constant_tuple", ptime_linearization = False):
    '''
    Calculates an approximation responsibility of given database instance using a Flow algorithm - either with NetworkX or Pulp

    This method assumes that the query / database is not linear!

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        responsibility_tuples (str or list): A single responsibility tuple or a list of tuples for which we find responsibility
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        method (str, optional): Whether to perform an ILP or LP optimization. Defaults to 'NetworkX'.
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        exogenous_tables(list, optional): Tables which may not be removed in resilience computation. Defaults to empty
        ptime_linearization (bool, optional): Denotes whether to use a PTIME single linearization or all possible linearizations

    Returns:
        result: A dictionary with result and problem parameters -> responsibility, solve time etc
    '''
    results ={}
    if linearization_method == "constant_tuple":
        
        linearized_queries = constant_tuple_linearization_of_query(query)
        for lq in linearized_queries:
            result_lq = responsibility_with_flow(lq, database_instance, responsibility_tuples, tuple_weights = tuple_weights,
                                 exogenous_tables=exogenous_tables, time_limit = time_limit, method = method)
            if 'Responsibility' in results:
                results['Responsibility'] = min(results['Responsibility'], result_lq['Responsibility'])
                results['Solve Time'] = results['Solve Time'] + result_lq['Solve Time']
            else:
                results['Responsibility'] = result_lq['Responsibility']
                results['Solve Time'] = result_lq['Solve Time'] 
            
            
            if time_limit is not None and results['Solve Time'] > time_limit:
                results['Responsibility'] = None
                return results

            
    elif linearization_method == "constant_witness":
        linearized_instances = constant_witness_linearization_of_query(query, database_instance, responsibility_tuples, tuple_weights = tuple_weights, ptime_linearization = ptime_linearization)
        for (lq, ldb, lrt, ltw) in linearized_instances:
            
            result_lq = responsibility_with_flow(lq, ldb, lrt, tuple_weights = ltw,
                                 exogenous_tables = exogenous_tables, time_limit = time_limit, method = method)
            if 'Responsibility' in results:
                results['Responsibility'] = min(results['Responsibility'], result_lq['Responsibility'])
                results['Solve Time'] = results['Solve Time'] + result_lq['Solve Time']
            else:
                results['Responsibility'] = result_lq['Responsibility']
                results['Solve Time'] = result_lq['Solve Time'] 
            
            
            if time_limit is not None and results['Solve Time'] > time_limit:
                results['Responsibility'] = None
                return results
    
    return results
