import urllib, hashlib
from django import template

register = template.Library()

def show_place(place):
	counties = place.county.all()
	return {'place':place, 'counties': counties}
	
register.inclusion_tag('show_place.html')(show_place)