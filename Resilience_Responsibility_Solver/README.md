# Resilience and Responsibility Code

This repository contains code to run Resilience and Responsibility ILPs.

Summary of contents:
- ``expt``: Code to run predefined experiments, such as resilience for a specific query over a certain type of data (synthetic, snap or tpch) or to find IJPs
    - To define a new experiment, you can add a new experiment "case" in the case csv files in the synthetic, tpch and snap folder.
    - Existing figures can be viewed in the notebooks in ``expt/expt_plots`` and the file ``SIGMOD_expts.ipynb`` includes all the plots that are in the paper.
- ``plot``: contains scripts to plot raw data generated from the experiments
- ``src``: contains src code- which includes the resilience and responsibility ILPs

## Requirements 

In addition to Python library mentioned in ``requirements.txt``, we use [Gurobi ILP Solver](https://www.gurobi.com/).
A free academic license is [available](https://www.gurobi.com/academia/academic-program-and-licenses/).