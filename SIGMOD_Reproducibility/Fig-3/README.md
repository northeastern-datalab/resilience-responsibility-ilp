# Figure 3: Automatically generated and visualized IJPs

### Figure Description

Figure 3 consists of 5 subfigures as shown in [the folder reference-output](reference-output/).
These 5 sub-figures are automatically generated hardness gadgets that together with Theorem 7.4 in the paper show the hardness of resilience for the queries in question. 

### End-to-End Pipeline to Generate Figure

There is a three-step process to generate the figures from scratch
1. Generate the Answer Set Program that searches for an IJP using a query as input
2. Run the Answer Set Program using the solver clingo. **This step is time intensive - 3 queries in this experiment take 2 hours each on an 8 core machine, and 1 query (z6) takes 15 hours on a 64 core machine**
3. Visualize the result of the Answer Set Program as a hypergraph

### Instructions to Reproduce Figures

1. Make sure all prerequisites are satisfied as specified in [README.md](../../README.md)
2. Run 
```
bash SIGMOD_Reproducibility/Fig-3/generate_figure_3.sh
```
You will be prompted to enter the number of cores you can utilize.

3. You can also run the process in the background after entering the number of cores by  
    * Pressing Ctrl+z to put the current process to sleep and return to your shell. 
    * Running the ``bg`` command to then resume it in the background