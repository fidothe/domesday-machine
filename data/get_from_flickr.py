# Get Domesday photo coordinate information from the Flickr API. 

import urllib2
import simplejson as json

API_KEY = 'a83663106e894f45dc536581ecffe54e'
API_KEY = '0844d395b1c92f85ce18b5de392ad597'
#b8ec3f48a5677c9a
#5f6c9bc6002d122a
PHOTO_ID = '5050819987'
AUTH_TOKEN = '72157625085023075-57e6120189c1fafc'
API_SIG = '5050819987'
#http://www.flickr.com/x/t/0097009/gp/54527420@N02/38Xg65

photo_url = 'http://api.flickr.com/services/rest/?method=flickr.photos' + \
              '.getInfo&api_key=%s&photo_id=%s' % \
               (API_KEY, PHOTO_ID)
print photo_url
response = urllib2.urlopen(photo_url)
html = response.read()
print "HTML: " + html