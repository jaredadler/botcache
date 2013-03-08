# -*- coding: utf-8 -*-
import csv
import operator
import cPickle as pickle
from datetime import datetime
from datetime import timedelta
from collections import Counter


#load the list of defined words
word_dump = pickle.load(open('word_dump.p', 'rb'))

#create a list of words defined in the last seven days
last_week_time = datetime.utcnow() - timedelta(days=7)
last_week_words = []
for word in word_dump:
    if word[1] > last_week_time:
        last_week_words.append(word)
    else:
        pass

#list of top 20 most commonly-defined words last week
lastweek_toptwenty = sorted(dict(Counter([word[0] for word in last_week_words])).iteritems(), key=lambda item: item[1], reverse=True)[:20]
#list of top 20 most commonly-defined words since we started running the script
alltime_toptwenty = sorted(dict(Counter([word[0] for word in word_dump])).iteritems(), key=lambda item: item[1], reverse=True)[:20]

#write the top 20 lists to csv for use later
with open('lastweek.csv', 'wb') as lastweek:
    csvfile = csv.writer(lastweek, delimiter=",", quoting=csv.QUOTE_ALL)
    for word in lastweek_toptwenty:
        csvfile.writerow(word)
with open('alltime.csv', 'wb') as alltime:
	csvfile = csv.writer(alltime, delimiter=",", quoting=csv.QUOTE_ALL)
	for word in alltime_toptwenty:
		csvfile.writerow(word)



