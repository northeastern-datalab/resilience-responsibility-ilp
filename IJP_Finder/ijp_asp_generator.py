'''
March 2023. 

Code to generate an ASP program that can find if there exists an IJP for a query or not.
The program uses the saturation technique
'''
import argparse
import itertools
import pandas as pd

from src.constants import queries

PROGRAM_SAVE_FILE = 'src/ijp_asp/autogen_asp_scripts/ijp_expt_cases-{}.dl'
EXPT_CASE_DETAILS_FILE = 'src/ijp_asp/ijp_expt_cases.csv'


def generate_asp_program(case_no, query_name, endpoint_table, max_domain, optimize = False, check_composability = False):
    '''
    For a given query generate the asp problem to check if there is an ijp or not
    '''
    query = queries[query_name]
    file_key = query_name+'-'+endpoint_table+'-'+str(max_domain)+'-'+str(optimize)
    file_key = case_no
    f = open(PROGRAM_SAVE_FILE.format(file_key), "w") 
    # Part 1: Generate database

    query_tables = set([t for (t,_) in query])
    query_tables_arity = {t: len(vars) for (t,vars) in query}
    query_variables = list(set([v for (_, qvars) in query for v in qvars]))

    endpoint_arity = query_tables_arity[endpoint_table]
    endpoint_tuple_1_values = ",".join([str(i + 1) for i in range(endpoint_arity)])
    endpoint_tuple_2_values = ",".join([str(endpoint_arity + i + 1) for i in range(endpoint_arity)])

    for t in query_tables:
        a = [i+1 for i in range(max_domain)]
        lists = [a for _ in range(query_tables_arity[t])]
        for i,element in enumerate(itertools.product(*lists)):
            e = ','.join(str(x) for x in element)
            f.write(str(t).lower()+'('+str(i+1)+','+e+').\n')

            if endpoint_table == t:
                if endpoint_tuple_1_values == e:
                    endpoint_tuple_1 = i+1
                if endpoint_tuple_2_values == e:
                    endpoint_tuple_2 = i+1

    # Part 2: There exists an ijp (shown by relation in indb)
    # Disjunction could be left away here
    for t in query_tables:
        table_name = t.lower()
        underscores = ", ".join(["_" for _ in range(query_tables_arity[t])])
        f.write("indb({t}, Tid, 1) | indb({t}, Tid, 0) :- {t}(Tid, {underscores}).\n".format(t = table_name, underscores = underscores))


    # Part 3: Compute witnesses
    query_variables_str = ", ".join([qv.upper() for qv in query_variables])
    tid_str = ", ".join(["T"+str(i+1) for i in range(len(query))])
    query_table_str_array = []
    query_indb_str_array = []
    for i, (table, qvars) in enumerate(query):
        qvars_str = ", ".join([v.upper() for v in qvars])
        query_table_str_array.append("{t}(T{tid}, {qvars})".format(t = table.lower(), tid = i+1, qvars = qvars_str))
        query_indb_str_array.append("indb({t}, T{tid}, 1)".format(t = table.lower(), tid = i+1))


    query_table_str = ", ".join(query_table_str_array)
    query_indb_str = ", ".join(query_indb_str_array)

    f.write("witness({query_variables_str}, {tid_str}) :- {query_table_str}, {indb_str}.\n".format(query_variables_str = query_variables_str, tid_str = tid_str, query_table_str = query_table_str, indb_str = query_indb_str))
    f.write("number_of_witnesses(K) :- #count{{ {query_variables_str}, {tid_str} : witness({query_variables_str}, {tid_str}) }} = K.\n".format(query_variables_str = query_variables_str, tid_str = tid_str))

    # Part 3c - Set endpoints
    f.write("\n")
    f.write("valid_res2({endpoint_table}, {endpoint_tuple_1}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_1 = endpoint_tuple_1))
    f.write("invalid_res2({endpoint_table}, {endpoint_tuple_1}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_1 = endpoint_tuple_1))

    f.write("valid_res3({endpoint_table}, {endpoint_tuple_2}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_2 = endpoint_tuple_2))
    f.write("invalid_res3({endpoint_table}, {endpoint_tuple_2}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_2 = endpoint_tuple_2))

    f.write("valid_res4({endpoint_table}, {endpoint_tuple_1}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_1 = endpoint_tuple_1))
    f.write("invalid_res4({endpoint_table}, {endpoint_tuple_1}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_1 = endpoint_tuple_1))
    f.write("valid_res4({endpoint_table}, {endpoint_tuple_2}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_2 = endpoint_tuple_2))
    f.write("invalid_res4({endpoint_table}, {endpoint_tuple_2}, 1).\n".format(endpoint_table = endpoint_table.lower(), endpoint_tuple_2 = endpoint_tuple_2))

    # Part 4 - Guess
    f.write("\n")

    # Part 4a Guess invalid_res
    for i in range(1, 5, 1):
        for t in query_tables:
            table_name = t.lower()
            underscores = ", ".join(["_" for _ in range(query_tables_arity[t])])
            f.write("invalid_res{i}({t}, Tid, 1) | invalid_res{i}({t}, Tid, 0) :- {t}(Tid, {underscores}).\n".format(i = i, t = table_name, underscores = underscores))
        f.write("\n")


    # Part 4b Guess valid_res
    # Disjunction not necessary but used
    for i in range(1, 5, 1):
        for t in query_tables:
            table_name = t.lower()
            underscores = ", ".join(["_" for _ in range(query_tables_arity[t])])
            f.write("valid_res{i}({t}, Tid, 1) | valid_res{i}({t}, Tid, 0) :- {t}(Tid, {underscores}).\n".format(i = i, t = table_name, underscores = underscores))
        f.write("\n")


    # Part 5 - Check
    f.write("\n")

    # Print 5a - Check invalid resilience
    for i in range(1, 5, 1):
        invalid_res_i_str_array = []
        for ti, (table, qvars) in enumerate(query):
            invalid_res_i_str_array.append("invalid_res{i}({t}, T{tid}, 0)".format(i=i, t = table.lower(), tid = ti+1))
        invalid_res_i_str = ", ".join(invalid_res_i_str_array)
        f.write("invalid_resilience{i} :- witness({query_variables_str}, {tid_str}), {invalid_res_i_str}.\n".format(i = i, query_variables_str = query_variables_str, tid_str = tid_str,invalid_res_i_str = invalid_res_i_str))
        if i != 4:
            f.write("invalid_resilience{i} :- #count{{Table, Tid: invalid_res{i}(Table, Tid, 1)}} >= K, res(K).\n".format(i = i))
        else:
            f.write("invalid_resilience{i} :- #count{{Table, Tid: invalid_res{i}(Table, Tid, 1)}} >= K+1, res(K).\n".format(i = i))


    # Print 5b - Check valid resilience
    f.write("\n")
    for i in range(1, 5, 1):
        invalid_res_i_str_array = []
        for ti, (table, qvars) in enumerate(query):
            invalid_res_i_str_array.append("valid_res{i}({t}, T{tid}, 0)".format(i=i, t = table.lower(), tid = ti+1))
        invalid_res_i_str = ", ".join(invalid_res_i_str_array)
        f.write(":- witness({query_variables_str}, {tid_str}), {invalid_res_i_str}.\n".format(i = i, query_variables_str = query_variables_str, tid_str = tid_str,invalid_res_i_str = invalid_res_i_str))
        if i == 1:
            f.write("res(K) :- #count{{Table, Tid: valid_res{i}(Table, Tid, 1)}} = K.\n".format(i = i))
        elif i == 4:
            f.write(":- not #count{{Table, Tid: valid_res{i}(Table, Tid, 1)}} = K+1, res(K).\n".format(i = i))
        else:
            f.write(":- not #count{{Table, Tid: valid_res{i}(Table, Tid, 1)}} = K, res(K).\n".format(i = i))



    # Part 6: Saturate 
    f.write("\n")

    for i in range(1, 5, 1):
        for t in query_tables:
            underscores = ", ".join(["_" for _ in range(query_tables_arity[t])])
            for c in range(2):
                f.write("invalid_res{i}({t}, Tid, {c}) :- invalid_resilience{i}, {t}(Tid, {underscores}).\n".format(i = i, t = t.lower(), c = c, underscores = underscores))
        f.write("\n")


    for i in range(1, 5, 1):
        f.write(":- not invalid_resilience{i}.\n".format(i = i))



    # Part 7 : Add composability check 
    if check_composability:
        f.write("")
        f.write("range_triangle(1..3).")
        f.write("range_domain(1..{d}).\n".format(d = max_domain))

        for i in range(2):
            for j in range(1, endpoint_arity+1, 1):
                f.write("endpoint{i}_constant({j}).\n".format(i=i+1, j = i*endpoint_arity+j))

        # An endpoint witness is one that has a tuple that is entirely composed of endpoint constants
        # Ensure that there is only one endpoint witness for each of the two endpoints
        for i in [1,2]:
            for ti, (table, qvars) in enumerate(query):
                table_vars = [v.upper() for v in qvars]
                table_vars_str = ', '.join(table_vars)
                endpoint_constraints = [ "endpoint{x}_constant({tv})".format(x = i, tv = tv.upper()) for tv in qvars]
                endpoint_constraints_str = ", ".join(endpoint_constraints)

                f.write("endpoint_{i}_witness({tid_str}) :- witness({query_variables_str}, {tid_str}), indb({t}, {table_tid}, 1), {t}({table_tid}, {table_vars_str}), {endpoint_constraints_str}.\n".format(tid_str = tid_str, i = i, query_variables_str = query_variables_str, t = table.lower(), table_tid = 'T'+str(ti+1), table_vars_str = table_vars_str, endpoint_constraints_str = endpoint_constraints_str))

            f.write(":- not #count{{{tid_str}: endpoint_{i}_witness({tid_str})}} = 1.\n".format(tid_str = tid_str, i = i))


        # Ensure that no tuples other than the endpoints consist of only endpoint constants i.e. ensure endpoints are not dominated 
        # for i in range(2):
        #     for t in query_tables:
        #         permitted_count = 0 # Count of tuples in ijp consisting exclusively of endpoints
        #         table_vars = ["V"+str(vi) for vi in range(query_tables_arity[t])]
        #         table_vars_str = ", ".join(table_vars)

        #         endpoint_constraints = [ "endpoint{x}_constant({tv})".format(x = i + 1, tv = tv) for tv in table_vars]
        #         endpoint_constraints_str = ", ".join(endpoint_constraints)
        #         if t == endpoint_table:
        #             break
            
        #         f.write(":- not #count{{ {table_vars_str} : indb({t}, TID, 1), {t}(TID, {table_vars_str}), {endpoint_constraints} }} = {pcount}.\n".format(table_vars_str = table_vars_str, t = t.lower(), endpoint_constraints = endpoint_constraints_str, pcount = permitted_count ))

        # Ensure that no witness contains entirely endpoints
        for i in [1,2]:
            witness_endpoints_constraint = ["endpoint{i}_constant({v})".format(i = i, v = v.upper()) for v in query_variables]
            witness_endpoints_constraint_str = ", ".join(witness_endpoints_constraint)
            f.write(":- witness({query_variables_str}, {tid_str}), {witness_endpoints_constraint_str}.\n".format(query_variables_str = query_variables_str, tid_str = tid_str, witness_endpoints_constraint_str = witness_endpoints_constraint_str))

        # Enure that endpoint tuples occur in only one witness
        # for i in range(2):
        #     for table, table_vars in query:
        #         if table == endpoint_table:
        #             endpoint_table_dict = {table_vars[j].upper(): str(endpoint_arity*i+j+1) for j in range(len(table_vars))}
        #             endpoint_witness = [endpoint_table_dict[v.upper()] if v.upper() in endpoint_table_dict else v.upper() for v in query_variables]
        #             endpoint_witness_str = ", ".join(endpoint_witness)
        #             f.write(":- not #count{{ {tid_str}: witness({endpoint_witness_str}, {tid_str})}} = 1.\n".format(tid_str = tid_str, endpoint_witness_str = endpoint_witness_str))

        f.write("\n")
        f.write("isomorph_map(C, 1, C) :-  endpoint1_constant(C), range_triangle(I). % endpoint1 gets mapped to itself for edge 1\n")
        f.write("isomorph_map(C, 2, X) :-  endpoint1_constant(C), range_triangle(I), X = C + {ea}. %endpoint1 gets mapped to 2 for edge 2 - add endpoint arity\n".format(ea = endpoint_arity))
        f.write("isomorph_map(C, 3, C) :-  endpoint1_constant(C), range_triangle(I). %endpoint1 gets mapped to itself for edge 3\n")

        f.write("isomorph_map(C, 1, C) :-  endpoint2_constant(C), range_triangle(I). %endpoint2 gets mapped to itself for edge 1\n")
        f.write("isomorph_map(C, 2, X) :-  endpoint2_constant(C), range_triangle(I), X = C + {ea}. %endpoint2 gets mapped to 3 for edge 2\n".format(ea = endpoint_arity))
        f.write("isomorph_map(C, 3, X) :-  endpoint2_constant(C), range_triangle(I), X = C + {ea}. %endpoint2 gets mapped to 3 for edge 3\n".format(ea = endpoint_arity))


        f.write("isomorph_map(C, I, X) :- range_triangle(I), range_domain(C), X = C+({d}+1)*I, not endpoint1_constant(C), not endpoint2_constant(C).\n".format(d = max_domain))

        f.write("\n")
        for i in range(1, 3+1):
            for t in query_tables:
                table_vars = []
                table_isomorphic_vars = []
                table_isomorphic_rules = []
                for vi in range(query_tables_arity[t]):
                    table_vars.append('V'+str(vi))
                    table_isomorphic_vars.append('VI'+str(vi))
                    table_isomorphic_rules.append("isomorph_map({table_var},{i},{table_isomorphic_var})".format(i=i, table_var = table_vars[-1], table_isomorphic_var = table_isomorphic_vars[-1]))

                v_str = ",".join(table_vars)
                vi_str = ",".join(table_isomorphic_vars)
                isomorphic_map_constraints = ", ".join(table_isomorphic_rules)
                f.write("ijp_isomorph_{i}_{t}(TID, {vi_str}) :- indb({t}, TID, 1), {t}(TID, {v_str}), {isomorphic_map_constraints}.\n".format(i = i, t = t.lower(), v_str = v_str, vi_str = vi_str, isomorphic_map_constraints = isomorphic_map_constraints))

        # Combine all 3 isomorphs into 1 single edge
        f.write("\n")
        for i in range(1, 3+1):
            for t in query_tables:
                table_vars = ["V"+str(vi) for vi in range(query_tables_arity[t])]
                table_vars_str = ", ".join(table_vars)
                f.write("ijp_isomorph_triangle_{t}(TID, {table_vars}) :- ijp_isomorph_{i}_{t}(TID, {table_vars}).\n".format(t = t.lower(), i = i, table_vars = table_vars_str))

        # Part 3: Compute witnesses
        query_variables_str = ", ".join([qv.upper() for qv in query_variables])
        query_table_str_array = []
        for i, (table, qvars) in enumerate(query):
            qvars_str = ", ".join([v.upper() for v in qvars])
            query_table_str_array.append("{t}(T{tid}, {qvars})".format(t = table.lower(), tid = i+1, qvars = qvars_str))

        triangle_query_table_str = ", ".join(['ijp_isomorph_triangle_'+q for q in query_table_str_array])

        f.write("")
        f.write("ijp_triangle_witness({query_variables_str}) :- {query_table_str}.\n".format(query_variables_str = query_variables_str, query_table_str = triangle_query_table_str))

        f.write(":- number_of_witnesses(K), not  #count{{ {query_variables_str} : ijp_triangle_witness({query_variables_str}) }}= 3*K.\n".format(query_variables_str = query_variables_str))
    
    if optimize:
        f.write(":~ witness({query_variables_str}, {tid_str}). [1@1, {query_variables_str}]\n".format(query_variables_str = query_variables_str, tid_str = tid_str))

    f.write("\n")
    f.write("#show.\n")
    f.write("#show number_of_witnesses(K) : number_of_witnesses(K).\n")
    f.write("#show witness({query_variables_str}) : witness({query_variables_str}, {tid_str}).\n".format(query_variables_str = query_variables_str, tid_str = tid_str))
    f.write("#show res(K) : res(K).\n")

def runCase(case_no):
    """
     Read the details of the experiment from a file with specifications, and run it

    Args:
        case_no (int): The case number to be run
    """
    # Read the details of the experiment from the file 
    expt_case_details =  pd.read_csv(EXPT_CASE_DETAILS_FILE)
    case_details = expt_case_details[expt_case_details['case_no'] == case_no].iloc[0].to_dict()
    
    generate_asp_program(case_no, case_details['query_name'], case_details['endpoint_table'], int(case_details['max_domain']), optimize = case_details['optimize'], check_composability = case_details['check_composability'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a ijp experiment')
    parser.add_argument('case', type=int, help="The case number to be run (Details specified in $EXPT_CASE_DETAILS_FILE)")
    args = parser.parse_args()
    runCase(args.case)
