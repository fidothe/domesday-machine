import urllib, hashlib
from django import template

register = template.Library()

def show_gravatar(email, size=48):
    #default = "http://localhost:8000{ settings.MEDIA_URL }}/images/lion1.gif"
    url = "http://www.gravatar.com/avatar.php?"
    url += urllib.urlencode({
        'gravatar_id': hashlib.md5(email).hexdigest(), 
        #'default': default, 
        'size': str(size)
    })
    return {'gravatar': {'url': url, 'size': size}}

register.filter('show_gravatar', show_gravatar)