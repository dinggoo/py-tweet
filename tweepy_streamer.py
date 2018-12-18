from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy import API

import twitter_api_credentials
import json

# OSC part
import argparse
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import osc_message_builder
from pythonosc import udp_client
import threading

# windows encoding stuff
import sys
import codecs
import time

# stream keywords
KEYWORDS = ['scram c baby', 'elephant']

sys.stdout = codecs.getwriter('utf8')(sys.stdout.buffer)

# OSC CLIENT
# parser = argparse.ArgumentParser()
# parser.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
# parser.add_argument("--port", type=int, default=7777, help="The port the OSC server is listening on")
# args = parser.parse_args()
client = udp_client.SimpleUDPClient("127.0.0.1", 7777)

# parser2 = argparse.ArgumentParser()
# parser2.add_argument("--ip", default="127.0.0.1", help="The ip of the OSC server")
# parser2.add_argument("--port", type=int, default=6666, help="The port to listen on")
# args2 = parser2.parse_args()

auth = OAuthHandler(twitter_api_credentials.CONSUMER_KEY, twitter_api_credentials.CONSUMER_SECRET)
auth.set_access_token(twitter_api_credentials.ACCESS_TOKEN, twitter_api_credentials.ACCESS_TOKEN_SECRET)
api = API(auth)

class TwitterStreamer():
    def stream_tweets(self, hash_tag_list):
        # This handles Twitter auth and connection to the twitter streaming api
        listener = StdOutListener()
        stream = Stream(auth=api.auth, listener=listener, tweet_mode='extended')
        stream.filter(track=hash_tag_list)


class StdOutListener(StreamListener):
    def on_data(self, data):
        tweet = json.loads(data)
        if 'extended_tweet' in tweet:
            client.send_message("/tweet_long",  'name: '+tweet['user']['name']+' -> '+tweet['extended_tweet']['full_text'])
        elif 'retweeted_status' in tweet:
            retweet = tweet['retweeted_status']
            if 'extended_tweet' in retweet:
                client.send_message("/retweet_long", 'name: '+tweet['user']['name']+' -> '+tweet['retweeted_status']['extended_tweet']['full_text'])
            else:
                client.send_message("/retweet_short", 'name: '+tweet['user']['name']+' -> '+tweet['retweeted_status']['text'])
        elif 'text' in tweet:
            client.send_message("/tweet_short", 'name: '+tweet['user']['name']+' -> '+tweet['text'])

        client.send_message("/dict", data)


    def on_error(self, status):
        print(status)


def copyKeywords(unused_addr, args, val):
    # hash_tag_list = val
    # print(type(hash_tag_list))
    # newList = hash_tag_list.split()
    # print(type(newList))
    # keywords = val
    if val == 1:
        sys.exit(0)
    # twitter_streamer.stream_tweets(keywords)


if __name__ == "__main__":
    twitter_streamer = TwitterStreamer()

    # OSC RECEIVER (not reliable)
    # dispatcher = dispatcher.Dispatcher()
    #
    # # dispatcher.map("/keywords", print)
    # dispatcher.map("/keywords", copyKeywords, "test")
    #
    # server = osc_server.ThreadingOSCUDPServer((args.ip, args2.port), dispatcher)
    # server_thread = threading.Thread(target=server.serve_forever)
    # server_thread.daemon = True
    # server_thread.start()

    # input('Press ENTER to exit')
    twitter_streamer.stream_tweets(KEYWORDS)
    #
    # while True:
    #     time.sleep(1)
