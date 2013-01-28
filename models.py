from flask import Flask

"""
Commented out Mongo stuff for now while we figure out the server situation.
from flaskext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'x'
app.config['MONGOALCHEMY_USER'] = 'x'
app.config['MONGOALCHEMY_PASSWORD'] = 'x'
app.config['MONGOALCHEMY_SERVER_AUTH'] = False
db = MongoAlchemy(app)
"""

"""
#This is for MongoDB
#defines the Bot object
class Bot(db.Document):
    bothandle = db.StringField(required=False)
    created_at = db.StringField(required=False)
    botlocation = db.StringField(required=False)
    botname = db.StringField(required=False)
    botdesc = db.StringField(required=False)
    friendscount = db.IntField(required=False)
    followerscount = db.IntField(required=False)
    imgurl = db.StringField(required=False)
    boturl = db.StringField(required=False)
    status = db.StringField(required=False)
    bottimezone = db.StringField(required=False)
    primarylanguage = db.StringField(required=False)
    keywordtriggers = db.StringField(required=False)
    discussiontopics = db.StringField(required=False)
"""

#This is for shelve.
class Bot(object):
    def __init__(self, bothandle=None, created_at=None, botlocation=None, botname=None, botdesc=None, friendscount=None, followerscount=None, imgurl=None, boturl=None, status=None, bottimezone=None, primarylanguage=None, keywordtriggers=None, discussiontopics=None):
        self.bothandle = bothandle
        self.created_at = created_at
        self.botlocation = botlocation
        self.botname = botname
        self.botdesc = botdesc
        self.friendscount = friendscount
        self.followerscount = followerscount
        self.imgurl = imgurl
        self.boturl = boturl
        self.status = status
        self.bottimezone = bottimezone
        self.primarylanguage = primarylanguage
        self.keywordtriggers = keywordtriggers
        self.discussiontopics = discussiontopics
        self.last_update = last_update