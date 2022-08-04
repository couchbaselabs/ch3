#!/bin/bash

echo Delete Buckets

Url=${1:-127.0.0.1}
Auth=${2:-Administrator:password}
replica=${3:-0}
Site=http://$Url:8091/pools/default/buckets/
bucket_memory=(2560)
bucket=(bench)
collections=(customer district history item neworder orders stock warehouse supplier nation region)

numberOfBuckets=${#bucket[@]}
echo POST /pools/default/buckets

echo "Deleting Buckets"

for i in "${collections[@]}"
do
echo curl -u $Auth $Site$i
curl -X DELETE -u $Auth $Site$i
done
for i in "${bucket[@]}"
do
echo curl -u $Auth $Site$i
curl -X DELETE -u $Auth $Site$i
done

# echo rm -rf /run/data/
# rm -rf /run/data/

echo "Creating Buckets"

# Bucket Params
Site=http://$Url:8091/pools/default/buckets
port=${4:-11224}
low=${4:-3}
high=${4:-8}

# Create bucket
for ((i=0; i < 1 ; i++))
do
	echo curl -X POST -u $Auth -d name=${bucket[$i]} -d ramQuotaMB=${bucket_memory[$i]} -d authType=none $Site -d threadsNumber=$high -d replicaNumber=$replica -d evictionPolicy=fullEviction
let port\+=1
curl -X POST -u $Auth -d name=${bucket[$i]} -d ramQuotaMB=${bucket_memory[$i]} -d authType=none  $Site -d threadsNumber=$high -d replicaNumber=$replica -d evictionPolicy=fullEviction
let port\+=1
done

echo "sleep 30 seconds"
sleep 30

#create scope
echo curl $Site/bench/scopes -u $Auth -d 'name=ch3'
curl $Site/bench/scopes -u $Auth -d 'name=ch3'

sleep 30
#create collections
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=customer'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=customer'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=district'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=district'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=history'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=history'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=item'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=item'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=neworder'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=neworder'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=orders'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=orders'
#echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=ORDER_LINE'
#curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=ORDER_LINE'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=stock'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=stock'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=warehouse'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=warehouse'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=supplier'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=supplier'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=nation'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=nation'
echo curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=region'
curl $Site/bench/scopes/ch3/collections -u $Auth -d 'name=region'