# -*- coding: utf-8 -*-

from flask import Flask
from flask import escape, request, Response, url_for, render_template, flash, redirect, jsonify
from flask.ext.login import LoginManager, login_user, logout_user, login_required, current_user
from flask.ext import uploads
from flask.ext.uploads import IMAGES, configure_uploads, patch_request_class
from flaskext.mongoalchemy import MongoAlchemy
import flask
import twitter
import codecs
import sys
from collections import Counter

#brings in API key
from tweetkey import api

#imports models and utilities
from models import Bot
import utilities
from utilities import jsonjson, clean_up, word_feats, negids, posids, negfeats, posfeats, negcutoff, poscutoff, trainfeats, testfeats, classifier, pullrandimage, nltk

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'bot_library2'
db = MongoAlchemy(app)


###
# Hardcoded web site variables, uncomment to get this working on the test server
#htmlpage = 'http://50.116.10.109/~an/robotcensus/'
#pythonpage = 'http://50.116.10.109/~an/p/robotcensus'

#Local web site variables, uncomment to get this working when running locally
htmlpage = '/'
pythonpage =''

css = htmlpage + 'static/robotcensus.css'
smlogo = htmlpage + 'static/botworldcensusgraphic.100px.png'
biglogo = htmlpage + 'static/botworldcensusgraphic.png'
###
    


@app.route('/index')
def landingpage():
    print >> sys.stderr, "Received GET request to /index."
    try:
        BotDB = Bot.query.all()
    
        #This gets a count of bots based on the len of the BotDB
        botcount = len(BotDB)
        
        #Gets the sum of bot followers
        followersum = []
        for bot in BotDB:
            followersum.append(bot.followerscount)
        followersum = sum(followersum)
        
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
            try:
                #BotDB = shelve.open('botchive.db')
                twitterhandle = request.form['twitterhandle']
                print twitterhandle
                test = Bot.query.filter(Bot.bothandle == '@'+ str(twitterhandle)).first()
                print test
                testquery = str(test.bothandle[1:])
                print testquery
                # Checks if bot already exists.
                return render_template('alreadyexists.html',twitterhandle=twitterhandle,css=css,smlogo=smlogo,\
                                                           pythonpage=pythonpage,htmlpage=htmlpage)
            except:
                try:
                    xx = jsonjson("http://api.twitter.com/1/users/show.json?screen_name=%s" % twitterhandle)
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
        except:
            return "Error with botchive at consideration level"
        newbot.save()
        print Bot.query.all()[0].bothandle
        return render_template('robotcomplete.html', twitterhandle=bothandle,css=css,smlogo=smlogo,\
                               pythonpage=pythonpage,htmlpage=htmlpage)
    else:
        return "Error"
    
@app.route('/testtest')
def test():
    try:
        print 'george'
        a = Bot.query.all()
        print a
        b = Bot.query.filter(Bot.bothandle == '@csik').first()
        print b
        print b.bothandle
        return "george"
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])

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
    BotDB = Bot.query.all()
    #This gets all the timezones and maps them into an array for the Google Map
    timezonelist = []
    result_dict = {}
    for bot in BotDB:
        timezonelist.append(bot.bottimezone)
    result_dict = dict( [ (i, timezonelist.count(i)) for i in set(timezonelist)])
    timezones = result_dict.items()
    
    #This gets a count of bots based on the len of the BotDB
    botcount = len(BotDB)
    
    #Gets the sum of bot followers
    followersum = []
    for bot in BotDB:
        followersum.append(bot.followerscount)
    followersum = sum(followersum)
    
    #Gets the sum of bot friends
    friendsum = []
    for bot in BotDB:
        friendsum.append(bot.friendscount)
    friendsum = sum(friendsum)
    
    #Gets the Kardashian Count
    kim = api.GetUser('kimkardashian')
    kardashiancount = kim.GetFollowersCount()
    kcoefficient = float(friendsum) / float(kardashiancount)
    
    #
    return render_template('botopia.html',botdb=BotDB,css=css,smlogo=smlogo,pythonpage=pythonpage,htmlpage=htmlpage,\
                           timezones=timezones,botcount=botcount,followersum=followersum,friendsum=friendsum,\
                               kardashiancount=kardashiancount,kcoefficient=kcoefficient)

