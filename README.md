# Resilience and Responsibility Code

[![Project Page](https://img.shields.io/badge/Project%20Page-blue.svg)](https://northeastern-datalab.github.io/unified-reverse-data-management/)
[![Sigmod Paper](https://img.shields.io/badge/Paper-SIGMOD24-blue.svg)](https://doi.org/10.1145/3626715)
[![Arxiv Paper](https://img.shields.io/badge/Paper-arXiv-blue.svg)](https://arxiv.org/abs/2212.08898)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains code to solve Resilience and Causal Responsibility via Integer Linear Programming (ILP) and Linear Programming (LP) relaxations.

**Resilience**: What is the minimal number of tuples to delete from a database in order to eliminate all query answers?

**Causal Responsibility**: What is a minimum subset of tuples to remove from a database to make a given input tuple ``counterfactual''?

The src repository is divided into two parts:
-  ``automatic_ijp_finder``: The code in this folder can be used to check the hardness of solving resilience and causal responsibility for a given query by automatically searching for hardness gadgets or Independent Join Paths (IJPs).

- ``resilience_responsibility_Solver``: The code translates the problem of determining resilience (or responsibility) for a given query and database (and tuple) into Integer Linear Programs (ILPs) and then solves them with existing solvers (e.g. Gurobi).

Details and instructions for running the code in both parts are in the READMEs of the respective folders.

## Reproducibility: SIGMOD 2024

The repository contains a description for reproducing the experimental results reported in our research paper in [sigmod_expts.ipynb](Resilience_Responsibility_Solver/expt/expt_plots/sigmod_expts.ipynb)

1. Install Prerequisites
    1. Download the [Gurobi optimizer](https://www.gurobi.com/downloads/). **A free Gurobi academic license is required to run the code**. Request an Academic Named-User License and follow instructions to install gurobi on your computer.
    2. Install the Answer Set Programming Solver [Clingo](https://potassco.org/clingo/) following instructions at https://potassco.org/clingo/
        * We use clingo version 5.7.1
        * Use conda for Linux/ Windows and brew for MAC OS
    3. (Optional, highly recommended) Set up a [virtual environment](https://docs.python.org/3/library/venv.html).
    4. Install the requirements in ``requirements.txt``
    ```
    pip install -r requirements.txt
    ```
2. For Figure 3 - automatic hardness gadgets: we use clingo, an Answer Set Propramming Solver to help us prove computational complexity results automatically. 
This part is highly compute intensive - the hardest subfigure to generate took 15 hours on a 64-core processor. However, the fastest example takes under a minute end-to-end. More details are in [SIGMOD_Reproducibility/Fig-3/README.md](SIGMOD_Reproducibility/Fig-3/README.md)

3. For Figures 5,6, and 7 in the paper - we generate data instances (either through tpch-dbgen or via our own random instance generator), and measure the performance of our algorithms as they scale. The data generation process, algorithms, and plotting scripts are all included. More details are in [SIGMOD_Reproducibility/Fig-5,6,7/README.md](SIGMOD_Reproducibility/Fig-5,6,7/README.md)

## Citation
If you use this code in your work, please cite: 
```bibtex
@inproceedings{DBLP:conf/sigmod/MG24,
  author    = {Neha Makhija and Wolfgang Gatterbauer},
  title     = {A Unified Approach for Resilience and Causal Responsibility with Integer Linear Programming (ILP) and LP Relaxations},
  booktitle = {International Conference on Management of Data (SIGMOD)},
  publisher = {{ACM}},
  year      = {2024},
  doi       = {https://doi.org/10.1145/3626715},
  url       = {https://arxiv.org/abs/2212.08898}
}
```

## License
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

## Contributors
- [Neha Makhija](https://nehamakhija.github.io/)
- [Wolfgang Gatterbauer](http://gatterbauer.name)