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
from tweetkey import api
from utilities import jsonjson, clean_up, word_feats, negids, posids, negfeats, posfeats, negcutoff, poscutoff, trainfeats, testfeats, classifier, pullrandimage, nltk


#This opens the botcache db for analysis and then stores tallies onto a different shelve
botcacheshelf = shelve.open('../botcachedb2')
botdatashelf = shelve.open('../botdatadb',writeback=True)

for bot in botcacheshelf.values():
    bothandle = bot.bothandle[1:]
    botdatashelf[str(bothandle)] = {'allrepliescount':0,'publicrepliescount':0,'googlechart':{}}

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



botcacheshelf.close()
botdatashelf.close()

print 'Individual bot data counts complete'