from flask import Flask
from flaskext.mongoalchemy import MongoAlchemy

import urllib2, urllib, json, simplejson
import xml.dom.minidom as minidom
import htmllib
from random import choice

#function to acquire the json for a web page at x. Useful for searching Twitter.
def jsonjson(x):
     req = urllib2.Request(x)
     opener = urllib2.build_opener()
     instance = opener.open(req)
     return simplejson.load(instance)

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