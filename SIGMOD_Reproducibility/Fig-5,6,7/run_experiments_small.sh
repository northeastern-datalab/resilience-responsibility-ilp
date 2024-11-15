# Run the experiments for Figure 5 but on smaller instances - defined by case 4 in src/resilience_responsibility_solver/expt/synthetic/res_synthetic_data_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 4 ; }

# Run the experiments for Figure 7 but on smaller instances - defined by case 5 and 6 in src/resilience_responsibility_solver/expt/synthetic/res_synthetic_data_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 5 ; }
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 6 ; }