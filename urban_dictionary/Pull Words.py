# -*- coding: utf-8 -*-
import tweepy
import cPickle as pickle
#get tokens from the Twitter application
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

#set up tweepy with twitter app tokens
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

#open the list of already-recorded words
try:
    word_file = open('defined_words.p', 'rb')
    word_dump = pickle.load(word_file)
except:
    word_dump = []

#place the last 3200 tweets in a list
ud_statuses = []
for x in tweepy.Cursor(api.user_timeline, screen_name="urbandictionary").pages():
    for y in x:
        ud_statuses.append(x)

#extract the defined word from each tweet,
#and add it to a list with its creation time
words = []
for tweet in ud_statuses:
    try:
        words.append((" ".join(tweet.text.split(": ")[0].split(" ")[1:]).lower(), tweet.created_at))
    except:
        continue

#based on creation time, add new words to the
#list of recorded words called word_dump
latest_time = max([word[1] for word in word_dump])
for word in words:
    if word[1] < latest_time:
        pass
    else:
        word_dump.append(word)

#repickle the list
pickle.dump(word_dump, open('defined_words.p', 'wb'))

