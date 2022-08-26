# CH3 Benchmark
CH3 measures a mixed workload performance with transactional, analytical and full test search (FTS) queries in Couchbase Server. However, it is not specific to Couchbase, rather it can be implemented on other NoSQL platforms that support query, analytics and search services.

** For Couchbase, we have implemented "nestcollectionsdriver.py". Create a new file in the 'drivers' directory for your system that follows 
the proper naming convention. For example, the driver class in "nestcollectionsdriver.py" is 'NestcollectionsDriver'.

*** CH3 supports FTS queries, transactional queries based on TPC-C, and TPC-H-equivalent analytical queries.

## Executing CH3 in a Couchbase cluster
In the following commands, replace the IP addresses with the appropriate ones. Besides, the parameters we use are:
```
userid = Administrator
password = password
warehouses = 10
aclients = 1
fclients = 40
tclients = 40
```
1. Create the "bench" bucket with scope and collections
```
sh -x util/cbcrbucketcollection.sh <Data_IPAddress> Administrator:password
```
2. Create GSI indexes
```
/opt/couchbase/bin/cbq -e=<Index_IPAddress>:8093 -u=Administrator -p=password < util/cbcrindexcollection.sql
```
3. Prepare shadow for analytics
```
/opt/couchbase/bin/cbq -e=<Analytics_IPAddress>:8095 -u=Administrator -p=password < util/crdataset.n1ql
/opt/couchbase/bin/cbq -e=<Analytics_IPAddress>:8095 -u=Administrator -p=password < util/crdatasetindexes.n1ql
```
4. Create FTS indexes
```
sh -x util/cbcrftsindexcollection.sh <FTS_IPAddress> Administrator:password
```
5. Load data into "bench" bucket
```
python3 ./tpcc.py --warehouses 10 --no-execute nestcollections \
--data-url <Data_IPAddress> --userid Administrator --password password \
--datasvc-bulkload --tclients 40
```
Note that we have three load modes: (1) datasvc-bulkload, (2) datasvc-load, (3) qrysvc-load. In the above command, we have "nestcollections" for the driver name.

6. Execute CH3 benchmark with appropriate number of Txn, FTS and analytical clients
```
python3 ./tpcc.py --warehouses 10 --aclients 1 --tclients 40 --fclients 40 \
--query-url <Query_IPAddress>:8093 --analytics-url <Analytics_IPAddress>:8095 --fts-url <FTS_IPAddress>:8094 \
--query-iterations 2 --warmup-query-iterations 1 nestcollections \
--userid Administrator --password password --no-load
```
If there is no analytical clients, then we need "duration" parameter.
```
python3 ./tpcc.py --warehouses 10 --tclients 40 --aclients 0 --fclients 40 \
--query-url <Query_IPAddress>:8093 --analytics-url <Analytics_IPAddress>:8095 --fts-url <FTS_IPAddress>:8094 \
--duration 180 --warmup-duration 90 nestcollections \
--userid Administrator --password password --no-load
```

## Useful Links:
CH3 extends CH2 benchmark framework.

ch2: https://github.com/couchbaselabs/ch2

py-tpcc: https://github.com/couchbaselabs/py-tpcc
