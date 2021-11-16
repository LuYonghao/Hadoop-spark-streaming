from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
import sys
import os

conf = SparkConf()
conf.setAppName("TwitterStreamApp")
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
ssc = StreamingContext(sc, 5)
ssc.checkpoint("checkpoint_TwitterApp")
dataStream = ssc.socketTextStream("twitter", 9009)

words = dataStream.flatMap(lambda line: line.split(" "))

my_filter = ["#MasterChef", "#SOSCuba", "#SalveSeQuemPuder", "#COVID19", "#SkilledTrade"]
# my_filter = ['#Trump', '#GOP', '#Russia', '#ImpeachmentHearing', '#USA']
hashtags = words.filter(lambda w: w in my_filter)
hashtag_counts = hashtags.map(lambda x: (x, 1))


# add count to last count
def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)


hashtag_totals = hashtag_counts.updateStateByKey(aggregate_tags_count)

if os.path.exists('graph_data.txt'):
    os.remove('graph_data.txt')
# graph_data = open('graph_data.txt', 'a+')
graph_data = open('graph_data.txt', 'w+')
output = open('A_out.txt', 'a+')


# process a single time interval
def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))
    output.write("----------- %s -----------\n" % str(time))
    try:
        sorted_rdd = rdd.sortBy(lambda x: x[1], True)
        top10 = sorted_rdd.take(10)

        for tag in top10:
            graph_data.write('{:<40} {}\n'.format(tag[0], tag[1]))
            output.write('{:<40} {}\n'.format(tag[0], tag[1]))
            print('{:<40} {}'.format(tag[0], tag[1]))
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


hashtag_totals.foreachRDD(process_interval)

ssc.start()
ssc.awaitTermination()

graph_data.close()
output.close()
