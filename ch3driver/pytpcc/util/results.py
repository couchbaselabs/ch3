# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------
# Copyright (C) 2011
# Andy Pavlo
# http://www.cs.brown.edu/~pavlo/
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

from asyncore import loop
import logging
import time
import constants

class Results:
    
    def __init__(self, warmupDuration, warmupQueryIterations):
        self.start = None
        self.stop = None
        self.txn_id = 0
        self.warmupDuration = warmupDuration
        self.warmupQueryIterations = warmupQueryIterations
        self.txn_counters = { }
        self.txn_status = { }
        self.txn_times = { }
        self.running = { }
        self.query_times = []
        self.fts_query_times = []
        
    def startBenchmark(self):
        """Mark the benchmark as having been started"""
        assert self.start == None
        logging.debug("Starting benchmark statistics collection")
        self.start = time.time()
        return self.start
        
    def stopBenchmark(self):
        """Mark the benchmark as having been stopped"""
        assert self.start != None
        assert self.stop == None
        logging.debug("Stopping benchmark statistics collection")
        self.stop = time.time()
        
    def startTransaction(self, txn):
        self.txn_id += 1
        id = self.txn_id
        self.running[id] = (txn, time.time())
        return id
        
    def abortTransaction(self, id):
        """Abort a transaction and discard its times"""
        assert id in self.running
        txn_name, txn_start = self.running[id]
        del self.running[id]

        if self.warmupDuration != None and (txn_start >= self.start + self.warmupDuration):
            if txn_name not in self.txn_status :
                self.txn_status[txn_name] = {}

            status = "aborted"
            cnt = self.txn_status[txn_name].get(status, 0)
            self.txn_status[txn_name][status] = cnt + 1
        
    def stopTransaction(self, id, status):
        """Record that the benchmark completed an invocation of the given transaction"""
        assert id in self.running
        txn_name, txn_start = self.running[id]
        del self.running[id]

        if self.warmupDuration != None and (txn_start >= self.start + self.warmupDuration):
            duration = time.time() - txn_start
            total_time = self.txn_times.get(txn_name, 0)
            self.txn_times[txn_name] = total_time + duration

            total_cnt = self.txn_counters.get(txn_name, 0)
            self.txn_counters[txn_name] = total_cnt + 1

            if txn_name not in self.txn_status :
                self.txn_status[txn_name] = {}

            if status != "":
                cnt = self.txn_status[txn_name].get(status, 0)
                self.txn_status[txn_name][status] = cnt + 1

    def append(self, r):
        for txn_name in r.txn_counters.keys():
            orig_cnt = self.txn_counters.get(txn_name, 0)
            orig_time = self.txn_times.get(txn_name, 0)

            self.txn_counters[txn_name] = orig_cnt + r.txn_counters[txn_name]
            self.txn_times[txn_name] = orig_time + r.txn_times[txn_name]
            logging.debug("%s [cnt=%d, time=%d]" % (txn_name, self.txn_counters[txn_name], self.txn_times[txn_name]))
        for txn_name in r.txn_status.keys():
             if txn_name not in self.txn_status :
                  self.txn_status[txn_name] = {}
             for k in r.txn_status[txn_name].keys():
                 cnt = self.txn_status[txn_name].get(k, 0)
                 self.txn_status[txn_name][k] = cnt + r.txn_status[txn_name][k]

        if len(r.query_times) > 0:
            self.query_times.append(r.query_times)
        ## HACK
        self.start = r.start
        if len(r.query_times) == 0:
            self.stop = r.stop
        
        if len(r.fts_query_times) > 0:
            self.fts_query_times.append(r.fts_query_times)
        ## HACK
        self.start = r.start
        if len(r.fts_query_times) == 0:
            self.stop = r.stop
            
    def __str__(self):
        return self.show()
        
    def show(self, duration, queryIterations, numClients, numAClients, numFClients = 0, load_time = None):
        if self.start == None:
            return "Benchmark not started"
        if self.warmupDuration == None:
            warmupTime = 0
        else:
            warmupTime = self.warmupDuration
        if duration == None:
            if self.stop == None:
                res_duration = time.time() - self.start - warmupTime
            else:
                res_duration = self.stop - self.start - warmupTime
        else:
            res_duration = duration - warmupTime

        col_width = 15
        total_width = (col_width*6)
        f = "\n  " + (("%-" + str(col_width) + "s")*5)
        line = "-"*total_width

        ret = u"" + "="*total_width + "\n"
        if load_time != None:
            ret += "Data Loading Time: %d seconds\n\n" % (load_time)

        if duration != None:
            if warmupTime == 0:
                if duration == 1:
                    ret += "\n\n\nTransaction Execution Results after %d second\n%s" % (duration, line)
                else:
                    ret += "\n\n\nTransaction Execution Results after %d seconds\n%s" % (duration, line)
            else:
                if duration == 1:
                    ret += "\n\n\nTransaction Execution Results after %d second with warmup of %d seconds \n%s" % (duration, warmupTime, line)
                else:
                    ret += "\n\n\nTransaction Execution Results after %d seconds with warmup of %d seconds\n%s" % (duration, warmupTime, line)
 
        else:
            if self.warmupQueryIterations == None: 
                if queryIterations == 1:
                    ret += "\n\n\nTransaction Execution Results after %d query iteration\n%s" % (queryIterations, line)
                else:
                    ret += "\n\n\nTransaction Execution Results after %d query iterations\n%s" % (queryIterations, line)
            else:
                if queryIterations == 1:
                    ret += "\n\n\nTransaction Execution Results after %d query iteration with %d warmup query iteration\n%s" % (queryIterations, self.warmupQueryIterations, line)
                else:
                    ret += "\n\n\nTransaction Execution Results after %d query iterations with %d warmup query iterations\n%s" % (queryIterations, self.warmupQueryIterations, line)
        # ret += f % ("", "Executed", u"Time (µs)", "Rate")
        ret += f % ("", "Executed", u"Time (ms)", "Avg. Time (ms)", "Rate")
        total_txn_time = 0
        total_txn_cnt = 0
        total_avg_time = 0
        for txn in sorted(self.txn_counters.keys()):
            if txn == constants.QueryTypes.CH2 or txn == constants.QueryTypes.FTS:
                continue
            txn_time = self.txn_times[txn]
            txn_cnt = self.txn_counters[txn]
            txn_rate = u" %.02f txn/s" % ((txn_cnt / res_duration))
            #avg_latency = u"%.03f sec" % ((txn_cnt / txn_time))
            avg_time = round((txn_time * 1000 / txn_cnt), 2)
            ret += f % (txn, str(txn_cnt), str(round(txn_time * 1000,3)), avg_time, txn_rate)
            total_txn_time += txn_time
            total_txn_cnt += txn_cnt
            total_avg_time += avg_time
            ret += "("
            i = 0
            for k in sorted(self.txn_status[txn].keys()):
                if txn == constants.QueryTypes.CH2 or txn == constants.QueryTypes.FTS:
                    continue
                if i != 0 :
                   ret += ", "
                i += 1
                ret += k + ":"+ str(self.txn_status[txn][k])
            ret += ")"
        ret += "\n" + ("-"*total_width)
        total_rate = " %.02f txn/s" % ((total_txn_cnt / res_duration))
        ret += f % ("TOTAL", str(total_txn_cnt), str(round(total_txn_time * 1000,3)), round(total_avg_time, 2), total_rate)
        
        ret = self.print_analytics_stats(ret, duration, queryIterations, warmupTime, numClients, numAClients)
        ret = self.print_fts_stats(ret, duration, queryIterations, warmupTime, numClients, numFClients)

        return (ret)
    
    ## ================================================================
    ## print_fts_stats
    ## ================================================================
    def print_fts_stats(self, ret, duration, queryIterations, warmupTime, numClients, numFClients):
        col_width = 20
        total_width = (col_width*5)+5
        f = "\n  " + (("%-" + str(col_width) + "s")*5)
        line = "-"*total_width
        if duration != None:
            if warmupTime == 0:
                if duration == 1:
                    ret += "\n\n\nFTS Execution Results after %d second\n%s" % (duration, line)
                else:
                    ret += "\n\n\nFTS Execution Results after %d seconds\n%s" % (duration, line)
            else:
                if duration == 1:
                    ret += "\n\n\nFTS Execution Results after %d second with warmup of %d seconds \n%s" % (duration, warmupTime, line)
                else:
                    ret += "\n\n\nFTS Execution Results after %d seconds with warmup of %d seconds\n%s" % (duration, warmupTime, line)
        else:
            if queryIterations == 1:
                ret += "\n\n\nFTS Execution Results after %d query iteration and %d FTS clients\n%s" % (queryIterations, numFClients, line)
            else:
                ret += "\n\n\nFTS Execution Results after %d query iterations and %d FTS clients\n%s" % (queryIterations, numFClients, line)

        overall_avg_fts_resp_time = {"FQ01": [0, 0], "FQ02": [0, 0], "FQ03": [0, 0], "FQ04": [0, 0], 
                                     "FQ05": [0, 0], "FQ06": [0, 0], "FQ07": [0, 0], "FQ08": [0, 0],
                                     "FQ09": [0, 0], "FQ10": [0, 0], "FQ11": [0, 0], "FQ12": [0, 0],
                                     "FQ13": [0, 0], "FQ14": [0, 0], "FQ15": [0, 0], "FQ16": [0, 0],
                                     "FQ17": [0, 0], "FQ18": [0, 0], "FQ19": [0, 0], "FQ20": [0, 0]}

        #HACK
        if numClients == 1:
            # Make self.query_times an array of arrays to keep the show() code consistent
            tmp = []
            tmp.append(self.fts_query_times)
            self.fts_query_times = tmp

        fts_stats_loop = [] #------ list to store summary of all clients, each element corresponds to each loop
        for qry_times in self.fts_query_times: # fts_query_times is a list, each element corresponds to one client
            iter = 0
            for qry_dict in qry_times: # each dict corresponds to one loop of query execution
                fts_stats_dict = {} #------- dict to store summary per loop over all clents
                for qry in qry_dict:
                    total_exec_time = 0
                    for exec_time in qry_dict[qry]: # qry_dict[qry] is a list of executions per FTS queries
                        total_exec_time += exec_time[2]
                    stas_per_qry = [qry, iter + 1, len(qry_dict[qry]), total_exec_time]
                    fts_stats_dict[qry] = stas_per_qry

                    if iter + 1 <= len(fts_stats_loop):
                        fts_stats_loop[iter][qry][2] += fts_stats_dict[qry][2]
                        fts_stats_loop[iter][qry][3] += fts_stats_dict[qry][3]
                if iter + 1 > len(fts_stats_loop):
                    fts_stats_loop.append(fts_stats_dict)
                iter += 1
        
        iter = 0
        for loop_stats in fts_stats_loop:
            total_execs_per_loop = 0
            total_exec_time_per_loop = 0
            total_avg_time = 0
            geo_mean = 1
            
            iter += 1
            ret += f % ("Query", "Loop", "Executed", u"Total Time (ms)", u"Avg. Elapsed Time (ms)")
            for qry in loop_stats:
                total_execs_per_loop += loop_stats[qry][2]
                total_exec_time_per_loop += loop_stats[qry][3] 
                avg_time = round(loop_stats[qry][3]/loop_stats[qry][2], 2)
                total_avg_time += avg_time
                geo_mean *= avg_time
                ret += f % (qry, loop_stats[qry][1], loop_stats[qry][2], round(loop_stats[qry][3], 2), avg_time)
                overall_avg_fts_resp_time[qry][0] += round(avg_time, 2)
                overall_avg_fts_resp_time[qry][1] += 1
            
            total_queries = len(loop_stats)
            ret += "\n" + ("-"*total_width)
            ret += f % ("TOTAL (Loop " + str(iter) + ")", "", total_execs_per_loop, str(round(total_exec_time_per_loop, 2)), str(round(total_avg_time, 2)))
            ret += "\n" + ("-"*col_width) + "\nOn Average:"
            ret += "\t" + ("QUERIES RUN = %d \t TOTAL TIME = %.02f \t GEOMETRIC MEAN = %.02f \t  ARITHMETIC MEAN = %.02f" %(total_queries, round(total_avg_time, 2), round(geo_mean**(1./total_queries), 2), round(total_avg_time/total_queries, 2)))
            ret += "\n" + ("-"*col_width)
            ret += '\n\n'
        
        overall_geo_mean = 1
        overall_num_queries = 0
        sum_avg_fts_resp_time = 0
        simple_geo_mean, adv_geo_mean, na_geo_mean = 1, 1, 1
        simple_resp_time, adv_resp_time, na_resp_time = 0, 0, 0
        num_simple_qry, num_adv_qry, num_na_query = 0, 0, 0
        for query in overall_avg_fts_resp_time:
            if overall_avg_fts_resp_time[query][1] > 0:
                overall_num_queries += 1
                overall_avg_fts_resp_time[query][0] /= overall_avg_fts_resp_time[query][1]
                overall_geo_mean *= overall_avg_fts_resp_time[query][0]
                sum_avg_fts_resp_time += overall_avg_fts_resp_time[query][0]

                if overall_num_queries <= 6: ## 6 simple FTS queries
                    num_simple_qry += 1
                    simple_resp_time += overall_avg_fts_resp_time[query][0]
                    simple_geo_mean *= overall_avg_fts_resp_time[query][0]
                elif overall_num_queries <= 6 + 8:  ## 8 advanced FTS queries
                    num_adv_qry += 1
                    adv_resp_time += overall_avg_fts_resp_time[query][0]
                    adv_geo_mean *= overall_avg_fts_resp_time[query][0]
                else:    ## 6 non-analytical FTS queries
                    num_na_query += 1
                    na_resp_time += overall_avg_fts_resp_time[query][0]
                    na_geo_mean *= overall_avg_fts_resp_time[query][0]

        if sum_avg_fts_resp_time == 0:
            return(ret)
        
        col_width = 25
        total_width = (col_width*2)+10
        f = "\n  " + (("%-" + str(col_width) + "s")*2)
        line = "-"*total_width
        ret += "\n" + ("OVERALL RESULTS FOR COMPLETED FTS QUERY SETS")
        ret += "\n" + ("-"*total_width)
        ret += f % ("Query", u"Average Response Time (ms)")
        ret += "\n" + ("-"*total_width)
        for query in overall_avg_fts_resp_time:
            if overall_avg_fts_resp_time[query][1] > 0:
                ret += f % (query, round(overall_avg_fts_resp_time[query][0], 2))
        ret += "\n" + ("-"*total_width)
        ret += "\n" + ("OVERALL FTS GEOMETRIC MEAN = %.02f" %(round(overall_geo_mean**(1./overall_num_queries), 2)))
        ret += "\n" + ("AVERAGE TIME PER FTS QUERY SET = %.02f" %(round(sum_avg_fts_resp_time, 2)))
        ret += "\n" + ("FTS QUERIES PER HOUR (Qph) = %.02f" %(round(overall_num_queries * 3600 * 1000/sum_avg_fts_resp_time*numFClients, 2)))
        
        ret += "\n\n" + ("-"*col_width*2)
        ret += "\n" + ("GEOMETRIC MEAN (Simple: FQ01-FQ06) = %.02f" %(round(simple_geo_mean**(1./num_simple_qry), 2)))
        ret += "\n" + ("AVERAGE TIME PER QUERY SET (simple) = %.02f" %(round(simple_resp_time, 2)))
        ret += "\n" + ("QUERIES PER HOUR (Qph) = %.02f" %(round(num_simple_qry * 3600 * 1000/simple_resp_time*numFClients, 2)))
        ret += "\n" + ("-"*col_width*2)
        ret += "\n" + ("GEOMETRIC MEAN (Advanced: FQ07-FQ14) = %.02f" %(round(adv_geo_mean**(1./num_adv_qry), 2)))
        ret += "\n" + ("AVERAGE TIME PER QUERY SET (advanced) = %.02f" %(round(adv_resp_time, 2)))
        ret += "\n" + ("QUERIES PER HOUR (Qph) = %.02f" %(round(num_adv_qry * 3600 * 1000/adv_resp_time*numFClients, 2)))
        ret += "\n" + ("-"*col_width*2)
        ret += "\n" + ("GEOMETRIC MEAN (NA: FQ15-FQ20) = %.02f" %(round(na_geo_mean**(1./num_na_query), 2)))
        ret += "\n" + ("AVERAGE TIME PER QUERY SET (non-analytics) = %.02f" %(round(na_resp_time, 2)))
        ret += "\n" + ("QUERIES PER HOUR (Qph) = %.02f" %(round(num_na_query * 3600 * 1000/na_resp_time*numFClients, 2)))
        ret += "\n" + ("-"*col_width*2) + "\n"

        ret += "\n" + ("-"*total_width)
        return ret

    ## ================================================================
    ## print_analytics_stats
    ## ================================================================
    def print_analytics_stats(self, ret, duration, queryIterations, warmupTime, numClients, numAClients):
        col_width = 13
        total_width = (col_width*6)+5
        f = "\n  " + (("%-" + str(col_width) + "s")*6)
        line = "-"*total_width
        if duration != None:
            if warmupTime == 0:
                if duration == 1:
                    ret += "\n\n\nAnalytics Execution Results after %d second\n%s" % (duration, line)
                else:
                    ret += "\n\n\nAnalytics Execution Results after %d seconds\n%s" % (duration, line)
            else:
                if duration == 1:
                    ret += "\n\n\nAnalytics Execution Results after %d second with warmup of %d seconds \n%s" % (duration, warmupTime, line)
                else:
                    ret += "\n\n\nAnalytics Execution Results after %d seconds with warmup of %d seconds\n%s" % (duration, warmupTime, line)
        else:
            if self.warmupQueryIterations == None: 
                if queryIterations == 1:
                    ret += "\n\n\nAnalytics Execution Results after %d query iteration\n%s" % (queryIterations, line)
                else:
                    ret += "\n\n\nAnalytics Execution Results after %d query iterations\n%s" % (queryIterations, line)
            else:
                if queryIterations == 1:
                    ret += "\n\n\nAnalytics Execution Results after %d query iteration with %d warmup query iteration\n%s" % (queryIterations, self.warmupQueryIterations, line)
                else:
                    ret += "\n\n\nAnalytics Execution Results after %d query iterations with %d warmup query iterations\n%s" % (queryIterations, self.warmupQueryIterations, line)

        total_analytics_time = 0
        total_analytics_cnt = 0
        overall_avg_resp_time = {"Q01": [0, 0], "Q02": [0, 0], "Q03": [0, 0], "Q04": [0, 0], "Q05": [0, 0], "Q06": [0, 0],
                                 "Q07": [0, 0], "Q08": [0, 0], "Q09": [0, 0], "Q10": [0, 0], "Q11": [0, 0], "Q12": [0, 0],
                                 "Q13": [0, 0], "Q14": [0, 0], "Q15": [0, 0], "Q16": [0, 0], "Q17": [0, 0], "Q18": [0, 0],
                                 "Q19": [0, 0], "Q20": [0, 0], "Q21": [0, 0], "Q22": [0, 0]}

        #HACK
        if numClients == 1:
            # Make self.query_times an array of arrays to keep the show() code consistent
            tmp = []
            tmp.append(self.query_times)
            self.query_times = tmp

