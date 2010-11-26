##############################################################
# Gets size of each place (using crude metric)
# Figures out median and quartiles and plots distribution
##############################################################
import county_dict
import json
import osgb
import os
import psycopg2
import sys
import urllib2
from django.template.defaultfilters import slugify
import util

# connect to postgres database
try:
    conn_string = "host='localhost' dbname='domesday' user='postgres' password=''"  
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print "Connected!\n"
except:
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

all_places = []

def calculate_place_size():
    print "calculate_place_size()"
    # Get all place IDs and names.
    sql_string = "SELECT id, vill FROM domes_place;"
    cursor.execute(sql_string)
    
    for place in cursor.fetchall():
        place_details = {}
        place_details['id'] = place[0]
        place_details['vill'] = place[1]
        print id, vill
        sql_string = "SELECT manor_id FROM domes_manor_place WHERE place_id=%s" % id
        cursor.execute(sql_string)
        place_details['totaL_geld'] = 0.0
        if len(cursor.fetchall()) > 1:
            print 'FOUND PLACE WITH MORE THAN ONE MANOR! %s %s' % (id, vill)
        else:
            print 'only one manor for  %s %s' % (id, vill)
        for manor in cursor.fetchall():
            sql_string = "SELECT geld FROM domes_manor WHERE structidx=%s" % manor[0]  
            cursor.execute(sql_string)
            for geld in cursor.fetchall():
                if geld[0]:
                    place_details['totaL_geld'] += geld[0] 
                    print place_details['totaL_geld']  
        all_places.append(place_details)

calculate_place_size()
all_places
print all_places[0:9]
cursor.close()
conn.close()

