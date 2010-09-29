import settings
from django.conf.urls.defaults import *
import domes.forms as domes_forms
from django.views.generic.simple import direct_to_template
from django.contrib.auth import views as auth_views
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Home page
    url(r'^$', 'domes.views.homepage', name="home"),
    # Map
    url(r'map/$', 'domes.views.map', name="map"),
    # Places and people
    url(r'^county/$', 'domes.views.all_counties', name="counties"),
    url(r'^place/$', 'domes.views.all_places', name="all_places"),
    url(r'^people/$', 'domes.views.all_people', name="all_people"),
    url(r'^county/(?P<county_name>.+)/$', 'domes.views.county', name="county"),
    url(r'^hundred/(?P<hundred_name>.+)/$', 'domes.views.hundred', name="hundred"),
    url(r'^place/(?P<grid>[A-Za-z0-9]+)/(?P<vill_slug>.+)/$', 'domes.views.place', name="place"),
    url(r'^owner/(?P<owner_name>.+)/$', 'domes.views.owner', name="owner"),
    url(r'^people/(?P<person_name>.+)/$', 'domes.views.person', name="person"),
    # Text and statistics
    url(r'^text/$', 'domes.views.text', name="text"),
    url(r'^book/$', 'domes.views.book', name="book"),
    url(r'^translate/$', 'domes.views.translate', name="translate"),
    url(r'^stats/$', 'domes.views.stats', name="stats"),
    # Text and statistics
    url(r'^image/$', 'domes.views.image', name="image"),
    # FAQ and to-do list
    #url(r'^forum/$', 'domes.views.forum', name="forum"),
    url(r'^about/$', 'domes.views.about', name="about"),
    url(r'^help/$', 'domes.views.help', name="help"),
    url(r'^todo/$', 'domes.views.todo', name="todo"),
    # Search page
    url(r'^search/$', 'domes.views.search', name="search"),
    # Comments
    (r'^comments/', include('django.contrib.comments.urls')),
    # API
    url(r'^api/$', 'domes.views.api', name="api"),
    url(r'^markers_within_bounds/$', 'domes.views.markers_within_bounds', name="markers_within_bounds"), 
    url(r'^all_markers/$', 'domes.views.all_markers', name="all_markers"),   
    # Contact form
    (r'^contact/', include('contact_form.urls')),
    # Json files (used for autocomplete)
    url(r'^all_places_json/$', 'domes.views.all_places_json', name="all_places_json"),
    # static files of various kinds
    (r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/media/images/favicon.ico'}),
    # Admin
    url(r'^admin/', include(admin.site.urls)),
    # Static media server for local dev
    url(r'^media/(?P<path>.*)$',       'django.views.static.serve', {'document_root': settings.MEDIA_DIR, 'show_indexes':True}),
    #(r'^forum/', include('snapboard.urls')),
    (r'^accounts/login/$', auth_views.login,
    {'template_name': 'forum/signin.html'}, 'auth_login'),
    (r'^accounts/logout/$', auth_views.logout,
    {'template_name': 'forum/signout.html'}, 'auth_logout'),
    (r'^admin/(.*)', admin.site.root),
)
