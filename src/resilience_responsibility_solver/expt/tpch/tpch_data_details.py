"""
Tracks the tpch tables to be populated for each query.

E.g. for the SJ-chain query R(x,y)R(y,z), we populate the table R with lineitem(shipdate, commitdate)
This runs the query, find line item pairs where the ship date is same as commit date
"""

tpch_query_tables = {
    "SJ-chain": {"R": ("lineitem",["shipdate", "commitdate"])},
    "SJ-conf": {"R": ("lineitem",["linenumber", "shipdate"])},
    "5Cycle": {
                "R1": ("customer",["nationkey", "custkey"]),
                "R2": ("orders",["custkey", "orderkey"]),
                "R3": ("lineitem",["orderkey", "ps_id"]),
                "R4": ("partsupp",["id", "suppkey"]),
                "R5": ("supplier",["suppkey", "nationkey"]),
                },
    "5Chain": {
                "R1": ("customer",["name", "custkey"]),
                "R2": ("orders",["custkey", "orderkey"]),
                "R3": ("lineitem",["orderkey", "ps_id"]),
                "R4": ("partsupp",["id", "suppkey"]),
                "R5": ("supplier",["suppkey", "name"]),
                }

}

tpch_schema = {
    "lineitem": ["id","orderkey","ps_id","linenumber",
        "quantity","extendedprice","discount","tax",
        "returnflag","linestatus","shipdate","commitdate",
        "receiptdate","shipinstruct","shipmode","comment"],
    "partsupp": ["id", "partkey", "suppkey", "availqty", "supplycost", "comment"],
    "supplier":["suppkey", "name", "address", "nationkey", "phone", "acctbal", "comment"],
    "customer":["custkey", "name", "address", "nationkey", "phone", "acctbal", "mktsegment", "comment" ],
    "orders": ["orderkey", "custkey", "orderstatus", "totalprice", "orderdate", "orderpriority", "cleark", "shippriority", "comment"]
}