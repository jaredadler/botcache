from flask import Flask
from flask import escape, request, Response, url_for, render_template, flash, redirect, jsonify
#from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
#from flask.ext import uploads
#from flask.ext.uploads import IMAGES, configure_uploads, patch_request_class

import flask
import twitter
import codecs
import sys
import shelve
import feedparser

#from collections import Counter

#brings in API key
from tweetkey import api

#imports models and utilities
from models import Bot
from utilities import jsonjson

app = Flask(__name__)


"""
Commented out Mongo stuff for now while we figure out the server situation.
Search for "##' to find the legacy Mongo code when it's time to restore it.

from flaskext.mongoalchemy import MongoAlchemy
import mongoalchemy
from flaskext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'x'
app.config['MONGOALCHEMY_USER'] = 'x'
app.config['MONGOALCHEMY_PASSWORD'] = 'x'
app.config['MONGOALCHEMY_SERVER_AUTH'] = False
db = MongoAlchemy(app)
"""


#Local web site variables, uncomment to get this working when running locally
htmlpage = '/'
pythonpage =''

css = htmlpage + 'static/robotcensus.css'
smlogo = htmlpage + 'static/botworldcensusgraphic.100px.png'
biglogo = htmlpage + 'static/botworldcensusgraphic.png'
###
    


@app.route('/')
def landingpage():
    print >> sys.stderr, "Received GET request to /."
    try:
        tallyshelf = shelve.open('botcachetallies2')
        followersum = tallyshelf['followersum'][sorted(tallyshelf['followersum'])[-1]]
        botcount = tallyshelf['botcount'][sorted(tallyshelf['botcount'])[-1]]
        tallyshelf.close()
        
        return render_template('index.html',biglogo=biglogo,css=css,pythonpage=pythonpage,htmlpage=htmlpage,smlogo=smlogo,\
                               followersum=followersum,botcount=botcount)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/robotsubmission', methods=['GET', 'POST'])
def robotsubmission():
    print >> sys.stderr, "Received GET request to /robotsubmission."
     # Twitter handle received
    if request.method == 'POST':
        try:
            ##try:
            # Checks if bot already exists.
            twitterhandle = request.form['twitterhandle']
            ##test = Bot.query.filter(Bot.bothandle == '@'+ str(twitterhandle)).first()
            ##testquery = str(test.bothandle[1:])
            ##print testquery
            newshelf = shelve.open('botcachedb2')
            newnewshelf = []
            for key in newshelf.keys():
                newnewshelf.append(key.lower())
            if twitterhandle.lower() in newnewshelf:
                return render_template('alreadyexists.html',twitterhandle=twitterhandle,css=css,smlogo=smlogo,\
                                                           pythonpage=pythonpage,htmlpage=htmlpage)
            else:
            ##except:
                try:
                    xx = jsonjson("http://api.twitter.com/1/users/show.json?screen_name=%s" % twitterhandle)
                    created_at = ""
                    created_at = xx['created_at']
                    created_at = created_at.split()
                    created_at = str(created_at[1]) + " " + str(created_at[2]) + ", " + str(created_at[5]) + " " + str(created_at[3])
                except:
                    print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
                    print >> sys.stderr, str(sys.exc_info()[1])
                finally:
                    # API requests via Twitter helper library
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

                    # Posts a note that the bot is being considered. Just used for testing.
                    #api.PostUpdate("New bot %s is now being considered! Visit LINK to cast your vote." % twitterhandle)
                    
                    return render_template('robotsubmission.html',twitterhandle=twitterhandle,imgurl=imgurl,\
                                           botdesc=botdesc,botlocation=botlocation,botname=botname,\
                                               followerscount=followerscount,friendscount=friendscount,\
                                                   created_at=created_at,boturl=boturl,bottimezone=bottimezone,\
                                                       css=css,smlogo=smlogo,\
                                                           pythonpage=pythonpage,htmlpage=htmlpage)
        except:
            print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
            print >> sys.stderr, str(sys.exc_info()[1])
    else:
        return "Error"

