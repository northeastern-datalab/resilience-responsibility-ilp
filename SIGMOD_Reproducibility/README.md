# SIGMOD Reproducibility 

We split the reproducibility section into two parts:

1. For Figure 3 in the paper- automatic hardness gadgets: we use clingo, an Answer Set Propramming Solver to help us prove computational complexity results automatically. 
This part is highly compute intensive - the hardest subfigure to generate took 15 hours on a 64-core processor. However, the fastest example takes under a minute end-to-end. More details are in [Fig-3/README.md](Fig-3/README.md)

2. For Figures 5,6, and 7 in the paper dealing with experimental evaluation of the algorithms for resilience and responsibility - we generate data instances (either through tpch-dbgen or via our own random instance generator), and measure the performance of our algorithms as they scale. The data generation process, algorithms, and plotting scripts are all included. More details are in [Fig-5,6,7/README.md](Fig-5,6,7/README.md)