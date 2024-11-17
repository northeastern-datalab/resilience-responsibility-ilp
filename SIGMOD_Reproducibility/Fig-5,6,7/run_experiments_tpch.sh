# Run the experiments for Figure 6 - defined by case 1 and 2 in src/resilience_responsibility_solver/expt/tpch/tpch_resp_expt_cases.py
{ cd src/resilience_responsibility_solver ; python3 -m expt.tpch.tpch_resp_expt 1 ; }
{ cd src/resilience_responsibility_solver ; python3 -m expt.tpch.tpch_resp_expt 2 ; }