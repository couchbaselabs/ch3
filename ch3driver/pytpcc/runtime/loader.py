# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Copyright (C) 2011
# Andy Pavlo
# http:##www.cs.brown.edu/~pavlo/
#
# Original Java Version:
# Copyright (C) 2008
# Evan Jones
# Massachusetts Institute of Technology
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
# -----------------------------------------------------------------------

import os
import profile
import sys

import logging
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
import random
from random import randint, shuffle, randrange, sample
from pprint import pprint,pformat

import constants
from util import *
from faker import Faker
fake = Faker()

def load(fname):
  f = open(fname, 'r')
  data = []
  for line in f.readlines():
    data.append(line.strip())
  f.close()
  return data

def intRange(start,end):
    return random.randint(start,end)

dataDir = os.path.dirname(os.path.realpath(__file__))
# Path to zip percentile files:
ZIPDATA = os.path.join(dataDir, '../../../ch3data/zipdata')
PctFiles = []
# Load all our PopPercentile files into a array of arrays.
popPercentiles=[]
for _ in range(0,100):
  percentileNum = "0" + str(_)
  fileName = ZIPDATA + "/PopPercentile"+percentileNum[-2:]+".txt"
  popPercentiles.append(load(fileName))

# Path to sample product data file:
PRODUCT_FILE = os.path.join(dataDir, '../../../ch3data/itemdata/flipkart_ecommerce.csv')
products = load(PRODUCT_FILE)

