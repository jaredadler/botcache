#This script runs manually. You can use it to create a new bot or modify an existing bot.
#This is a temporary measure until we have a better input form and login system.
#But for now it's more secure to run a script in the background via SSH than via the web site.

import shelve
import twitter
from tweetkey import api
from utilities import jsonjson
from models import Bot

#This opens the botcache db for
botcacheshelf = shelve.open('botcachedb2',writeback=True)

#prints the existing bot cache
print " "
print "--- BotCache ---"
print " "

for bot in botcacheshelf.values():
    print "bot: " + str(bot.bothandle) + " | " + str(bot.status)

print " "
nextstep = raw_input("New bot or modify bot status? (n or m) ")

if nextstep == 'n':
    twitterhandle = raw_input("Enter bot handle (no @ sign) ") 
    if "@" + str(twitterhandle) in botcacheshelf.keys():
        print "Oops, bot already in database"
    else:
        xx = jsonjson("http://api.twitter.com/1/users/show.json?screen_name=%s" % twitterhandle)
        created_at = xx['created_at']
        created_at = created_at.split()
        created_at = str(created_at[1]) + " " + str(created_at[2]) + ", " + str(created_at[5]) + " " + str(created_at[3])
        
        # API requests via Twitter helper library
        bothandle = "@" + str(twitterhandle)
        botuser = api.GetUser(str(twitterhandle))
        friendscount = botuser.GetFriendsCount()
        followerscount = botuser.GetFollowersCount()
        botlocation = botuser.GetLocation()
        botname = botuser.GetName()
        botdesc = botuser.GetDescription()
        botdesc = botdesc
        boturl = botuser.GetUrl()
        bottimezone = botuser.GetTimeZone()
        imgurl = botuser.GetProfileImageUrl()
        
        print "Created at: "
        print created_at
        print "Friends: "
        print friendscount
        print "Followers: "
        print followerscount
        print "Location: "
        print botlocation
        print "Name: "
        print botname
        print "Desc: "
        print botdesc
        print "URL: "
        print boturl
        print "Time zone: "
        print bottimezone
        print "Img URL: "
        print imgurl
        print " "
        keywordtriggers = raw_input("Enter keyword triggers (separated by commas): ")
        discussiontopics = raw_input("Enter discussion topics: ")
        primarylanguage = raw_input("Enter primary language: ")
        newbot = Bot(bothandle = bothandle,\
                 boturl = boturl,\
                created_at = created_at,\
                 botlocation = botlocation,\
                botname = botname,\
                         botdesc = botdesc,\
                             friendscount = int(friendscount),\
                                 followerscount = int(followerscount),\
                                     imgurl = imgurl,\
                                         status='under consideration',\
                                             bottimezone = bottimezone,\
                                                 primarylanguage = primarylanguage,\
                                                     keywordtriggers = keywordtriggers,\
                                                         discussiontopics = discussiontopics)
        #print newbot
        botcacheshelf[str(newbot.bothandle)] = newbot
        #print botcacheshelf
        
        print "New bot " + str(newbot.bothandle) + " added!"
            
elif nextstep == 'm':
    bothandle = "@" + raw_input("Enter bothandle (no @ sign): ")
    status = raw_input("Enter status ('under consideration', 'confirmed', 'not accepted'): ")
    botcacheshelf[str(bothandle)].status = status
    print "New status for " + str(bothandle) + ": "
    print botcacheshelf[str(bothandle)].status
else:
    pass

#This has to come at the end in order to save all changes.
botcacheshelf.close()