@app.route('/robotcomplete', methods=['GET', 'POST'])
def robotcomplete():
    print >> sys.stderr, "Received GET request to /robotcomplete."
    enc = sys.stdin.encoding
    # Completed robot submitted to archive
    keywordtriggers = []
    discussiontopics = []
    if request.method == 'POST':
        botname = request.form['botname']
        bothandle = request.form['bothandle']
        imgurl = request.form['imgurl']
        botlocation = request.form['botlocation']
        botdesc = request.form['botdesc']
        created_at = request.form['created_at']
        friendscount = int(request.form['friendscount'])
        followerscount = int(request.form['followerscount'])
        boturl = request.form['boturl']
        bottimezone = request.form['bottimezone']
        primarylanguage = request.form['primarylanguage']
        discussiontopics = request.form['discussiontopics']
        keywordtriggers = request.form['keywordtriggers']
        try:
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
            newshelf = shelve.open('botcachedb2',writeback = True)
            newshelf[str(newbot.bothandle)] = newbot
        except:
            return "Error with botchive at consideration level"
        ##newbot.save()
        ##print Bot.query.all()[0].bothandle
        return render_template('robotcomplete.html', twitterhandle=bothandle,css=css,smlogo=smlogo,\
                               pythonpage=pythonpage,htmlpage=htmlpage)
    else:
        return "Error"

@app.route('/about')
def aboutpage():
    print >> sys.stderr, "Received GET request to /about."
    try:
        return render_template('about.html',biglogo=biglogo,smlogo=smlogo,css=css,pythonpage=pythonpage,htmlpage=htmlpage)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/submit')
def submitpage():
    print >> sys.stderr, "Received GET request to /submit."
    try:
        return render_template('submit.html',biglogo=biglogo,smlogo=smlogo,css=css,pythonpage=pythonpage,htmlpage=htmlpage)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])

@app.route('/botopia')
def botopia():
    ##BotDB = Bot.query.all()
    newshelf = shelve.open('botcachedb2')
    tallyshelf = shelve.open('botcachetallies2')
    
    BotDB = []
    for bot in newshelf.values():
        if bot.status == 'under consideration':
            pass
        else:
            BotDB.append(bot)
    
    followersum = tallyshelf['followersum'][sorted(tallyshelf['followersum'])[-1]]
    friendsum = tallyshelf['friendsum'][sorted(tallyshelf['friendsum'])[-1]]
    kardashiancount = tallyshelf['kardashiancount'][sorted(tallyshelf['kardashiancount'])[-1]]
    kcoefficient = tallyshelf['kcoefficient'][sorted(tallyshelf['kcoefficient'])[-1]]
    botcount = tallyshelf['botcount'][sorted(tallyshelf['botcount'])[-1]]
    timezones = tallyshelf['timezones'][sorted(tallyshelf['timezones'])[-1]]
    #
    return render_template('botopia.html',botdb=BotDB,css=css,smlogo=smlogo,pythonpage=pythonpage,htmlpage=htmlpage,\
                           timezones=timezones,botcount=botcount,followersum=followersum,friendsum=friendsum,\
                               kardashiancount=kardashiancount,kcoefficient=kcoefficient)

@app.route('/botcache')
def viewbotcache():
    print >> sys.stderr, "Received GET request to /botcache."
    try:
        ##BotDB = Bot.query.filter(Bot.status == 'confirmed').all()
        ##considered = Bot.query.filter(Bot.status == 'under consideration').all()
        ##consideredlist = []
        ##for bot in considered:
        ##    consideredlist.append(bot.bothandle)
        
        newshelf = shelve.open('botcachedb2')
        BotDB = []
        consideredlist = []
        notacceptedlist = []
        for bot in newshelf.values():
            if bot.status == 'under consideration':
                consideredlist.append(bot.bothandle)
            elif bot.status == 'confirmed':
                BotDB.append(bot)
            elif bot.status == 'not accepted':
                notacceptedlist.append(bot.bothandle)
            else:
                pass
        newshelf.close()
        
        return render_template('botcache.html',botdb=BotDB,consideredlist=consideredlist,notacceptedlist=notacceptedlist,css=css,smlogo=smlogo,pythonpage=pythonpage,htmlpage=htmlpage)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
    

