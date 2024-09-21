STORAGE_PATH="SIGMOD_Reproducibility/Fig-3/output/"
read -p "Enter the number of cores (1-64, 64 ideal, and 8+ recommended) [8]" cores
cores=${cores:-8}

#### Query "SJ-3-perm-R-SxyC"
# Expected total time: Under a minute  (8 cores)

# Step 1: Generate the ASP program for different queries with the endpoints and domain sizes as used in the paper
query="SJ-3-perm-R-SxyC"
endpoint="C"
domain_size=4
python -m src.automatic_ijp_finder.ijp_asp_generator ${query} ${endpoint} ${domain_size} --program_save_folder $STORAGE_PATH
# Step 2: Use the answer set programming solver clingo to find if there exist any IJPs for the given query and domain size
# Expected time (8 cores): 3seconds
clingo "${STORAGE_PATH}${query}-${endpoint}-${domain_size}.dl" -t ${cores} > "${STORAGE_PATH}clingo_output-${query}.txt"
# Step 3: Visualize the IJPs found
python -m src.automatic_ijp_finder.ijp_visualizer ${query} ${STORAGE_PATH}clingo_output-${query}.txt --output_file ${STORAGE_PATH}${query}


#### Query "SJ-3-perm-R-ASxy"
# Expected total time: 2 hours  (8 cores)

# Step 1: Generate the ASP program for different queries with the endpoints and domain sizes as used in the paper
query="SJ-3-perm-R-ASxy"
endpoint="A"
domain_size=6
python -m src.automatic_ijp_finder.ijp_asp_generator ${query} ${endpoint} ${domain_size} --program_save_folder $STORAGE_PATH
# Step 2: Use the answer set programming solver clingo to find if there exist any IJPs for the given query and domain size
# Expected time (8 cores): 7000 seconds
clingo "${STORAGE_PATH}${query}-${endpoint}-${domain_size}.dl" -t ${cores} > "${STORAGE_PATH}clingo_output-${query}.txt"
# Step 3: Visualize the IJPs found
python -m src.automatic_ijp_finder.ijp_visualizer ${query} ${STORAGE_PATH}clingo_output-${query}.txt --output_file ${STORAGE_PATH}${query}



#### Query "SJ-3-perm-R-SxyB"
# Expected total time: 2 hours  (8 cores)

# Step 1: Generate the ASP program for different queries with the endpoints and domain sizes as used in the paper
query="SJ-3-perm-R-SxyB"
endpoint="B"
domain_size=6
python -m src.automatic_ijp_finder.ijp_asp_generator ${query} ${endpoint} ${domain_size} --program_save_folder $STORAGE_PATH
# Step 2: Use the answer set programming solver clingo to find if there exist any IJPs for the given query and domain size
# Expected time (8 cores): 6400 seconds
clingo "${STORAGE_PATH}${query}-${endpoint}-${domain_size}.dl" -t ${cores} > "${STORAGE_PATH}clingo_output-${query}.txt"
# Step 3: Visualize the IJPs found
python -m src.automatic_ijp_finder.ijp_visualizer ${query} ${STORAGE_PATH}clingo_output-${query}.txt --output_file ${STORAGE_PATH}${query}




#### Query "SJ-3-chain-conf-s"
# Expected total time: 2 hours (8 cores)
query="SJ-3-chain-conf-s"
endpoint="R"
domain_size=6
python -m src.automatic_ijp_finder.ijp_asp_generator ${query} ${endpoint} ${domain_size} --program_save_folder $STORAGE_PATH
# Step 2: Use the answer set programming solver clingo to find if there exist any IJPs for the given query and domain size
# Expected time (8 cores): 5000 seconds
clingo "${STORAGE_PATH}${query}-${endpoint}-${domain_size}.dl" -t ${cores} > "${STORAGE_PATH}clingo_output-${query}.txt"
# Step 3: Visualize the IJPs found
python -m src.automatic_ijp_finder.ijp_visualizer ${query} ${STORAGE_PATH}clingo_output-${query}.txt --output_file ${STORAGE_PATH}${query}



#### Query "SJ-z6"
# Expected total time: 15 hours (64 cores)
query="SJ-z6"
endpoint="A"
domain_size=7
python -m src.automatic_ijp_finder.ijp_asp_generator ${query} ${endpoint} ${domain_size} --program_save_folder $STORAGE_PATH
# Step 2: Use the answer set programming solver clingo to find if there exist any IJPs for the given query and domain size
# Expected time (64 cores): 50000 seconds
clingo "${STORAGE_PATH}${query}-${endpoint}-${domain_size}.dl" -t ${cores} > "${STORAGE_PATH}clingo_output-${query}.txt"
# Step 3: Visualize the IJPs found
python -m src.automatic_ijp_finder.ijp_visualizer ${query} ${STORAGE_PATH}clingo_output-${query}.txt --output_file ${STORAGE_PATH}${query}