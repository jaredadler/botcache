#This should run once every 2-4 hours.
#To keep shelvedb light, it doesn't archive past the current moment.
#We can update this later when we have a proper Mongo database so it starts collecting all tweets

import twitter
import codecs
import sys
import shelve
import feedparser
import datetime


import sys
sys.path.append('../')
sys.path.append('mysite/')
from tweetkey import api
from utilities import jsonjson, clean_up, pullrandimage


#imports NLTK fun
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
import re


#This opens the botcache db for analysis and then stores individual bot data onto a different shelve
botcacheshelf = shelve.open('botcachedb2')
botdatashelf = shelve.open('botdatadb',writeback=True)

#filters out just the confirmed bots
BotDB = []
for bot in botcacheshelf.values():
    if bot.status == 'confirmed':
        BotDB.append(bot)
    else:
        pass
    
#NLTK functions
#used for NLTK sentiment analysis
def word_feats(words):
    return dict([(word, True) for word in words])

negids = movie_reviews.fileids('neg')
posids = movie_reviews.fileids('pos')
negfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'neg') for f in negids]
posfeats = [(word_feats(movie_reviews.words(fileids=[f])), 'pos') for f in posids]
negcutoff = len(negfeats)*3/4
poscutoff = len(posfeats)*3/4
trainfeats = negfeats[:negcutoff] + posfeats[:poscutoff]
testfeats = negfeats[negcutoff:] + posfeats[poscutoff:]
#print 'train on %d instances, test on %d instances' % (len(trainfeats), len(testfeats))
classifier = NaiveBayesClassifier.train(trainfeats)
#print 'accuracy:', nltk.classify.util.accuracy(classifier, testfeats)
print 'NLTK stuff done'

#Cleans up text by removing stopwords and puncutation.
def clean_up(text):
    text = text.lower() 
    text = re.findall(r'\w+', text,flags = re.UNICODE | re.LOCALE) 
    clean_uptext = []
    for word in text:
        if word not in stopwords.words('english'):
            clean_uptext.append(word)
    return clean_uptext