#        print(self.query_times) #self.query_times is an array of arrays, one element for each client

        for qry_times in self.query_times: #qry_times is an array element, each element corresponds to one client
            ret += f % ("Client", "Query", "Loop", "Start Time", "End Time", u"Elapsed Time (s)")
            partialLoop = False
            loopNum = 0
            for qry_dict in qry_times: # each dict corresponds to one loop of query execution
                loopNum += 1
                if loopNum <= self.warmupQueryIterations:
                    continue
                geo_mean = 1
                total_time = 0
                numQueriesPerIteration = len(qry_dict)
                if numQueriesPerIteration < constants.NUM_CH2_QUERIES:
                    partialLoop = True
                    logging.debug("Partial Loop")

                for qry in qry_dict: # individual query
                    if qry_dict[qry][3][-2:] == "ms":
                        q_time = float(qry_dict[qry][3][:-2])/1000
                    elif qry_dict[qry][3][-1:] == "s":
                        q_time = float(qry_dict[qry][3][:-1])
                    if not partialLoop:
                        overall_avg_resp_time[qry][0] += round(q_time, 2)
                        overall_avg_resp_time[qry][1] += 1
                    ret += f % (qry_dict[qry][0], qry, qry_dict[qry][1], qry_dict[qry][2], qry_dict[qry][4], round(q_time, 2))
                    geo_mean *= q_time
                    total_time += q_time

                ret += "\n" + ("-"*total_width)
                if numQueriesPerIteration == 0:
                    ret += "\n" + ("QUERIES RUN = %d" %(numQueriesPerIteration))
                else:
                    ret += "\n" + ("QUERIES RUN = %d TOTAL TIME = %.02f GEOMETRIC MEAN = %.02f  ARITHMETIC MEAN = %.02f" %(numQueriesPerIteration, round(total_time, 2), round(geo_mean**(1./numQueriesPerIteration), 2), round(total_time/numQueriesPerIteration, 2)))
                
                ret += "\n"
                ret += "\n"

        if len(self.query_times) == 0:
            return(ret)
        
        overall_geo_mean = 1
        overall_num_queries = 0
        sum_avg_resp_time = 0
        for query in overall_avg_resp_time:
            if overall_avg_resp_time[query][1] > 0:
                overall_num_queries += 1
                overall_avg_resp_time[query][0] /= overall_avg_resp_time[query][1]
                overall_geo_mean *= overall_avg_resp_time[query][0]
                sum_avg_resp_time += overall_avg_resp_time[query][0]

        if sum_avg_resp_time == 0:
            return(ret)
        
        col_width = 25
        total_width = (col_width*2)+2
        f = "\n  " + (("%-" + str(col_width) + "s")*2)
        line = "-"*total_width
        ret += "\n" + ("OVERALL RESULTS FOR COMPLETED QUERY SETS")
        ret += "\n" + ("-"*total_width)
        ret += f % ("Query", u"Average Response Time (s)")
        ret += "\n" + ("-"*total_width)
        for query in overall_avg_resp_time:
            if overall_avg_resp_time[query][1] > 0:
                ret += f % (query, round(overall_avg_resp_time[query][0], 2))
        ret += "\n" + ("-"*total_width)
        ret += "\n" + ("OVERALL ANALYTICS GEOMETRIC MEAN = %.02f" %(round(overall_geo_mean**(1./overall_num_queries), 2)))
        ret += "\n" + ("AVERAGE TIME PER ANALYTICS QUERY SET = %.02f" %(round(sum_avg_resp_time, 2)))
        ret += "\n" + ("ANAYTICS QUERIES PER HOUR (Qph) = %.02f" %(round(overall_num_queries * 3600/sum_avg_resp_time*numAClients, 2)))
        
        ret += "\n" + ("-"*total_width)

        return ret
## CLASS
