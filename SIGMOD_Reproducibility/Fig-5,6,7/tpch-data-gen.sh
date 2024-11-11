for sf in 0.01 0.015 0.021 0.032 0.046 0.068 0.1 0.15 0.21 0.32 0.46 0.68 1
do

cd data/tpch/

mkdir -p data/tpch-sf$sf
# Move the dbgen and dists.dss files to the new folder
newfolder="data/tpch-sf$sf"
echo $newfolder
# echo $ls
cp tpch-dbgen/dbgen $newfolder/dbgen
cp tpch-dbgen/dists.dss $newfolder/dists.dss

cd $newfolder/

./dbgen -s $sf

cd ../../../..

done