#Heavy lifting for the individual bot pages.
for bot in BotDB:
    bothandle = bot.bothandle[1:]
    botdatashelf[str(bothandle)] = {'allrepliescount':0,'publicrepliescount':0,'googlechart':{},'replycomplexity':0,'tweetcomplexity':0,'botsentiment':'','audiencesentiment':'','cleanreplies':[],'fd':[]}

    #Gets all the timeline stuff
    y = jsonjson('https://api.twitter.com/1/statuses/user_timeline.json?count=100&screen_name=@%s' % str(bothandle))
    twittertimeline = y
    x = jsonjson('http://search.twitter.com/search.json?q=@%s%%20-RT&rpp=100&include_entities=true&result_type=mixed' % str(bothandle))
    replytimeline = x['results']
    retweettimeline = api.GetSearch('RT @' + str(bothandle))
    
    #Checks for multiple user handles as a sign of conversational embeddedness
    embedtimeline = []
    newreplytimeline = []
    for reply in replytimeline:
        newreplytimeline.append(reply['text'])
    #print newreplytimeline
    for reply in newreplytimeline:
        try:
            if reply.count('@') > 1:
                embedtimeline.append(reply)
            elif reply.split()[0].lower() != "@" + str(bothandle):
                embedtimeline.append(reply)
            else:
                #print "Skipped " + reply + " in checking for embeddedness."
                pass
        except:
            print "Error"
    embeddedness = []
    embeddedness = (float(len(embedtimeline)), float(len(newreplytimeline)))
    if embeddedness == 1:
        embeddedness = "Error Calculating"
    else:
        embeddedness = embeddedness
        publicrepliescount = embeddedness[0]
        allrepliescount = embeddedness[1]
        botdatashelf[str(bothandle)]['publicrepliescount'] = int(publicrepliescount)
        botdatashelf[str(bothandle)]['allrepliescount'] = int(allrepliescount)

    #Converts most recent 100 tweets and replies into a dict of the day of the month and tweet count.
    recentrepliesdays = []
    recenttweetsdays = []

    for tweet in replytimeline:
        recentrepliesdays.append(tweet['created_at'].split()[1])
    for tweet in twittertimeline:
        recenttweetsdays.append(tweet['created_at'].split()[2])
    print recentrepliesdays
    print recenttweetsdays
    googlechart = {'30': [0, 0], '02': [0, 0], '03': [0, 0], '26': [0, 0], '01': [0, 0], '06': [0, 0], '07': [0, 0], '04': [0, 0], '05': [0, 0], '08': [0, 0], '09': [0, 0], '28': [0, 0], '29': [0, 0], '14': [0, 0], '24': [0, 0], '25': [0, 0], '27': [0, 0], '20': [0, 0], '21': [0, 0], '11': [0, 0], '10': [0, 0], '13': [0, 0], '12': [0, 0], '15': [0, 0], '22': [0, 0], '17': [0, 0], '16': [0, 0], '19': [0, 0], '18': [0, 0], '31': [0, 0], '23': [0, 0]}
    for i in set(recentrepliesdays):
        googlechart[i][0] = recentrepliesdays.count(i)
    for i in set(recenttweetsdays):
        googlechart[i][1] = recenttweetsdays.count(i)
    botdatashelf[str(bothandle)]['googlechart'] = googlechart

    #This is NLTK stuff for the Conversations page. Lots of heavy lifting here!
    #Sets up a string of replies for NLTK interpretation
    replytimelinenltk = []
    for reply in replytimeline:
        replytimelinenltk.append(reply['text'])
    replytimelinenltk = str(replytimelinenltk)
    replycomplexity = len(set(replytimelinenltk))
    #print replytimelinenltk
    botdatashelf[str(bothandle)]['replycomplexity'] = replycomplexity

    #Cleans up replies for the word cloud
    cleanreplies = clean_up(replytimelinenltk)
    for x in cleanreplies:
        if x == str(bothandle):
            cleanreplies.remove(x)
        else:
            pass
    cleanreplies = ' '.join(cleanreplies)
    print cleanreplies
    botdatashelf[str(bothandle)]['cleanreplies'] = cleanreplies

    #Sets up a string of tweets for NLTK interpretation
    tweettimelinenltk = []
    for tweet in twittertimeline:
        tweettimelinenltk.append(tweet['text'])
    tweettimelinenltk = str(tweettimelinenltk)
    tweetcomplexity = len(set(tweettimelinenltk))
    #print tweettimelinenltk
    botdatashelf[str(bothandle)]['tweetcomplexity'] = tweetcomplexity

    #Calls the sentiment analysis stuff, marks as positive or negative
    botsentiment = classifier.classify(word_feats(clean_up(tweettimelinenltk)))
    if botsentiment == 'pos':
        botsentiment = 'comedybot.png'
    else:
        botsentiment = 'tragedybot.png'
    #print word_feats(clean_up(tweettimelinenltk))
    #print botsentiment
    audiencesentiment = classifier.classify(word_feats(clean_up(replytimelinenltk)))
    if audiencesentiment == 'pos':
        audiencesentiment = 'comedybot.png'
    else:
        audiencesentiment = 'tragedybot.png'
    #print word_feats(clean_up(replytimelinenltk))
    #print audiencesentiment
    botdatashelf[str(bothandle)]['audiencesentiment'] = audiencesentiment
    botdatashelf[str(bothandle)]['botsentiment'] = botsentiment

    fd = nltk.FreqDist(cleanreplies.split(' '))
    fd = fd.items()[0:10]
    botdatashelf[str(bothandle)]['fd'] = fd


botcacheshelf.close()
botdatashelf.close()

print 'Individual bot data counts complete'