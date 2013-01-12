#This should run once an hour.

import twitter
import codecs
import sys
import shelve
import feedparser
import datetime


import sys
sys.path.append('../')
from tweetkey import api

#This opens the botcache db for analysis and then stores tallies onto a different shelve
botcacheshelf = shelve.open('../botcachedb2')
tallyshelf = shelve.open('../botcachetallies2',writeback=True)
##BotDB = Bot.query.all()

now = datetime.datetime.now()
BotDB = []
for bot in botcacheshelf.values():
    if bot.status == 'confirmed':
        BotDB.append(bot)
    else:
        pass

#If you're running the script for the first time, you'll need to uncomment these so it creates the data models.
#Be sure to comment them back out afterward, or you'll lose your data.
#tallyshelf['botcount'] = {now:0}
#tallyshelf['followersum'] = {now:0}
#tallyshelf['friendsum'] = {now:0}
#tallyshelf['timezones'] = {now:0}
#tallyshelf['kardashiancount'] = {now:0}
#tallyshelf['kcoefficient'] = {now:0}


#This gets a count of bots based on the len of the BotDB
##botcount = len(BotDB)
botcount = []
for bot in botcacheshelf.values():
    if bot.status == 'confirmed':
        botcount.append(bot)
    else:
        pass

tallyshelf['botcount'][now] = len(botcount)


#Gets the sum of bot followers
followersum = []
##for bot in BotDB:
##    followersum.append(bot.followerscount)
for bot in BotDB:
    followersum.append(bot.followerscount)
followersum = sum(followersum)
tallyshelf['followersum'][now] = followersum



#Gets the sum of bot friends
friendsum = []
for bot in BotDB:
    friendsum.append(bot.friendscount)
friendsum = sum(friendsum)
tallyshelf['friendsum'][now] = friendsum



#This gets all the timezones and maps them into an array for the Google Map
timezonelist = []
result_dict = {}
for bot in BotDB:
    timezonelist.append(bot.bottimezone)
result_dict = dict( [ (i, timezonelist.count(i)) for i in set(timezonelist)])
timezones = result_dict.items()
tallyshelf['timezones'][now] = timezones




#Gets the Kardashian Count
kim = api.GetUser('kimkardashian')
kardashiancount = kim.GetFollowersCount()
kcoefficient = float(friendsum) / float(kardashiancount)
tallyshelf['kardashiancount'][now] = kardashiancount
tallyshelf['kcoefficient'][now] = kcoefficient



botcacheshelf.close()
tallyshelf.close()

print 'Botopia Tallies count complete'