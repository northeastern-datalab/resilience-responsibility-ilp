'''
Find resilience of a set of witnesses under a query
'''

import pulp
import timeit
import networkx as nx 
import pandas as pd

import src.constants as constants
from src.utils import computeWitnesses, addLPVariable, constant_witness_linearization_of_query, \
                        constant_tuple_linearization_of_query, nx_minimum_cut_with_timeout

def resilience(query, database_instance, tuple_weights = {}, time_limit = None, lp_type = 'ILP', verbosity = constants.VERBOSITY_LOW, exogenous_tables=[]):
    '''
    Calculates the resilience of given database instance using an ILP

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        lp_type (str, optional): Whether to perform an ILP or LP optimization. Defaults to 'ILP'.
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        exogenous_tables(list, optional): Tables which may not be removed in resilience computation. Defaults to empty

    Returns:
        result: A dictionary with result and problem parameters -> resilience, solve time etc
    '''

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
            w_map[col] = '_'+str(witnesses[col].loc[i])
        witnesses_map.append(w_map)

    
    tuple_variables = {}
    for w in witnesses_map:
        for (table_name, table_columns) in query:
            variableKey = table_name +''.join([w[variable] for variable in table_columns])
            addLPVariable(variableKey, tuple_variables, lp_type = lp_type)

    
    
    prob = pulp.LpProblem('Resilience', pulp.LpMinimize)

    
    prob += pulp.lpSum((tuple_weights[t] if t in tuple_weights else 1)*tuple_variables[t] for t in tuple_variables)

    
    for w in witnesses_map:
        tuples = []
        for (table_name, table_columns) in query:
            if table_name not in exogenous_tables:
                t = tuple_variables[table_name + ''.join([w[variable] for variable in table_columns])]
                tuples.append(t)

        tuples = set(tuples) 
        prob += pulp.lpSum(tuples) >= 1

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
            print('Status:', pulp.LpStatus[prob.status])

        if verbosity >= constants.VERBOSITY_HIGH:
            for v in prob.variables():
                if v.varValue == 1:
                    print(v.name, '=', v.varValue)
        
        if lp_type == 'LP':
            k = len(query)
            approx_obj = 0
            for v in prob.variables():
                if v.varValue >= (1/k):
                    if v.name in tuple_weights:
                        approx_obj += 1 * tuple_weights[v.name]
                    else:
                        approx_obj += 1
        
            result['resilience lp approximation'] = approx_obj
        
        result['Resilience'] = pulp.value(prob.objective) 
        result['error'] = None

    except Exception as e:
        print('Error!')
        print(e)
        result['Solve Time'] = -1
        result['Solver Solution Time'] = -1
        if lp_type == 'LP':
            result['resilience lp approximation'] = -1
        result['Resilience'] = -1 
        result['error'] = str(e)
    
    if verbosity >= constants.VERBOSITY_LOW:
        print('Objective ', result['Resilience'])

    return result

def resilience_with_flow(query, database_instance, tuple_weights = {}, exogenous_tables=[], time_limit = None, method = 'NetworkX'):
    '''
    Calculates the resilience of given database instance using a Flow algorithm - either with NetworkX or Pulp

    This method assumes that the query / database has been linearized!

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        method (str, optional): Whether to perform an ILP or LP optimization. Defaults to 'NetworkX'.
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        exogenous_tables(list, optional): Tables which may not be removed in resilience computation. Defaults to empty

    Returns:
        result: A dictionary with result and problem parameters -> resilience, solve time etc
    '''

    results = {}
    
    G = buildFlowGraphForResilience(query, database_instance, tuple_weights, exogenous_tables)

    if method == 'NetworkX':
        solve_begin_time = timeit.default_timer()
        cut_value = nx_minimum_cut_with_timeout(G, time_limit) 
        results['Solve Time'] = timeit.default_timer() - solve_begin_time if cut_value is not None else time_limit + 1
        results['Resilience'] = cut_value

    elif method == "LP":
        results = min_cut_flow_lp(G, time_limit = time_limit)
    
    return results

