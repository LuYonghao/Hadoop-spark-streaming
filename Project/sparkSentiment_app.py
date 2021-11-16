"""
    This Spark app connects to a script running on another (Docker) machine
    on port 9009 that provides a stream of raw tweets text. That stream is
    meant to be read and processed here, where top trending hashtags are
    identified. Both apps are designed to be run in Docker containers.

    To execute this in a Docker container, do:

        docker run -it -v $PWD:/app --link twitter:twitter eecsyorku/eecs4415

    and inside the docker:

        spark-submit spark_app.py

    For more instructions on how to run, refer to final tutorial 8 slides.

    Made for: EECS 4415 - Big Data Systems (York University EECS dept.)
    Modified by: Tilemachos Pechlivanoglou
    Based on: https://www.toptal.com/apache/apache-spark-streaming-twitter
    Original author: Hanee' Medhat

"""

from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import requests
import os


# create spark configuration
conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")
# create the Streaming Context from spark context, interval size 5 seconds
ssc = StreamingContext(sc, 5)
# setting a checkpoint for RDD recovery (necessary for updateStateByKey)
ssc.checkpoint("checkpoint_TwitterApp")
# read data from port 9009
dataStream = ssc.socketTextStream("twitter", 9009)

# dictionary holding all hashtags (values) for each topic (keys)
# competing topics: Republicans vs Democrats, Apple vs Samsung vs Google
dic = {'Apple': ["#iphone", "#apple", "#ipad", "#ipod", "#applewatch", "#imac", "#macbookpro", "#iphoneonly", "#iphone12",
         "#iphonephoto"],
       'Google': ["#pixel", "#firebase", "#google", "#chromebook", "#googlehome", "#chromecast", "#googlehomemini", "#pixel3",
          "#googleassistant", "#dialogflow"],
       'Microsoft': ["#microsoftoffice", "#powerpoint", "#microsoftword", "#excel", "#surfacepro", "#azure", "#office360",
             "#surface", "#xbox", "#windows"],
       'Samsung': ["#samsung", "#galaxy", "#galaxyfold", "#foldphone", "#SamsungSam", "#GalaxyS21", "#GalaxyNote20",
           "#GalaxyZFold2", "#GalaxyA", "#GalaxyBook"],
       'amazon': ["#alexa", "#echo", "#echodot", "#kindle", "#aws", "#amazonprime", "#amazonvideo", "#amazon", "#amazonmusic",
          "#audible"]}


# filter out tweets with tags in the dictionary
def tag_filter(line):
    res = False
    for word in line.split(" "):
        for tags in dic.values():
            if word.lower() in tags:
                res = True
    return res


hashtags = dataStream.filter(tag_filter)


# finds the topic for the hashtag
def topic_sort(line):
    res = ""
    for word in line.split(" "):
        for key in dic.keys():
            for value in dic[key]:
                if value == word.lower():
                    res = key
    return res

# rank the polarity of each tweet
def sentiment(tweet):
    sia = SIA()
    polarity = sia.polarity_scores(tweet)

    if polarity['compound'] > 0.2:
        return 'pos'
    elif polarity['compound'] < -0.2:
        return 'neg'
    else:
        return 'neu'


# map each hashtag to be a pair of (hashtag,1)
hashtag_counts = hashtags.map(lambda x: (topic_sort(x) + "-" + sentiment(x), 1))


# adding the count of each hashtag to its last count
def aggregate_tags_count(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)


# do the aggregation, note that now this is a sequence of RDDs
hashtag_totals = hashtag_counts.updateStateByKey(aggregate_tags_count)


if os.path.exists('graph_data.txt'):
    os.remove('graph_data.txt')

graph_data = open('graph_data.txt', 'a+')
output = open('B_out.txt', 'a+')


# process a single time interval
def process_interval(time, rdd):
    # print a separator
    print("----------- %s -----------" % str(time))
    output.write("----------- %s -----------\n" % str(time))
    try:
        all_rdd = rdd.sortBy(lambda x:x[0], False).take(1000)

        # print it nicely
        for tag in all_rdd:
            graph_data.write('{:<40} {}\n'.format(tag[0], tag[1]))
            output.write('{:<40} {}\n'.format(tag[0], tag[1]))
            print('{:<40} {}'.format(tag[0], tag[1]))
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


# do this for every single interval
hashtag_totals.foreachRDD(process_interval)

# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()

# close files
graph_data.close()
output.close()
