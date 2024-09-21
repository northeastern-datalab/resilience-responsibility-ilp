# Run the experiments for Figure 5 - defined by case 1 in src/resilience_responsibility_solver/expt/synthetic/res_synthetic_data_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 1 ; }

# Run the experiments for Figure 7 - defined by case 2 and 3 in src/resilience_responsibility_solver/expt/synthetic/res_synthetic_data_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 2 ; }
{ cd src/resilience_responsibility_solver ; python3 -m expt.synthetic.res_synthetic_expt 3 ; }

# Run the experiments for Figure 6 - defined by case 4 and 5 in src/resilience_responsibility_solver/expt/tpch/tpch_resp_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.tpch.tpch_resp_expt 1 ; }
{ cd src/resilience_responsibility_solver ; python3 -m expt.tpch.tpch_resp_expt 2 ; }