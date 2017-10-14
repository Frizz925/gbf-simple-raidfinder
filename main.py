#!/usr/bin/env python
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from configparser import ConfigParser
import codecs
config = ConfigParser()
config.readfp(codecs.open('config.ini', encoding='utf8'))

import requests
import pyperclip
import tweepy

import traceback
import time
import sys
import os
import re

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')
access_token = os.environ.get('ACCESS_TOKEN')
access_token_secret = os.environ.get('ACCESS_TOKEN_SECRET')

TWEET_SOURCE = 'グランブルー ファンタジー'
TWEET_SOURCE_URL = 'http://granbluefantasy.jp/'

def logMessage(message):
    if  isinstance(message, list):
        message = '\n'.join(message)
    message = u'[%s] %s\n' % (time.strftime('%H:%M:%S'), message)
    # Windows terminals can't print unicode characters properly
    message = message.encode().decode(sys.stdout.encoding)
    sys.stdout.write(message)
    sys.stdout.flush()

class RaidListener(tweepy.StreamListener):
    def __init__(self, config, onTweet=None):
        super(RaidListener, self).__init__()
        self.config = config
        self.onTweet = onTweet
        self.regexp = r'([^\s]+)( :Battle ID\nI need backup!\n| :参戦ID\n参加者募集！\n)(.+)$'
        self.englishBosses = [x.strip() for x in config['Bosses']['English'].split(',')]
        self.japaneseBosses = [x.strip() for x in config['Bosses']['Japanese'].split(',')]
        self.allBosses = self.englishBosses + self.japaneseBosses
        self.streamFilter = self.getStreamFilter()

    def getStreamFilter(self):
        tweetFilter = ['Lv%d' % x for x in range(15, 200, 5)]
        tweetFilter += self.englishBosses
        return tweetFilter

    def filterTweet(self, tweet):
        if tweet.source != TWEET_SOURCE: return False
        if tweet.source_url != TWEET_SOURCE_URL: return False
        if not re.search(self.regexp, tweet.text): return False
        return True

    def parseTweetText(self, text):
        parts = text.split('\n')
        match = re.search(self.regexp, text)
        index = text.index(match.group(1))
        return {
            'message': text[:index],
            'code': match.group(1),
            'boss': match.group(3)
        }

    def parseTweet(self, tweet):
        if not self.filterTweet(tweet):
            return None

        parsed = self.parseTweetText(tweet.text)
        if not parsed['boss'] in self.allBosses:
            return None

        parsed['username'] = tweet.user.screen_name
        parsed['name'] = tweet.user.name
        parsed['lang'] = tweet.lang

        return parsed

    def handleTweet(self, tweet):
        message = [
            u'Found new raid:',
            u'[Boss] %s (%s)' % (tweet['code'], tweet['boss']),
            u'[From] %s (%s)' % (tweet['username'], tweet['name']),
            u'[Message] %s' % tweet['message']
        ]
        if self.config['Raidfinder']['AutoCopy'] == 'yes':
            pyperclip.copy(tweet['code'])
            message.append(u'[Action] Copied to clipboard')
        logMessage(message)

        if self.onTweet is not None:
            self.onTweet(tweet)

    def on_connect(self):
        logMessage('Connected.')

    def on_status(self, status):
        parsed = self.parseTweet(status)
        if parsed:
            self.handleTweet(parsed)

class Autopilot:
    def __init__(self, config):
        self.port = int(config['Autopilot']['Port'])
        self.interval = float(config['Autopilot']['IntervalInSeconds'])
        self.lastRequest = 0

    def elapsed(self):
        return time.time() - self.lastRequest

    def reset(self):
        self.lastRequest = time.time()

    def sendRequest(self, tweet):
        if self.elapsed() >= self.interval:
            requests.post('http://localhost:%d/raid' % self.port, 
                data=tweet['code'], headers={'Content-Type': 'text/plain'})
            self.reset()

def main():
    if config['Autopilot']['Enabled'] == 'yes':
        logMessage('Autopilot enabled')
        autopilot = Autopilot(config)
        onTweet = autopilot.sendRequest
    else:
        onTweet = None
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    listener = RaidListener(config, onTweet=onTweet)
    while True:
        try:
            logMessage('Starting stream...')
            stream = tweepy.Stream(auth=auth, listener=listener)
            stream.filter(track=listener.streamFilter)
        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            traceback.print_exc(e)
            input()
            sys.exit(1)

if __name__ == '__main__':
    main()