def buildFlowGraphForResilience(query, database_instance, tuple_weights = {}, exogenous_tables=[], domination_applied = 'all'):
    '''
    Converts the problem of Resilience of a query to 

    This method assumes that the query / database has been linearized!

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        exogenous_tables(list, optional): Tables which may not be removed in resilience computation. Defaults to empty
        domination_applied (str, optional): Decides if to remove dominated tables or fully dominated table. Can take values 'all','fully','none'. Defaults to all.

    Returns:
        G: A NetworkX flow graph
    '''

    G = nx.DiGraph()
    edge_df = pd.DataFrame(columns=['source','target'])

    for idx, table in enumerate(query):
        
        
        current_table_df = pd.DataFrame(database_instance[table[0]], columns = table[1])
        current_table_df['current tuple name'] = current_table_df[table[1]].apply(lambda x: table[0] + '_' + '_'.join(map(str, x.values)), axis = 1)

        current_table_df['source'] = current_table_df['current tuple name'] + '_start'
        current_table_df['target'] = current_table_df['current tuple name'] + '_end'
        if table[0] not in exogenous_tables:
            current_table_df['capacity'] = current_table_df['current tuple name'].apply(lambda x: 1 if x not in tuple_weights else tuple_weights[x])
        else: 
            current_table_df['capacity'] = float('inf')
        new_edges = current_table_df[['source', 'target', 'capacity']]
        edge_df = pd.concat([edge_df, new_edges])

        
        if idx == 0:
            current_table_df['source'] = 'source'
            current_table_df['target'] = current_table_df['current tuple name'] + '_start'
            current_table_df['capacity'] = float('inf')
            new_edges = current_table_df[['source', 'target', 'capacity']]
            edge_df = pd.concat([edge_df, new_edges])
        
        if idx != 0:
            previous_table = query[idx-1]
            previous_table_df = pd.DataFrame(database_instance[previous_table[0]], columns = previous_table[1])
            intersecting_variables = list(set(table[1]).intersection(previous_table[1]))
            
            if len(intersecting_variables) == 0:
                merged_df = previous_table_df.assign(key=1).merge(current_table_df.assign(key=1), on="key").drop("key", axis=1)
            else:
                merged_df = previous_table_df.merge(current_table_df, how = 'inner', on = intersecting_variables)
            merged_df['source'] = merged_df[previous_table[1]].apply(lambda x: previous_table[0] + '_' + '_'.join(map(str, x.values)) + '_end', axis = 1)
            merged_df['target'] = merged_df[table[1]].apply(lambda x: table[0] + '_' + '_'.join(map(str, x.values)) + '_start', axis = 1)
            merged_df['capacity'] = float('inf')
            new_edges = merged_df[['source', 'target', 'capacity']]
            edge_df = pd.concat([edge_df, new_edges])

        
        if idx == len(query) - 1:
            
            current_table_df['source'] = current_table_df['current tuple name'] + '_end'
            current_table_df['target'] = 'target' 
            current_table_df['capacity'] = float('inf')
            new_edges = current_table_df[['source', 'target', 'capacity']]
            edge_df = pd.concat([edge_df, new_edges])
        
    G = nx.from_pandas_edgelist(edge_df, create_using = nx.DiGraph, edge_attr=True)   
    return G

