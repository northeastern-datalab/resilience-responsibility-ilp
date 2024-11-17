# Figure 5,6,7 : Experimental Scalibility Results for Resilience and Responsibility Problems

### Instructions to Reproduce Figures 5,6,7
 
1. Make sure all prerequisites are satisfied as specified in [README.md](../../README.md)
2. Download TPC-H data
    1. Clone the dbgen repository
    ```
        cd data/tpch
        
        git clone https://github.com/electrum/tpch-dbgen.git

        cd ../..
    ```
    2. Build dbgen by running
    ```
        cd data/tpch/tpch-dbgen
        make
    ```
    3. Run the ``tpch-data-gen.sh`` script to generate the TPC-H data at various scale factors
    ```
        bash SIGMOD_Reproducibility/Fig-5,6,7/tpch-data-gen.sh 
    ```
    4. You should see 13 folders in [data/tpch/data](data/tpch/data), corresponding to data generated for 13 scale factors.

3. Test Gurobi install by running ```gurobi_cl```

4. Run the experiments
    ```
        bash SIGMOD_Reproducibility/Fig-5,6,7/run_experiments.sh 
    ```

4(b). Optionally just run the experiments for Fig 5 and 7 for smaller sizes (takes <3 hours to terminate)
    ```
        bash SIGMOD_Reproducibility/Fig-5,6,7/run_experiments_small.sh 
    ```

4(c). Optionally just run the experiments for Fig 6 on tpch data (takes <30min to terminate)
    ```
        bash SIGMOD_Reproducibility/Fig-5,6,7/run_experiments_tpch.sh 
    ```


5. Visualize the output: We have a Jupyter notebook [sigmod_expts.ipynb](sigmod_expts.ipynb) code to read the experimental output and generate the plots by calling methods from [../../src/resilience_responsibility_solver/plot/](../../src/resilience_responsibility_solver/plot/).

The default notebook uses the reference experimental data to start with, but this can be toggled by setting ``use_reference_data = False``.
To use the data generated in smaller sized experiments set ``use_small_expt = True``.