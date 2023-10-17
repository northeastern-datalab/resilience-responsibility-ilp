import pandas as pd
import random

SNAP_DATA_FILE = 'data/snap/414-edges.txt'


def load_snap_data(sample_percent = 100, n_tables = 5, bag_semantics = False):
    """
    From the snap dataset build a random sample and split into tables
    Args:
        sample_percent: The percent of edges to be sampled
        n_tables: The number of tables to be split into        
    """
    # if random from [0,1] interval is greater than sample_percent the row will be skipped
    sampled_snap = pd.read_csv(
            SNAP_DATA_FILE,
            header = None, 
            sep=' ',
            skiprows = lambda i: i>0 and random.random() > (sample_percent/100)
    )
    database_instance = {}
    for i in range(n_tables):
        database_instance['R'+str(i+1)] = sampled_snap[(sampled_snap[0] + sampled_snap[1]) % n_tables == i].values.tolist()

    tuple_weights = {}

    return (database_instance, tuple_weights)