@app.route('/botcache')
def viewbotcache():
    print >> sys.stderr, "Received GET request to /botcache."
    try:
        BotDB = Bot.query.filter(Bot.status == 'confirmed').all()
        considered = Bot.query.filter(Bot.status == 'under consideration').all()
        consideredlist = []
        for bot in considered:
            consideredlist.append(bot.bothandle)
        return render_template('botcache.html',botdb=BotDB,consideredlist=consideredlist,css=css,smlogo=smlogo,pythonpage=pythonpage,htmlpage=htmlpage)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
    

@app.route('/botchive/<bothandle>')
def botchive_singlebot(bothandle):
    print >> sys.stderr, "Received GET request to '/botchive/<bothandle>."
    try:
        singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        discussiontopics = singlebot.discussiontopics[3:-2]
        
        
        #Return template
        return render_template('botpage.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                   pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/wiki')
def singlebotwiki(bothandle):
    print >> sys.stderr, "Received GET request to '/botchive/<bothandle>/wiki."
    try:
        singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        discussiontopics = singlebot.discussiontopics[3:-2]
        #Return template
        return render_template('botpagewiki.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                   pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/basicstats')
def singlebotstats(bothandle):
    try:
        singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        discussiontopics = singlebot.discussiontopics[3:-2]
        
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
                    print "Skipped " + reply + " in checking for embeddedness."
            except:
                print "Error"
        embeddedness = (float(len(embedtimeline)), float(len(newreplytimeline)))
        if embeddedness == 1:
            embeddedness = "Error Calculating"
        else:
            embeddedness = embeddedness

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


        #Return template
        return render_template('botpagebasicstats.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                                   pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,\
                                               embeddedness=embeddedness,googlechart=googlechart)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/botchive/<bothandle>/conversations')
def botconversations(bothandle):
    try:
        singlebot = Bot.query.filter(Bot.bothandle == '@'+ str(bothandle)).first()
        discussiontopics = singlebot.discussiontopics[3:-2]
        
        #Gets all the timeline stuff
        y = jsonjson('https://api.twitter.com/1/statuses/user_timeline.json?count=100&screen_name=@%s' % str(bothandle))
        twittertimeline = y
        x = jsonjson('http://search.twitter.com/search.json?q=@%s%%20-RT&rpp=100&include_entities=true&result_type=mixed' % str(bothandle))
        replytimeline = x['results']
        retweettimeline = api.GetSearch('RT @' + str(bothandle))
        
        #Sets up a string of replies for NLTK interpretation
        replytimelinenltk = []
        for reply in replytimeline:
            replytimelinenltk.append(reply['text'])
        replytimelinenltk = str(replytimelinenltk)
        replycomplexity = len(set(replytimelinenltk))
        #print replytimelinenltk
        
        #Cleans up replies for the word cloud
        cleanreplies = clean_up(replytimelinenltk)
        for x in cleanreplies:
            if x == str(bothandle):
                cleanreplies.remove(x)
            else:
                print "Clean clean clean"
        cleanreplies = ' '.join(cleanreplies)
        print cleanreplies
        
        #Sets up a string of tweets for NLTK interpretation
        tweettimelinenltk = []
        for tweet in twittertimeline:
            tweettimelinenltk.append(tweet['text'])
        tweettimelinenltk = str(tweettimelinenltk)
        tweetcomplexity = len(set(tweettimelinenltk))
        #print tweettimelinenltk
        
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
        
        fd = nltk.FreqDist(cleanreplies.split(' '))
        fd = fd.items()[0:10]

        #Return template
        return render_template('botpageconvos.html',css=css,smlogo=smlogo,bothandle=bothandle,singlebot=singlebot,\
                               twittertimeline=twittertimeline,replytimeline=replytimeline,retweettimeline=retweettimeline,\
                                   pythonpage=pythonpage,htmlpage=htmlpage,discussiontopics=discussiontopics,\
                                       replycomplexity=replycomplexity,tweetcomplexity=tweetcomplexity,\
                                           botsentiment=botsentiment,audiencesentiment=audiencesentiment,\
                                               cleanreplies=cleanreplies,fd=fd)
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])
        
@app.route('/blog')
def blogpage():
    print >> sys.stderr, "Received GET request to /blog."
    try:
        img = pullrandimage('http://wememechina.tumblr.com/api/read?&num=10')
        return render_template('blog.html',biglogo=biglogo,css=css,pythonpage=pythonpage,htmlpage=htmlpage,smlogo=smlogo,img=img
                               )
    except:
        print >> sys.stderr, str(sys.exc_info()[0]) # These write the nature of the error
        print >> sys.stderr, str(sys.exc_info()[1])

if __name__ == '__main__':
    app.run(debug=True)