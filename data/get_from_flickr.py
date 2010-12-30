# Get Domesday photo coordinate information from the Flickr API. 
import urllib2
import simplejson as json

#URLs: 
#http://www.flickr.com/x/t/0097009/gp/54527420@N02/38Xg65
#http://www.flickr.com/photos/54527420@N02/5050819987/

API_KEY = '0844d395b1c92f85ce18b5de392ad597'
PHOTO_ID = '5050819987'
SECRET='b61d24c764'

photo_url = 'http://api.flickr.com/services/rest/?method=flickr.photos' + \
              '.getInfo&api_key=%s&photo_id=%s&secret=%s' % \
               (API_KEY, PHOTO_ID, SECRET)
print photo_url
response = urllib2.urlopen(photo_url)
html = response.read()
print "HTML: " + html