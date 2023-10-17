# Resilience and Responsibility Code

[![Project Page](https://img.shields.io/badge/Project%20Page-blue.svg)](https://northeastern-datalab.github.io/unified-reverse-data-management/)
[![Sigmod Paper](https://img.shields.io/badge/Paper-SIGMOD24-blue.svg)](https://arxiv.org/abs/2212.08898)
[![Arxiv Paper](https://img.shields.io/badge/Paper-arXiv-blue.svg)](https://arxiv.org/abs/2212.08898)
[![License](https://img.shields.io/badge/License-Apache%202.0-orange.svg)](https://opensource.org/licenses/Apache-2.0)

This repository contains code to solve Resilience and Causal Responsibility via Integer Linear Programming (ILP) and Linear Programming (LP) relaxations.

**Resilience**: What is the minimal number of tuples to delete from a database in order to eliminate all query answers?

**Causal Responsibility**: What is a minimum subset of tuples to remove from a database to make a given input tuple ``counterfactual''?

The repository is divided into two parts:
-  ``IJP_Finder``: The code in this folder can be used to check the hardness of solving resilience and causal responsibility for a given query by automatically searching for hardness gadgets or IJPs.

- ``Resilience_Responsibility_Solver``: The code translates the problem into Integer Linear Programs (ILPs) and then solves them with existing solvers (e.g. Gurobi).

Details and instructions for running the code in both parts are in the READMEs of the respective folders.

## Reproducibility: SIGMOD 2024

The repository contains a description for reproducing the experimental results reported in our research paper in [sigmod_expts.ipynb](Resilience_Responsibility_Solver/expt/expt_plots/sigmod_expts.ipynb)

## Citation
If you use this code in your work, please cite: 
```bibtex
@inproceedings{DBLP:conf/sigmod/MG24,
  author    = {Neha Makhija and Wolfgang Gatterbauer},
  title     = {A Unified Approach for Resilience and Causal Responsibility with Integer Linear Programming (ILP) and LP Relaxations},
  booktitle = {International Conference on Management of Data (SIGMOD)},
  publisher = {{ACM}},
  year      = {2024},
  url       = {https://doi.org/10.1145/3626715},
}
```

## License
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

## Contributors
- [Neha Makhija](https://nehamakhija.github.io/)
- [Wolfgang Gatterbauer](http://gatterbauer.name)