class Loader:

    def __init__(self, handle, scaleParameters, w_ids, needLoadItems):
        self.handle = handle
        self.scaleParameters = scaleParameters
        self.w_ids = w_ids
        self.needLoadItems = needLoadItems
        self.batch_size = 2500
        self.numSecsPerDay = 86400
    ## ==============================================
    ## execute
    ## ==============================================
    def execute(self):

        ## Item Table
        if self.needLoadItems:
            logging.debug("Loading ITEM table")
            self.loadItems()
            self.handle.loadFinishItem()

            ## Load CH tables
            self.loadSupplier()
            self.loadNation()
            self.loadRegion()

        ## Then create the warehouse-specific tuples
        for w_id in self.w_ids:
            self.loadWarehouse(w_id)
            self.handle.loadFinishWarehouse(w_id)
        ## FOR

        return (None)

    ## ==============================================
    ## loadItems
    ## ==============================================
    def loadItems(self):
        ## Select 10% of the rows to be marked "original"
        originalRows = rand.selectUniqueIds(self.scaleParameters.items // 10, 1, self.scaleParameters.items)

        ## Load all of the items
        tuples = [ ]
        total_tuples = 0
        for i in range(1, self.scaleParameters.items+1):
            original = (i in originalRows)
            tuples.append(self.generateItem(i, original))
            total_tuples += 1
            if len(tuples) == self.batch_size:
                logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_ITEM, total_tuples, self.scaleParameters.items))
                self.handle.loadTuples(constants.TABLENAME_ITEM, tuples)
                tuples = [ ]
        ## FOR
        if len(tuples) > 0:
            logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_ITEM, total_tuples, self.scaleParameters.items))
            self.handle.loadTuples(constants.TABLENAME_ITEM, tuples)
    ## DEF

    ## ==============================================
    ## loadWarehouse
    ## ==============================================
    def loadWarehouse(self, w_id):
        logging.debug("LOAD - %s: %d / %d" % (constants.TABLENAME_WAREHOUSE, w_id, len(self.w_ids)))

        try:
            runDate = os.environ["RUN_DATE"]
        except:
            print ("Error parsing run date")

        startDate = self.computeStartDate(runDate) # runDate - 7 years
        endDate = self.computeEndDate(runDate)     # runDate - 1 day
        startOrderDate = startDate
        endOrderDate = endDate - timedelta(days=151)
        startOrderLineDayRange = 2
        endOrderLineDayRange = 151
        cum_h_amount_per_warehouse = 0

        ## WAREHOUSE
        w_tuples = [ self.generateWarehouse(w_id) ]
        self.handle.loadTuples(constants.TABLENAME_WAREHOUSE, w_tuples)

        ## DISTRICT
        d_tuples = [ ]
        w_name = str(w_tuples[0][1])
        prefix_arr = re.split(' |, |-', w_name)
        # District Prefix made of first characters of first and last tokens of w_name
        district_prefix = prefix_arr[0][0] + prefix_arr[len(prefix_arr) - 1][0]
        
        for d_id in range(1, self.scaleParameters.districtsPerWarehouse+1):
            cum_h_amount_per_district = 0
            d_next_o_id = self.scaleParameters.customersPerDistrict + 1
            d_tuples = [ self.generateDistrict(w_id, d_id, d_next_o_id, district_prefix) ]

            c_tuples = [ ]
            h_tuples = [ ]

            ## Select 10% of the customers to have bad credit
            selectedRows = rand.selectUniqueIds(self.scaleParameters.customersPerDistrict // 10, 1, self.scaleParameters.customersPerDistrict)

            ## TPC-C 4.3.3.1. says that o_c_id should be a permutation of [1, 3000]. But since it
            ## is a c_id field, it seems to make sense to have it be a permutation of the
            ## customers. For the "real" thing this will be equivalent
            cIdPermutation = [ ]

            for c_id in range(1, self.scaleParameters.customersPerDistrict+1):
                badCredit = (c_id in selectedRows)
                orderDate = self.computeRandomRangeDate(startOrderDate, endOrderDate)
                c_tuples.append(self.generateCustomer(w_id, d_id, c_id, orderDate, badCredit, True))
                h_tuples.append(self.generateHistory(w_id, d_id, c_id, orderDate))
                cIdPermutation.append(c_id)
                ## h_amount
                cum_h_amount_per_district += h_tuples[c_id-1][6]
                cum_h_amount_per_warehouse += h_tuples[c_id-1][6]
            ## FOR
            #d_ytd
            d_tuples[0][9] = cum_h_amount_per_district
            assert cIdPermutation[0] == 1
            assert cIdPermutation[self.scaleParameters.customersPerDistrict - 1] == self.scaleParameters.customersPerDistrict
            shuffle(cIdPermutation)

            o_tuples = [ ]
            no_tuples = [ ]

            for o_id in range(1, self.scaleParameters.customersPerDistrict+1):
                o_ol_cnt = rand.number(constants.MIN_OL_CNT, constants.MAX_OL_CNT)

                ## The last newOrdersPerDistrict are new orders
                newOrder = ((self.scaleParameters.customersPerDistrict - self.scaleParameters.newOrdersPerDistrict) < o_id)
                # use c_since as orderDate
                orderDate = c_tuples[cIdPermutation[o_id-1]-1][12]
                orderTime = self.computeRandomRangeTime(orderDate)
                o_tuple = self.generateOrder(w_id, d_id, o_id, cIdPermutation[o_id - 1], o_ol_cnt, orderTime, newOrder)
                total_ol_amount = 0
                ## Generate each OrderLine for the order
                ol_tuples = [ ]
                for ol_number in range(0, o_ol_cnt):
                    startOrderLineDate = orderDate + timedelta(days=startOrderLineDayRange)
                    endOrderLineDate = orderDate + timedelta(days=endOrderLineDayRange)
                    orderLineDate = self.computeRandomRangeDate(startOrderLineDate, endOrderLineDate)
                    orderLineTime = self.computeRandomRangeTime(orderLineDate)
                    ol_tuple = self.generateOrderLine(w_id, d_id, o_id, ol_number, self.scaleParameters.items, orderLineTime, newOrder)
                    ol_tuples.append(ol_tuple)
                    #ol_amount
                    total_ol_amount += ol_tuple[5]
                ## FOR
                o_tuple.append(ol_tuples)
                o_tuples.append(o_tuple)
                h_amount = h_tuples[cIdPermutation[o_id-1]-1][6]
                if not newOrder:
                    c_tuples[cIdPermutation[o_id-1]-1][16] = total_ol_amount - h_amount
                    c_tuples[cIdPermutation[o_id-1]-1][17] = h_amount
                ## This is a new order: make one for it
                if newOrder: no_tuples.append([o_id, d_id, w_id])
            ## FOR
            self.handle.loadTuples(constants.TABLENAME_DISTRICT, d_tuples)
            self.handle.loadTuples(constants.TABLENAME_CUSTOMER, c_tuples)
            self.handle.loadTuples(constants.TABLENAME_ORDERS, o_tuples)
#            self.handle.loadTuples(constants.TABLENAME_ORDERLINE, ol_tuples)
            self.handle.loadTuples(constants.TABLENAME_NEWORDER, no_tuples)
            self.handle.loadTuples(constants.TABLENAME_HISTORY, h_tuples)
#            self.handle.loadFinishDistrict(w_id, d_id)
        ## FOR
        #w_ytd
        w_tuples[0][8] = cum_h_amount_per_warehouse
        ## Select 10% of the stock to be marked "original"
        s_tuples = [ ]
        selectedRows = rand.selectUniqueIds(self.scaleParameters.items // 10, 1, self.scaleParameters.items)
        total_tuples = 0
        for i_id in range(1, self.scaleParameters.items+1):
            original = (i_id in selectedRows)
            s_tuples.append(self.generateStock(w_id, i_id, original))
            if len(s_tuples) >= self.batch_size:
                logging.debug("LOAD - %s [W_ID=%d]: %5d / %d" % (constants.TABLENAME_STOCK, w_id, total_tuples, self.scaleParameters.items))
                self.handle.loadTuples(constants.TABLENAME_STOCK, s_tuples)
                s_tuples = [ ]
            total_tuples += 1
        ## FOR
        if len(s_tuples) > 0:
            logging.debug("LOAD - %s [W_ID=%d]: %5d / %d" % (constants.TABLENAME_STOCK, w_id, total_tuples, self.scaleParameters.items))
            self.handle.loadTuples(constants.TABLENAME_STOCK, s_tuples)
    ## DEF

    ## ==============================================
    ## loadSupplier
    ## ==============================================
    def loadSupplier(self):
        ## Load all of the suppliers
        nkeyarr = []
        nkeyarr = [0 for i in range(constants.NUM_SUPPLIERS+1)]
        tuples = [ ]
        total_tuples = 0
        suppRecommendsCommentTuples = sample(list(range(1, constants.NUM_SUPPLIERS+1)), 5)
        suppComplaintsCommentTuples = sample(list(set(range(1, constants.NUM_SUPPLIERS+1)) - set(suppRecommendsCommentTuples)), 5)
        for i in range(1, constants.NUM_SUPPLIERS+1):
            tuples.append(self.generateSupplier(i, suppRecommendsCommentTuples, suppComplaintsCommentTuples, nkeyarr))
            total_tuples += 1
            if len(tuples) == self.batch_size:
                logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_SUPPLIER, total_tuples, constants.NUM_SUPPLIERS));
                self.handle.loadTuples(constants.TABLENAME_SUPPLIER, tuples)
                tuples = [ ]
        ## FOR
        if len(tuples) > 0:
            logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_SUPPLIER, total_tuples, constants.NUM_SUPPLIERS));
            self.handle.loadTuples(constants.TABLENAME_SUPPLIER, tuples)
    ## DEF

    ## ==============================================
    ## loadNation
    ## ==============================================
    def loadNation(self):
        ## Load all of the nations
        tuples = [ ]
        total_tuples = 0
        for i in range(0, constants.NUM_NATIONS):
            tuples.append(self.generateNation(i))
            total_tuples += 1
            if len(tuples) == self.batch_size:
                logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_NATION, total_tuples, constants.NUM_NATIONS));
                self.handle.loadTuples(constants.TABLENAME_NATION, tuples)
                tuples = [ ]
        ## FOR
        if len(tuples) > 0:
            logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_NATION, total_tuples, constants.NUM_NATIONS));
            self.handle.loadTuples(constants.TABLENAME_NATION, tuples)
    ## DEF

    ## ==============================================
    ## loadRegion
    ## ==============================================
    def loadRegion(self):
        ## Load all of the regions
        tuples = [ ]
        total_tuples = 0
        for i in range(0, constants.NUM_REGIONS):
            tuples.append(self.generateRegion(i))
            total_tuples += 1
            if len(tuples) == self.batch_size:
                logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_REGION, total_tuples, constants.NUM_REGIONS));
                self.handle.loadTuples(constants.TABLENAME_REGION, tuples)
                tuples = [ ]
        ## FOR
        if len(tuples) > 0:
            logging.debug("LOAD - %s: %5d / %d" % (constants.TABLENAME_REGION, total_tuples, constants.NUM_REGIONS));
            self.handle.loadTuples(constants.TABLENAME_REGION, tuples)
    ## DEF

    ## ==============================================
    ## generateItem
    ## ==============================================
    def generateItem(self, id, original):
        i_id = id
        i_im_id = rand.number(constants.MIN_IM, constants.MAX_IM)
        
        # i_name = rand.astring(constants.MIN_I_NAME, constants.MAX_I_NAME)
        # Product_info (item_name, item_description, item_brand) --> Sample product data
        product_info = products[randint(0, len(products) - 1)]
        product_array = re.split(r',+', product_info)
        i_name = product_array[0]
        i_name = i_name[:constants.MAX_I_NAME] if len(i_name) > constants.MAX_I_NAME else i_name
        i_price = rand.fixedPoint(constants.MONEY_DECIMALS, constants.MIN_PRICE, constants.MAX_PRICE)
        
        # i_data = rand.astring(constants.MIN_I_DATA, constants.MAX_I_DATA)
        # Item data contains brand information (if any) and the product description
        i_data = 'Brand: ' + product_array[2] + '\n' if len(product_array) > 2 else ''
        i_data += 'Description: ' + product_array[1] + '\n'
        # truncate i_data to maximum length
        if len(i_data) > constants.MAX_I_DATA:
            if original:
                i_data = i_data[:constants.MAX_I_DATA - 2 - len(constants.ORIGINAL_STRING)] + '..'
            else:
                i_data = i_data[:constants.MAX_I_DATA - 2] + '..'
        if original: i_data = self.fillOriginal(i_data)

        return [i_id, i_im_id, i_name, i_price, i_data]
    ## DEF

    ## ==============================================
    ## generateWarehouse
    ## ==============================================
    def generateWarehouse(self, w_id):
        percentileNum = intRange(0, 99)
        address = random.choice(popPercentiles[percentileNum])
        addr_array = re.split(r'\t+', address)

        w_tax = self.generateTax()
        w_ytd = constants.INITIAL_W_YTD

        # w_address = self.generateAddress()
        w_name = str(fake.company())
        w_city = addr_array[1]
        w_state = addr_array[2]
        w_zip = addr_array[0]
        w_street_1 = str(fake.street_address())
        w_street_2 = str(fake.secondary_address())
        
        return [w_id, w_name, w_street_1, w_street_2, w_city, w_state, w_zip, w_tax, w_ytd]
    ## DEF

    ## ==============================================
    ## generateDistrict
    ## ==============================================
    def generateDistrict(self, d_w_id, d_id, d_next_o_id, districtPrefix):
        percentileNum = intRange(0, 99)
        address = random.choice(popPercentiles[percentileNum])
        addr_array = re.split(r'\t+', address)

        d_tax = self.generateTax()
        d_ytd = constants.INITIAL_D_YTD

        # d_address = self.generateAddress()
        # District name contains prefix from w_name and suffix from d_id
        # (Not a standard one, but no district name dataset was availvale) 
        d_name = districtPrefix + '_district_' + str(d_id)
        d_city = addr_array[1]
        d_state = addr_array[2]
        d_zip = addr_array[0]
        d_street_1 = str(fake.street_address())
        d_street_2 = str(fake.secondary_address())

        return [d_id, d_w_id, d_name, d_street_1, d_street_2, \
                d_city, d_state, d_zip, d_tax, d_ytd, d_next_o_id]
    ## DEF

    ## ==============================================
    ## generateCustomer
    ## ==============================================
    def generateCustomer(self, c_w_id, c_d_id, c_id, sinceDate, badCredit, doesReplicateName):
        # We want to distribute pretty evenly across all our zip population percentile files
        percentileStr = "0" + str(intRange(0,99))
        percentileNum = int(percentileStr[-2:])

        # We're 50/50 male/female
        isMale = intRange(0,1)
        if (isMale):
            c_first = str(fake.first_name_male())
        else:
            c_first = str(fake.first_name_female())
        # One out of 100 people has no middle name...
        hasMiddleName = intRange(0,99)
        if (hasMiddleName):
            #...and sometimes someone slips in a blank, too
            c_middle = random.choice(' ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        else:
            c_middle = None
        
        assert 1 <= c_id and c_id <= constants.CUSTOMERS_PER_DISTRICT
        if c_id <= 1000:
            c_last = rand.makeLastName(c_id - 1)
        else:
            c_last = rand.makeRandomLastName(constants.CUSTOMERS_PER_DISTRICT)

        c_phone = str(fake.phone_number())
        c_since = sinceDate
        c_credit = constants.BAD_CREDIT if badCredit else constants.GOOD_CREDIT
        c_credit_lim = constants.INITIAL_CREDIT_LIM
        c_discount = rand.fixedPoint(constants.DISCOUNT_DECIMALS, constants.MIN_DISCOUNT, constants.MAX_DISCOUNT)
        c_balance = constants.INITIAL_BALANCE
        c_ytd_payment = constants.INITIAL_YTD_PAYMENT
        c_payment_cnt = constants.INITIAL_PAYMENT_CNT
        c_delivery_cnt = constants.INITIAL_DELIVERY_CNT
        
        #c_data = rand.astring(constants.MIN_C_DATA, constants.MAX_C_DATA)
        # In a paragraph, customer data contains profile creation date, username.
        # It also contains job_title, company, email and website url of the customer.
        c_data = 'The customer profile is created on ' + str(c_since)
        c_data = c_data + ' and the username is ' + fake.user_name() + '.\n'
        if (isMale):
            c_data = c_data + 'He works as a ' + fake.job() + ' in ' + fake.company() + ".\n"
            c_data = c_data + 'His email is ' + fake.free_email() + ' and website is ' + fake.url()
        else:
            c_data = c_data + 'She works as a ' + fake.job() + ' in ' + fake.company() + ".\n"
            c_data = c_data + 'Her email is ' + fake.free_email() + ' and website is ' + fake.url()

        geoStr = random.choice(popPercentiles[percentileNum])
        geoArray = re.split(r'\t+', geoStr)
        c_city = geoArray[1]
        c_state = geoArray[2]
        c_zip = geoArray[0]
        zipLat = geoArray[3]
        zipLong = geoArray[4]
        c_street1 = str(fake.street_address())
        # One out of eight addresses are in multi-unit places
        hasUnitNumber = intRange(0,7)
        if (hasUnitNumber):
            c_street2 = "Unit " + str(fake.building_number())
        else:
            c_street2 = None

        #Current data model doesn't include lat/long information, but we might want to consider
        #adding it so we can do analysis on distance from warehouse/district.  Below a method:

        #Now were going to randomly assign a new lat/long with a .02 degree radius of
        #the zip lat/long.  At the equator, this would be a 2.2264km radius.  We
        #will adjust based on the latitude, so it will be a smaller circle of
        #different sizes througout the US.  See:
        #https://gis.stackexchange.com/questions/25877/generating-random-locations-nearby
        #u = random.random()
        #v = random.random()
        #w = 0.02 * math.sqrt(u)
        #t = 2 * math.pi * v
        #xFlatAdjustment = w * math.cos(t)
        #yAdjustment = w * math.sin(t)
        #xAdjustment = xFlatAdjustment / math.cos(float(zipLong))
        #userLat = float(zipLat) + xAdjustment
        #userLong = float(zipLong) + yAdjustment


        return [ c_id, c_d_id, c_w_id, c_first, c_middle, c_last, \
                c_street1, c_street2, c_city, c_state, c_zip, \
                c_phone, c_since, c_credit, c_credit_lim, c_discount, c_balance, \
                c_ytd_payment, c_payment_cnt, c_delivery_cnt, c_data ]
    ## DEF

    ## ==============================================
    ## generateOrder
    ## ==============================================
    def generateOrder(self, o_w_id, o_d_id, o_id, o_c_id, o_ol_cnt, orderTime, newOrder):
        """Returns the generated o_ol_cnt value."""
        o_entry_d = orderTime
        o_carrier_id = constants.NULL_CARRIER_ID if newOrder else rand.number(constants.MIN_CARRIER_ID, constants.MAX_CARRIER_ID)
        o_all_local = constants.INITIAL_ALL_LOCAL
        return [ o_id, o_c_id, o_d_id, o_w_id, o_entry_d, o_carrier_id, o_ol_cnt, o_all_local ]
    ## DEF

    ## ==============================================
    ## generateOrderLine
    ## ==============================================
    def generateOrderLine(self, ol_w_id, ol_d_id, ol_o_id, ol_number, max_items, orderLineTime, newOrder):
        ol_i_id = rand.number(1, max_items)
        ol_supply_w_id = ol_w_id
        ol_delivery_d = orderLineTime
        ol_quantity = rand.number(constants.MIN_OL_QUANTITY, constants.MAX_OL_QUANTITY)
        if newOrder == False:
            if ol_o_id % 5 == 0:
                ol_amount = rand.fixedPoint(constants.MONEY_DECIMALS, constants.MIN_AMOUNT, constants.MAX_PRICE * constants.MAX_OL_QUANTITY)
            else:
                ol_amount = 0.00
        else:
            ol_amount = rand.fixedPoint(constants.MONEY_DECIMALS, constants.MIN_AMOUNT, constants.MAX_PRICE * constants.MAX_OL_QUANTITY)
            ol_delivery_d = None
        ol_dist_info = rand.astring(constants.DIST, constants.DIST)

        return [ ol_number, ol_i_id, ol_supply_w_id, ol_delivery_d, ol_quantity, ol_amount, ol_dist_info ]
    ## DEF

    ## ==============================================
    ## generateStock
    ## ==============================================
    def generateStock(self, s_w_id, s_i_id, original):
        s_quantity = rand.number(constants.MIN_QUANTITY, constants.MAX_QUANTITY);
        s_ytd = 0;
        s_order_cnt = rand.number(constants.DISTRICTS_PER_WAREHOUSE, constants.INITIAL_ORDERS_PER_DISTRICT);
        if len(self.w_ids) == 1:
            s_remote_cnt = 0
        else:
            s_remote_cnt = int(s_order_cnt * 0.1) # 10% of orders are remote

        # s_data = rand.astring(constants.MIN_I_DATA, constants.MAX_I_DATA)
        s_data = fake.text(max_nb_chars = constants.MAX_I_DATA)
        if original: 
            if len(s_data) > constants.MAX_I_DATA - len(constants.ORIGINAL_STRING):
                s_data = s_data[:constants.MAX_I_DATA - len(constants.ORIGINAL_STRING)]
            s_data = self.fillOriginal(s_data)

        s_dists = [ ]
        for i in range(0, constants.DISTRICTS_PER_WAREHOUSE):
            s_dists.append(rand.astring(constants.DIST, constants.DIST))

        return [ s_i_id, s_w_id, s_quantity ] + \
               s_dists + \
               [ s_ytd, s_order_cnt, s_remote_cnt, s_data ]
    ## DEF

    ## ==============================================
    ## generateHistory
    ## ==============================================
    def generateHistory(self, h_c_w_id, h_c_d_id, h_c_id, historyDate):
        h_w_id = h_c_w_id
        h_d_id = h_c_d_id
        h_date = historyDate
        h_amount = constants.INITIAL_AMOUNT
        
        # h_data = rand.astring(constants.MIN_DATA, constants.MAX_DATA)
        # Miscellaneous information of history in one random sentence
        h_data = str(fake.text(max_nb_chars = constants.MAX_DATA))
        
        return [ h_c_id, h_c_d_id, h_c_w_id, h_d_id, h_w_id, h_date, h_amount, h_data ]
    ## DEF

    ## ==============================================
    ## generateSupplier
    ## ==============================================
    def generateSupplier(self, suppkey, recommendsCommentTuples, complaintsCommentTuples, nkeyarr):
        su_suppkey = suppkey
        su_name = "Supplier#" + str(suppkey).zfill(constants.NUM_LEADING_ZEROS)
        # su_address = self.generateSupplierAddress()
        su_address = str(fake.street_address() + ', ' + fake.country())
        su_nationkey = constants.NATIONS[rand.number(0, constants.NUM_NATIONS-1)][0]
        nkeyarr[su_nationkey] += 1
        while 1:
            if nkeyarr[su_nationkey] > 162:
                nkeyarr[su_nationkey] -= 1
                su_nationkey = constants.NATIONS[rand.number(0, constants.NUM_NATIONS-1)][0]
                nkeyarr[su_nationkey] += 1
            else:
                break
        # su_phone = rand.nstring(constants.PHONE, constants.PHONE)
        su_phone = str(fake.phone_number())
        su_acctbal = rand.fixedPoint(constants.MONEY_DECIMALS, constants.MIN_SUPPLIER_ACCTBAL, constants.MAX_SUPPLIER_ACCTBAL)
        if suppkey in recommendsCommentTuples:
            su_comment = rand.randomStringsWithEmbeddedSubstrings(constants.MIN_SUPPLIER_COMMENT, constants.MAX_SUPPLIER_COMMENT, "Customer", "Recommends")
        elif suppkey in complaintsCommentTuples:
            su_comment = rand.randomStringsWithEmbeddedSubstrings(constants.MIN_SUPPLIER_COMMENT, constants.MAX_SUPPLIER_COMMENT, "Customer", "Complaints")
        else:
            su_comment = rand.randomStringMinMax(constants.MIN_SUPPLIER_COMMENT, constants.MAX_SUPPLIER_COMMENT)

        return [ su_suppkey, su_name, su_address, su_nationkey, su_phone, su_acctbal, su_comment ]
    ## DEF

    ## ==============================================
    ## generateNation
    ## ==============================================
    def generateNation(self, nationkey):
        n_nationkey = constants.NATIONS[nationkey][0]
        n_name = constants.NATIONS[nationkey][1]
        n_regionkey = constants.NATIONS[nationkey][2]
        n_comment = rand.randomStringMinMax(constants.MIN_NATION_COMMENT, constants.MAX_NATION_COMMENT)

        return [ n_nationkey, n_name, n_regionkey, n_comment ]
    ## DEF

    ## ==============================================
    ## generateRegion
    ## ==============================================
    def generateRegion(self, regionkey):
        r_regionkey = regionkey
        r_name = constants.REGIONS[regionkey]
        r_comment = rand.randomStringMinMax(constants.MIN_REGION_COMMENT, constants.MAX_REGION_COMMENT)

        return [ r_regionkey, r_name, r_comment ]
    ## DEF

    ## ==============================================
    ## generateAddress
    ## ==============================================
    def generateAddress(self):
        """
            Returns a name and a street address
            Used by both generateWarehouse and generateDistrict.
        """
        name = rand.astring(constants.MIN_NAME, constants.MAX_NAME)
        return [ name ] + self.generateStreetAddress()
    ## DEF

    ## ==============================================
    ## generateStreetAddress
    ## ==============================================
    def generateStreetAddress(self):
        """
            Returns a list for a street address
            Used for warehouses, districts and customers.
        """
        street1 = rand.astring(constants.MIN_STREET, constants.MAX_STREET)
        street2 = rand.astring(constants.MIN_STREET, constants.MAX_STREET)
        city = rand.astring(constants.MIN_CITY, constants.MAX_CITY)
        state = rand.astring(constants.STATE, constants.STATE)
        zip = self.generateZip()

        return [ street1, street2, city, state, zip ]
    ## DEF

    ## ==============================================
    ## generateSupplierAddress
    ## ==============================================
    def generateSupplierAddress(self):
        """
            Returns address of supplier
        """
        address = rand.astring(constants.MIN_SUPPLIER_ADDRESS, constants.MAX_SUPPLIER_ADDRESS)
        return address
    ## DEF

    ## ==============================================
    ## generateTax
    ## ==============================================
    def generateTax(self):
        return rand.fixedPoint(constants.TAX_DECIMALS, constants.MIN_TAX, constants.MAX_TAX)
    ## DEF

    ## ==============================================
    ## generateZip
    ## ==============================================
    def generateZip(self):
        length = constants.ZIP_LENGTH - len(constants.ZIP_SUFFIX)
        return rand.nstring(length, length) + constants.ZIP_SUFFIX
    ## DEF

    ## ==============================================
    ## fillOriginal
    ## ==============================================
    def fillOriginal(self, data):
        """
            a string with ORIGINAL_STRING at a random position
        """
        originalLength = len(constants.ORIGINAL_STRING)
        position = rand.number(0, len(data) - originalLength)
        out = data[:position] + constants.ORIGINAL_STRING + data[position + originalLength:]
        assert len(out) == len(data)
        return out
    ## DEF
    def computeStartDate(self, runDate):
        startDateTime = datetime.strptime(runDate,  "%Y-%m-%d %H:%M:%S") - relativedelta(years=7)
        return startDateTime
    ## DEF

    def computeEndDate(self, runDate):
        endDateTime = datetime.strptime(runDate,  "%Y-%m-%d %H:%M:%S") - timedelta(days=1)
        return endDateTime
    ## DEF

    def computeRandomRangeDate(self, startDate, endDate):
         delta = endDate - startDate
         deltaSecs = (delta.days * self.numSecsPerDay) + delta.seconds
         randomTime = randrange(deltaSecs)
         return startDate + timedelta(seconds=randomTime)
    ## DEF

    def computeRandomRangeTime(self, dateObj):
         return dateObj.strftime("%Y-%m-%d %H:%M:%S")
    ## DEF

## CLASS
