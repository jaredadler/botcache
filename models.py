from flask import Flask
from flaskext.mongoalchemy import MongoAlchemy

app = Flask(__name__)
app.config['MONGOALCHEMY_DATABASE'] = 'bot_library2'
db = MongoAlchemy(app)

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