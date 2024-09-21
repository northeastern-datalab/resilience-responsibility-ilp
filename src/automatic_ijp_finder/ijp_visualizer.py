import argparse
import matplotlib.pyplot as plt
import pandas as pd
import hypernetx as hnx
import sys
import re

from src.resilience_responsibility_solver.src.constants import queries

def generate_ijp_visualization(query, clingo_file, OUTPUT_FILE = ''):
    '''Generates a visualization of the IJP from a clingo output file
    Input - query: str - the query name as defined in src.constants.queries
            clingo_file: str - the path to the clingo output file
            OUTPUT_FILE: str (optional) - the folder where the generated pdf should be saved
    '''

    witness_string = process_clingo_output(clingo_file)
    hypergraph = build_hypergraph(query, witness_string)
    visualize_hypergraph(hypergraph, OUTPUT_FILE = OUTPUT_FILE)

def process_clingo_output(clingo_file):
    '''Extracts the IJP from a clingo output file
    Input - clingo_file: str - the path to the clingo output file
    '''
    # Read the clingo output file
    with open(clingo_file, 'r') as file:
        content = file.read()

    # Use regex to find all words that start with 'witness'
    witness_words = re.findall(r'\bwitness\(\d+,\d+,\d+\)', content)

    return ' '.join(witness_words)

def build_hypergraph(queryname, witneses_string):
    clingo_output_witnesses = [[int(x) for x in c[len('witness')+1:-1].split(',')] for c in witneses_string.split()]
    query = queries[queryname]
    query_variables = list(set([v for (_, qvars) in query for v in qvars]))
    query_variables.sort()
    clingo_output_witnesses_df = pd.DataFrame(clingo_output_witnesses, columns=query_variables)

    witness_edges = []
    for w in clingo_output_witnesses_df.iterrows():
        witness_edge = []
        for table, table_var in query:
            tuple_node = table + '('
            for tv in table_var:
                tuple_node += str(w[1].loc[tv])+','
            tuple_node = tuple_node[:-1]
            tuple_node += ')'
            witness_edge.append(tuple_node)
        witness_edges.append(witness_edge)

    # Convert the edges into the hypergraph
    witness_hypergraph = {i: tuple(witness_edges[i]) for i in range(len(witness_edges))}
    H = hnx.Hypergraph(witness_hypergraph)

    return H

def visualize_hypergraph(H, OUTPUT_FILE = ''):
    # Draw the hypergraph! 
    hnx.draw(H, with_edge_labels = False, nodes_kwargs={
                        'facecolors': "blue",
                    }, node_labels_kwargs={
                        'fontsize':18,
                        'color':"blue",
                        'weight': 'ultralight'
                    }, edges_kwargs={
                        'linewidths':3
                    })
    plt.savefig(OUTPUT_FILE+'.pdf', format='pdf')

def main(args): 
    parser = argparse.ArgumentParser(description='Visualize an automatically generated IJP from a clingo output file')
    parser.add_argument('query', type=str, help="The query name as defined in src.constants.queries")
    parser.add_argument('clingo_file', type=str, help="Folder and file name of the clingo output file")
    parser.add_argument('--output_file', type=str, help="The folder where the generated pdf should be saved")
    args = parser.parse_args()
    generate_ijp_visualization(args.query, args.clingo_file, OUTPUT_FILE = args.output_file)

if __name__ == "__main__":
    main(sys.argv)