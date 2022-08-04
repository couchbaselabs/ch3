#!/bin/bash

Url=${1:-127.0.0.1}
Auth=${2:-Administrator:password}

# FTS Index Params
Site=http://$Url:8094/api/index
customerFTSI=$Site/customerFTSI
itemFTSI=$Site/itemFTSI
ordersFTSI=$Site/ordersFTSI

multiFTSI=$Site/mutiCollectionFTSI
nonAnalyticFTSI=$Site/nonAnalyticFTSI
ngramFTSI=$Site/ngramFTSI

echo “Creating FTS Indexes”

# Create customer FTS Index
echo “Create Customer FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $customerFTSI -d \
'{
  "type": "fulltext-index",
  "name": "customerFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {},
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": false,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": false,
      "index_dynamic": false,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.customer": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "c_city": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "c_city",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "c_data",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_first": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "keyword",
                  "index": true,
                  "name": "c_first",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_since": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "c_since",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_street_1": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "c_street_1",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'


# Create item FTS Index
echo “Create Item FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $itemFTSI -d \
'{
  "type": "fulltext-index",
  "name": "itemFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {},
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": false,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": false,
      "index_dynamic": false,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.item": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "i_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "i_data",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "i_name": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "i_name",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'


# Create orders FTS Index
echo “Create Orders FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $ordersFTSI -d \
'{
  "type": "fulltext-index",
  "name": "ordersFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {},
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": false,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": false,
      "index_dynamic": false,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.orders": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "o_entry_d": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "date_format": "dateTimeOptional",
                  "index": true,
                  "name": "o_entry_d",
                  "store": true,
                  "type": "datetime"
                }
              ]
            },
            "o_id": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "o_id",
                  "store": true,
                  "type": "number"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'


# Create multi-coleection FTS Index
echo “Create multi-collection FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $multiFTSI -d \
'{
  "type": "fulltext-index",
  "name": "mutiCollectionFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {},
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": true,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": false,
      "index_dynamic": true,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.customer": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "c_city": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "c_city",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_d_id": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "c_d_id",
                  "store": true,
                  "type": "number"
                }
              ]
            },
            "c_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "c_data",
                  "store": true,
                  "type": "text"
                }
              ]
            },
            "c_street_1": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "c_street_1",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        },
        "ch3.district": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "d_city": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "d_city",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        },
        "ch3.orders": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "o_entry_d": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "index": true,
                  "name": "o_entry_d",
                  "store": true,
                  "type": "datetime"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'


# Create non-analytical FTS Index
echo “Create non-analytical FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $nonAnalyticFTSI -d \
'{
  "type": "fulltext-index",
  "name": "nonAnalyticFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {},
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": false,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": false,
      "index_dynamic": false,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.customer": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "c_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "include_term_vectors": true,
                  "index": true,
                  "name": "c_data",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        },
        "ch3.stock": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "s_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "keyword",
                  "index": true,
                  "name": "s_data",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        },
        "ch3.supplier": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "su_address": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "en",
                  "index": true,
                  "name": "su_address",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'

# Create ngram FTS Index
echo “Create edge-ngram FTS Index”

curl -XPUT -H "Content-Type: application/json" \
-u $Auth $ngramFTSI -d \
'{
  "type": "fulltext-index",
  "name": "ngramFTSI",
  "uuid": "",
  "sourceType": "gocbcore",
  "sourceName": "bench",
  "sourceUUID": "",
  "planParams": {
    "maxPartitionsPerPIndex": 1024,
    "indexPartitions": 1
  },
  "params": {
    "doc_config": {
      "docid_prefix_delim": "",
      "docid_regexp": "",
      "mode": "scope.collection.type_field",
      "type_field": "type"
    },
    "mapping": {
      "analysis": {
        "analyzers": {
          "custom": {
            "char_filters": [
              "asciifolding"
            ],
            "token_filters": [
              "to_lower",
              "edgengram"
            ],
            "tokenizer": "unicode",
            "type": "custom"
          }
        },
        "token_filters": {
          "edgengram": {
            "back": false,
            "max": 7,
            "min": 3,
            "type": "edge_ngram"
          }
        }
      },
      "default_analyzer": "standard",
      "default_datetime_parser": "dateTimeOptional",
      "default_field": "_all",
      "default_mapping": {
        "dynamic": false,
        "enabled": false
      },
      "default_type": "_default",
      "docvalues_dynamic": true,
      "index_dynamic": true,
      "store_dynamic": false,
      "type_field": "_type",
      "types": {
        "ch3.history": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "h_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "custom",
                  "index": true,
                  "name": "h_data",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        },
        "ch3.stock": {
          "dynamic": false,
          "enabled": true,
          "properties": {
            "s_data": {
              "dynamic": false,
              "enabled": true,
              "fields": [
                {
                  "analyzer": "custom",
                  "index": true,
                  "name": "s_data",
                  "store": true,
                  "type": "text"
                }
              ]
            }
          }
        }
      }
    },
    "store": {
      "indexType": "scorch",
      "segmentVersion": 15
    }
  },
  "sourceParams": {}
}'


echo "sleep 30 seconds"
sleep 30