def min_cut_flow_lp(G, time_limit = None):
    """
    Computes the Resilience of an instance represented as in flow graph 
    (alternative: finds min cut / max flow of a flow graph using an LP)

    Args:
        G (NetworkX DiGraph): A NetworkX graph populated with a flow graph to compute resilience from.
        time_limit (float): The time limit allowed for the solver

    Returns:
        results (dict): The solves and solve times etc, after solving for Resilience with an ILP.
    """
    result = {}

    
    lp_tuple_variables = {}

    
    for e in G.edges:
        capacity = G.get_edge_data(e[0],e[1])['capacity']
        variable_name = e[0]+'-'+e[1]
        lp_tuple_variables[variable_name] = pulp.LpVariable(variable_name, lowBound = 0, upBound = capacity, cat = 'Continuous')

    
    prob = pulp.LpProblem('RES_Flow_LP',pulp.LpMaximize)

    
    prob += pulp.lpSum([lp_tuple_variables[str(s+'-'+n)] for (s, n) in G.out_edges('source')])
    
    for node in G.nodes:
        if node != 'source' and node != 'target':
            
            incomingFlow = pulp.lpSum([lp_tuple_variables[u+'-'+v] for (u, v) in G.in_edges(node)])
            outgoingFlow = pulp.lpSum([lp_tuple_variables[u+'-'+v] for (u, v) in G.out_edges(node)])
            prob += pulp.lpSum(incomingFlow) == pulp.lpSum(outgoingFlow)

    try:
        
        ilp_solve_begin_time = timeit.default_timer()
        if time_limit is None:
            prob.solve(pulp.GUROBI_CMD())
        else:
            prob.solve(pulp.GUROBI_CMD(options=[('TimeLimit',time_limit)]))  
        result['Solve Time'] = timeit.default_timer() - ilp_solve_begin_time
        result['Solver Solution Time'] = prob.solutionTime
        result['Resilience'] = pulp.value(prob.objective)
        result['error'] = None

    except Exception as e:
        print('Error!')
        print(e)
        result['Solve Time'] = -1
        result['Solver Solution Time'] = -1
        result['Resilience'] = -1
        result['error'] = str(e)
    return result

def resilience_with_flow_nonlinear_query(query, database_instance, tuple_weights = {}, exogenous_tables=[], time_limit = None, method = 'NetworkX', linearization_method = "constant_tuple", ptime_linearization = False):
    '''
    Calculates an approximation resilience of given database instance using a Flow algorithm - either with NetworkX or Pulp

    This method assumes that the query / database is not linear!

    Args:
        query (list): A boolean conjunctive query described by the variables in each table
        database_instance (list): A list of tuples present in each table
        tuple_weights (list, optional): Weight of tuples under bag semantics. Defaults to an empty dict.
        time_limit (int, optional): The timeout period of the optimization. Defaults to None.
        method (str, optional): Whether to perform an ILP or LP optimization. Defaults to 'NetworkX'.
        verbosity (int, optional): Level of verbosity of the output. Defaults to 1.
        exogenous_tables(list, optional): Tables which may not be removed in resilience computation. Defaults to empty
        ptime_linearization (bool, optional): Denotes whether to use a PTIME single linearization or all possible linearizations

    Returns:
        result: A dictionary with result and problem parameters -> resilience, solve time etc
    '''
    results ={}
    if linearization_method == "constant_tuple":
        
        linearized_queries = constant_tuple_linearization_of_query(query)
        for lq in linearized_queries:
            result_lq = resilience_with_flow(lq, database_instance, tuple_weights = tuple_weights,
                                 exogenous_tables=exogenous_tables, time_limit = time_limit, method = method)
            if 'Resilience' in results:
                results['Resilience'] = min(results['Resilience'], result_lq['Resilience'])
                results['Solve Time'] = results['Solve Time'] + result_lq['Solve Time']
            else:
                results['Resilience'] = result_lq['Resilience']
                results['Solve Time'] = result_lq['Solve Time'] 
            
            
            if time_limit is not None and results['Solve Time'] > time_limit:
                results['Resilience'] = None
                return results
    elif linearization_method == "constant_witness":
        linearized_instances = constant_witness_linearization_of_query(query, database_instance, tuple_weights = tuple_weights, ptime_linearization = ptime_linearization)
        for (lq, ldb, ltw) in linearized_instances:
            result_lq = resilience_with_flow(lq, ldb, tuple_weights = ltw,
                                 exogenous_tables=exogenous_tables, time_limit = time_limit, method = method)
            if 'Resilience' in results:
                results['Resilience'] = min(results['Resilience'], result_lq['Resilience'])
                results['Solve Time'] = results['Solve Time'] + result_lq['Solve Time']
            else:
                results['Resilience'] = result_lq['Resilience']
                results['Solve Time'] = result_lq['Solve Time'] 
            
            
            if time_limit is not None and results['Solve Time'] > time_limit:
                results['Resilience'] = None
                return results
    
    return results