@app.route('/botchive/<bothandle>')
def botchive_singlebot(bothandle):
    print >> sys.stderr, "Received GET request to '/botchive/<bothandle>."
    try:
        ##singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        newshelf = shelve.open('botcachedb2')
        singlebot = newshelf['@' + str(bothandle)]
        if singlebot.status != 'confirmed':
            return "Still evaluating"
        
        else:
            discussiontopics = singlebot.discussiontopics[3:-2]
            
            #Return template
            return render_template('botpage.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                       pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/summary')
def singlebotwiki(bothandle):
    print >> sys.stderr, "Received GET request to '/botchive/<bothandle>/summary."
    try:
        ##singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        newshelf = shelve.open('botcachedb2')
        singlebot = newshelf['@' + str(bothandle)]
        if singlebot.status != 'confirmed':
            return "Still evaluating"
        else:
            discussiontopics = singlebot.discussiontopics[3:-2]
            #Return template
            return render_template('botpagesummary.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                       pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/basicstats')
def singlebotstats(bothandle):
    try:
        ##singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        newshelf = shelve.open('botcachedb2')
        singlebot = newshelf['@' + str(bothandle)]
        if singlebot.status != 'confirmed':
            return "Still evaluating"
        else:
            discussiontopics = singlebot.discussiontopics[3:-2]
            botdatashelf = shelve.open('botdatadb')
            publicrepliescount = botdatashelf[str(bothandle)]['publicrepliescount']
            allrepliescount = botdatashelf[str(bothandle)]['allrepliescount']
            googlechart = botdatashelf[str(bothandle)]['googlechart']
            botdatashelf.close()

            #Return template
            return render_template('botpagebasicstats.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                       pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,\
                                                   googlechart=googlechart,publicrepliescount=publicrepliescount,allrepliescount=allrepliescount)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/conversations')
def botconversations(bothandle):
    try:
        ##singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        newshelf = shelve.open('botcachedb2')
        singlebot = newshelf['@' + str(bothandle)]
        if singlebot.status != 'confirmed':
            return "Still evaluating"
        else:
            discussiontopics = singlebot.discussiontopics[3:-2]
            botdatashelf = shelve.open('botdatadb')
            replycomplexity = botdatashelf[str(bothandle)]['replycomplexity']
            tweetcomplexity = botdatashelf[str(bothandle)]['tweetcomplexity']
            botsentiment = botdatashelf[str(bothandle)]['botsentiment']
            audiencesentiment = botdatashelf[str(bothandle)]['audiencesentiment']
            cleanreplies = botdatashelf[str(bothandle)]['cleanreplies']
            fd = botdatashelf[str(bothandle)]['fd']
        
        #Return template
        return render_template('botpageconvos.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                   pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,\
                                       replycomplexity=replycomplexity,tweetcomplexity=tweetcomplexity,\
                                           botsentiment=botsentiment,audiencesentiment=audiencesentiment,\
                                               cleanreplies=cleanreplies,fd=fd)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
        
@app.route('/botchive/<bothandle>/favorites')
def botfavorites(bothandle):
    newshelf = shelve.open('botcachedb2')
    try:
        singlebot = newshelf['@' + str(bothandle)]
        discussiontopics = singlebot.discussiontopics[3:-2]
        
        y = jsonjson('https://api.twitter.com/1/statuses/user_timeline.json?count=200&screen_name=%s&include_rts=1&include_entities=true' % bothandle)
        twittertimeline = []
        for tweet in y:
            if tweet['retweet_count'] > 3:
                twittertimeline.append(tweet)
        return render_template('botpagefavorites.html',css=css,smlogo=smlogo,bothandle=bothandle,\
                               twittertimeline=twittertimeline,singlebot=singlebot,\
                                   pythonpage=pythonpage,htmlpage=htmlpage)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])


@app.route('/blog')
def blogpage():
    print >> sys.stderr, "Received GET request to /blog."
    try:
        botcachefeed = feedparser.parse('feed://botcache.tumblr.com/tagged/botcacheblog/rss')
        botcachefeed = botcachefeed['entries']
        return render_template('blog.html',biglogo=biglogo,css=css,pythonpage=pythonpage,htmlpage=htmlpage,smlogo=smlogo,botcachefeed=botcachefeed)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])

if __name__ == '__main__':
    app.run(debug=True)
