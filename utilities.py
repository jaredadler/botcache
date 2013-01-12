from flask import Flask
from flaskext.mongoalchemy import MongoAlchemy

import urllib2, urllib, json, simplejson
import xml.dom.minidom as minidom
import htmllib
from random import choice

#imports NLTK fun
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews
from nltk.corpus import stopwords
import re

#function to acquire the json for a web page at x. Useful for searching Twitter.
def jsonjson(x):
     req = urllib2.Request(x)
     opener = urllib2.build_opener()
     instance = opener.open(req)
     return simplejson.load(instance)
     
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


#function to acquire the json for a web page at x. Useful for searching Twitter.
def jsonjson(x):
     req = urllib2.Request(x)
     opener = urllib2.build_opener()
     instance = opener.open(req)
     return simplejson.load(instance)

#code modified from http://www.blog.pythonlibrary.org/2010/11/12/python-parsing-xml-with-minidom/
def pullrandimage(feed):
    """
    Pulls all image links found in Tumblr xml and selects one at random.
    """
    newfeed = minidom.parse(urllib.urlopen(feed))
    newnewfeed = []
    linkfeed = []
    newnewfeed = newfeed.getElementsByTagName('photo-url')
    for feed in newnewfeed:
        nodes = feed.childNodes
        for node in nodes:
            if node.nodeType == node.TEXT_NODE:
                linkfeed.append(node.data)
    return choice(linkfeed)

#Cleans up text by removing stopwords and puncutation.
def clean_up(text):
    text = text.lower() 
    text = re.findall(r'\w+', text,flags = re.UNICODE | re.LOCALE) 
    clean_uptext = []
    for word in text:
        if word not in stopwords.words('english'):
            clean_uptext.append(word)
    return clean_uptext