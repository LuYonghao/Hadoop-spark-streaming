from tweepy import StreamListener
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
import socket
import sys
import json

# Replace the values below with yours
consumer_key="ZAPfZLcBhYEBCeRSAK5PqkTT7"
consumer_secret="M81KvgaicyJIaQegdgXcdKDeZrSsJz4AVrGv3yoFwuItQQPMay"
access_token="2591998746-Mx8ZHsXJHzIxAaD2IxYfmzYuL3pYNVnvWoHZgR5"
access_token_secret="LJDvEa0jL7QJXxql0NVrULTAniLobe2TAAlnBdXRfm1xF"


class TweetListener(StreamListener):
    # prints tweets to local for processing
    def on_data(self, data):
        try:
            global connection

            full_tweet = json.loads(data)
            tweet_text = full_tweet['text']
            print("------------------------------------------")
            print(tweet_text + '\n')
            connection.send(str.encode(tweet_text + '\n'))

        except:
            e = sys.exc_info()[0]
            print("Error: %s" % e)

        return True

    def on_error(self, status):
        print(status)


TCP_IP = socket.gethostbyname(socket.gethostname())
TCP_PORT = 9009

connection = None
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print("Waiting for TCP connection...")
connection, address = s.accept()
print("Connected... Starting getting tweets.")

# setup connection
listener = TweetListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, listener)

# setup search terms

twitter = ["#follow", "#followback", "#Twitterers", "#tweegram", "#followme"]

mostPop = ["#HappyFathersDay2021", "#June20Coup", "#SundayMorning", "#FathersDay", "#EminevimHilesi", "#dad",
           "#FathersDay2021", "#HappyFathersDay"]
apple = ["#iphone", "#apple", "#ipad", "#ipod", "#applewatch", "#imac", "#macbookpro", "#iphoneonly", "#iphone12",
         "#iphonephoto"]
google = ["#pixel", "#firebase", "#google", "#chromebook", "#googlehome", "#chromecast", "#googlehomemini", "#pixel3",
          "#googleassistant", "#dialogflow"]
microsoft = ["#microsoftoffice", "#powerpoint", "#microsoftword", "#excel", "#surfacepro", "#azure", "#office360",
             "#surface", "#xbox", "#windows"]
amazon = ["#alexa", "#echo", "#echodot", "#kindle", "#aws", "#amazonprime", "#amazonvideo", "#amazon", "#amazonmusic",
          "#audible"]
samsung = ["#samsung", "#galaxy", "#galaxyfold", "#foldphone", "#SamsungSam", "#GalaxyS21", "#GalaxyNote20",
           "#GalaxyZFold2", "#GalaxyA", "#GalaxyBook"]

track = twitter + mostPop + apple + google + microsoft + samsung + amazon
# language = ['en']

try:
    # stream.filter(track=track, languages=language)
    stream.filter(track=track)
except KeyboardInterrupt:
    s.shutdown(socket.SHUT_RD)
