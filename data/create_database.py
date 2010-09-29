##############################################################
# Script to convert Domesday tab-separated files to SQL
# BEWARE! - will OVERWRITE your existing database
##############################################################
import county_dict
import json
import MySQLdb
import MySQLdb.cursors
import osgb
import os
import psycopg2
import sys
import urllib2
from django.template.defaultfilters import slugify

# convert tab-separated line into array
def line_to_values(line):
    line = line.strip('\n')
    line = line.decode("mac_roman")
    line = line.encode("utf-8")
    line = line.replace('"','')
    line = line.strip('\r')
    line = line.strip('\"')
    values = line.split('\t')
    return values
    
# convert OS code into Geodjango-friendly string
def convert_os_to_coords(oscode):
    lon, lat = osgb.osgb_to_lonlat(oscode)
    value_string = "ST_GeomFromText('POINT(" + str(lon) + " " + str(lat) + ")',4326)"
    return value_string

def check_null_field(field):
    if field=="":
        field = "null"
    return field

try:
	conn_string = "host='localhost' dbname='domesday' user='postgres' password=''"  
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    print "Connected!\n"
except:
    exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
    sys.exit("Database connection failed!\n ->%s" % (exceptionValue))

###############################
# Places
###############################
def get_places():
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/PlacesForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_place;')
    # get values from tab file 
    for (counter, line) in enumerate(file_lines): 
           if counter==0:
               continue
           values = line_to_values(line)
#"PlacesIdx" "County"    "Phillimore"    "Hundred"   "Vill"  "Area"  "XRefs" "OSrefs"    "OScodes"
           # deal with lines that end too soon
           if len(values) < 9:
               extra_values = 9 - len(values)
               for i in range(0, extra_values):
                   values.append('')
           placeid = MySQLdb.escape_string(values[0])
           structidx = MySQLdb.escape_string(values[1])
           subidx = MySQLdb.escape_string(values[2])
           if subidx=="":
               subidx = MySQLdb.escape_string("1")
           county = MySQLdb.escape_string(county_dict.county_dict[values[3]])
           phillimore = MySQLdb.escape_string(values[4])
           area = MySQLdb.escape_string(values[5])
           hundred = MySQLdb.escape_string(values[6])
           vill = values[7]
           #print vill
           # ignore entries with no vill name
           if vill=="":
                continue
           # TODO: deal with unusual vill names
           if vill[0]=="`":
                pass
           vill = MySQLdb.escape_string(vill)
           vill_slug = MySQLdb.escape_string(slugify(vill))
           vill_slug = vill_slug[:49] # limit of 50 characters on slugfields
           grid = values[8].strip()
           # deal with unknown grid refs
           if grid=="" or grid=="-" or grid=="--" or grid=="?" or grid=="??" or grid=="???" or grid=="--":
               grid = 'null'
               location = 'null'
           else: # convert to lat/lon
               grid = MySQLdb.escape_string(grid)
               location = convert_os_to_coords(grid)       
           holding = MySQLdb.escape_string(values[9])
           units = MySQLdb.escape_string(values[10])
           waste86 = MySQLdb.escape_string(values[11])
           mysql_string = "INSERT INTO domes_place (placeid, structidx, subidx, county, phillimore, "
           mysql_string += " area, hundred, vill, vill_slug, holding, units, waste86, grid, location) VALUES ('"
           mysql_string += placeid + "', '" + structidx + "', '" + subidx  + "', '" + county  + "', '"
           mysql_string += phillimore  + "', '" + area + "', '" + hundred + "', '" + vill + "', '"
           mysql_string += vill_slug  + "', '" + holding + "', '" + units + "', '" + waste86 + "', '"
           mysql_string += grid  + "', " +  location  + ");"
           #print mysql_string
           cursor.execute(mysql_string)

###############################
# Manors
###############################
def get_manors():
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ManorsForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_manors;')
    # get values from tab file - skip the first line
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            line = line.strip('\n')
            line = line.strip('\r')
            values = line.split('\t')
            if len(values) < 56:
                extra_values = 56 - len(values)
                for i in range(0, extra_values):
                    values.append('')
            try: 
                # update the database
                mysql_string = "INSERT INTO domes_manors (structidx, county, phillimore, headofmanor, geld, gcode, villtax, taxedon, "
                mysql_string += "lordsland, newland, ploughlands, pcode, lordsploughs, mensploughs, totalploughs, lordsploughspossible, "
                mysql_string += "mensploughspossible, totalploughspossible, villagers, smallholders, slaves, femaleslaves, "        
                mysql_string += "freemen, free2men, priests, cottagers, otherpop, miscpop, miscpopcategories, burgesses, mills, "       
                mysql_string += "millvalue, meadow ,meadowunits, pasture, pastureunits, woodland, woodlandunits, "          
                mysql_string += "fisheries, salthouses, payments, paymentsunits, churches, churchland, value86, value66, "
                mysql_string += "valueqr, value_string, render, waste, waste66, wasteqr, waste86, duplicates, subholdings, notes) " 
                mysql_string += "VALUES (";
                for (counter, value) in enumerate(values):
                    if counter == 1:
                        value = county_dict.county_dict[value]
                    mysql_string += "'" + MySQLdb.escape_string(value) + "'"
                    if counter != (len(values)-1):
                        mysql_string += ", " 
                    else:
                        mysql_string += ");"
                print mysql_string
                cursor.execute(mysql_string)
            except:
                print 'problem with mysql string : ' + mysql_string

###############################
# TREOwners
###############################
def get_treowners():
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TREForAHRC.txt')
    f = open(fn, 'r')
    # clear any existing entries
    cursor.execute('delete from domes_treowners;')
    # get values from tab file - skip the first line
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            values = line_to_values(line)
            if len(values) < 14:
                extra_values = 14 - len(values)
                for i in range(0, extra_values):
                    values.append('')
            tre_id = values[0]
            structidx = values[1]
            subidx = check_null_field(values[2])
            county = county_dict.county_dict[values[3]]
            phillimore = MySQLdb.escape_string(values[4])
            overlord66 = MySQLdb.escape_string(values[5])
            lord66 = MySQLdb.escape_string(values[6])
            idxoverlord66 = MySQLdb.escape_string(values[7])
            idxlord66 = MySQLdb.escape_string(values[8])
            holding = MySQLdb.escape_string(values[9])
            units = MySQLdb.escape_string(values[10])
            value66 = MySQLdb.escape_string(values[11])
            value66qr86  = MySQLdb.escape_string(values[12])
            v66code = MySQLdb.escape_string(values[13])
            try: 
                # update the database - add a new row, ignore duplicates
                mysql_string = "INSERT INTO domes_treowners (tre_id, structidx, subidx, county, " 
                mysql_string += "phillimore, overlord66, lord66, idxoverlord66, idxlord66, holding, units"
                mysql_string += ", value66, value66qr86, v66code) VALUES (" 
                mysql_string += tre_id + ", " + structidx + ", " + subidx  + ", '" + county  + "', '"
                mysql_string += phillimore  + "', '" + overlord66 + "', '" + lord66 + "', '" + idxoverlord66 + "', '"
                mysql_string += idxlord66  + "', '" + holding + "', '" + units + "', '" + value66 + "', '"
                mysql_string += value66qr86  + "', '" +  v66code  + "');"
                cursor.execute(mysql_string)
            except Exception, e:
                #print e.pgerror
                print e
                print 'problem with mysql string : ' + mysql_string
                sys.exit()

###############################
# TRWOwners
###############################
def get_trwowners():
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TRWForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_trwowners;')
    # get values from tab file - skip the first line
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            line = line.strip('\n')
            values = line.split('\t')
            if len(values) < 15:
                extra_values = 15 - len(values)
                for i in range(0, extra_values):
                    values.append(None)
            try: 
                # update the database - add a new row, ignore duplicates
                mysql_string = "INSERT INTO domes_trwowners (trw_id, structidx, subidx, county, "
                mysql_string += "phillimore, teninchief, lord86, demesne86, holding, units, value86, "
                mysql_string += " v86code, waste86, idxTinC, idxLord86) "
                mysql_string += "VALUES (";
                for (counter, value) in enumerate(values):
                    value = value.replace('"', '')
                    if counter == 3:
                        value = county_dict.county_dict[value]
                    mysql_string += "'" + MySQLdb.escape_string(value) + "'"
                    if counter != (len(values)-1):
                        mysql_string += ", "
                    else:
                        mysql_string += ");"
                cursor.execute(mysql_string)
            except:
                print 'problem with mysql string : ' + mysql_string

###############################
# Images
###############################
def get_images():
    print 'get_images'
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ImagesForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_image;')
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            values = line_to_values(line)
            if len(values) < 10:
                extra_values = 10 - len(values)
                for i in range(0, extra_values):
                    values.append(None)
            structidx = check_null_field(values[0])
            county = county_dict.county_dict[values[1]]
            phillimore = MySQLdb.escape_string(values[2])
            imagesub = MySQLdb.escape_string(values[3])
            image = values[4].replace('\\', '/') 
            image = MySQLdb.escape_string(image)
            marked = MySQLdb.escape_string(values[5])
            x1 = MySQLdb.escape_string(values[6])
            y1 = MySQLdb.escape_string(values[7])
            x2 = MySQLdb.escape_string(values[8])
            y2 = MySQLdb.escape_string(values[9])
            mysql_string = "INSERT INTO domes_image (structidx, county, "
            mysql_string += "phillimore, imagesub, image, marked, x1, y1, x2, y2) "
            mysql_string += "VALUES (";
            mysql_string += structidx + ", '" + county + "', '" + phillimore + "', '"
            mysql_string += imagesub + "', '" + image + "', '" + marked + "', "
            mysql_string += x1 + ", " + y1 + ", " + x2 + ", " + y2 + ");"
            print mysql_string
            cursor.execute(mysql_string)
                
###############################
# Call all the functions...
###############################
#get_places()
#get_manors()

get_names()
#get_treowners()
#get_trwowners()

#get_livestock()
#get_counties()

get_images()

# commit everything (postgres only)
conn.commit()

# close the SQL connections
cursor.close()
conn.close()

# 
# ###############################
# # Livestock
# ###############################
# def get_livestock():
#     # open tab file
#     f = open('domesdaystatistics_livestock.tab', 'r')
#     file_lines = f.readlines()
#     # clear any existing entries
#     cursor.execute('delete from domes_livestock;')
#     for (counter, line) in enumerate(file_lines): 
#         if counter == 0:
#             continue
#         else:
#             line = line.strip('\n')
#             line = line.strip('\r')
#             values = line.split('\t')
#             if len(values) < 23:
#                 extra_values = 23 - len(values)
#                 for i in range(0, extra_values):
#                     values.append("")
#             structidx = values[0]
#             county = county_dict.county_dict[values[1]]
#             phillimore = MySQLdb.escape_string(values[2])
#             cobs_1086 = check_null_field(values[3])
#             cobs_1066 = check_null_field(values[4])
#             cattle_1086  = check_null_field(values[5])
#             cattle_1066 = check_null_field(values[6])
#             cows_1086 = check_null_field(values[7])
#             cows_1066 = check_null_field(values[8])
#             pigs_1086 = check_null_field(values[9])
#             pigs_1066 = check_null_field(values[10])
#             sheep_1086 = check_null_field(values[11])
#             sheep_1066 = check_null_field(values[12])
#             goats_1086  = check_null_field(values[13])
#             goats_1066  = check_null_field(values[14])
#             beehives_1086 = check_null_field(values[15])
#             beehives_1066 = check_null_field(values[16])
#             wild_mares_1086 = check_null_field(values[17])
#             wild_mares_1066 = check_null_field(values[18])
#             other_1086 = MySQLdb.escape_string(values[19])
#             other_code_1086 = MySQLdb.escape_string(values[20])
#             other_1066 = MySQLdb.escape_string(values[21])
#             other_codes_1066 = MySQLdb.escape_string(values[22])
#             try:               
#                 mysql_string = "INSERT INTO domes_livestock (structidx, county, phillimore, cobs_1086, cobs_1066, "
#                 mysql_string += "cattle_1086, cattle_1066, cows_1086, cows_1066, pigs_1086, pigs_1066, sheep_1086, sheep_1066, "
#                 mysql_string += "goats_1086, goats_1066, beehives_1086, beehives_1066, wild_mares_1086, wild_mares_1066, "
#                 mysql_string += "other_1086, other_code_1086, other_1066, other_codes_1066) " 
#                 mysql_string += "VALUES (";
#                 mysql_string += structidx + ", '" + county + "', '" + phillimore  + "', " + cobs_1086  + ", "
#                 mysql_string += cobs_1066  + ", " + cattle_1086 + ", " + cattle_1066 + ", " + cows_1086 + ", "
#                 mysql_string += cows_1066  + ", " + pigs_1086 + ", " + pigs_1066 + ", " + sheep_1086 + ", "
#                 mysql_string += sheep_1066  + ", " + goats_1086 + ", " + goats_1066 + ", " + beehives_1086 + ", "
#                 mysql_string += beehives_1066  + ", " + wild_mares_1086 + ", " + wild_mares_1066 + ", '" + other_1086 + "', '"
#                 mysql_string += other_code_1086 + "', '" +  other_1066   + "', '" +  other_codes_1066 + "');"
#                 cursor.execute(mysql_string)
#             except:
#                 print 'problem with mysql string : ' + mysql_string
# 
# ###############################
# # Counties (uses several files)
# ###############################
# def get_counties():
#     # open tab file
#     f = open('domesdaystatistics_totals_query.tab', 'r')
#     file_lines = f.readlines()
#     # clear any existing entries
#     cursor.execute('delete from domes_county;')
#     # get values from tab file - skip the first line
#     for (counter, line) in enumerate(file_lines): 
#         if counter == 0:
#             continue
#         else:
#             line = line.strip('\n')
#             values = line.split('\t')
#             try:   
#                 # update the database - add a new row, ignore duplicates
#                 mysql_string = "INSERT INTO domes_county (short_code, geld, "
#                 mysql_string += "land, lordsploughs, mensploughs, totalploughs, villagers, "
#                 mysql_string += "smallholders, slaves, ancill, freemen, free_men, priests, cotts, burgesses, "
#                 mysql_string += "other, misc, mills, mvalue, val66, valqr, val86, churches, chland, name, circuit) "
#                 mysql_string += "VALUES (";
#                 for (counter, value) in enumerate(values):
#                     mysql_string += "'" + MySQLdb.escape_string(value) + "'"
#                     if counter != (len(values)-1):
#                         mysql_string += ", "
#                     else:
#                         mysql_string += ", '', 0);"  
#                 cursor.execute(mysql_string)
#             except:
#                 print 'problem with mysql string : ' + mysql_string
#     # domesdaystatistics_counties.tab - has county code + circuit
#     f = open('domesdaystatistics_counties.tab', 'r')
#     file_lines = f.readlines()
#     # get values from tab file - skip the first line
#     for (counter, line) in enumerate(file_lines): 
#         if counter == 0:
#             continue
#         else:
#             values = line_to_values(line)
#             try: 
#                 # update the database - add a new row, ignore duplicates
#                 mysql_string = "UPDATE domes_county SET circuit='"
#                 mysql_string += values[1] + "' WHERE short_code='" + values[0] + "';";
#                 cursor.execute(mysql_string)
#             except:
#                 print 'problem with mysql string : ' + mysql_string
#     # domes_county.tab - has county code + long name
#     f = open('domes_county.tab', 'r')
#     file_lines = f.readlines()
#     # get values from tab file - skip the first line
#     for (counter, line) in enumerate(file_lines): 
#             line = line.strip('\n')
#             values = line.split('\t')
#             try: 
#                 # update the database - add a new row, ignore duplicates
#                 mysql_string = "UPDATE domes_county SET name='"
#                 mysql_string += values[1] + "' WHERE short_code='" + values[0] + "';";
#                 cursor.execute(mysql_string)
#             except:
#                 print 'problem with mysql string : ' + mysql_string
# 
# ###############################
# # Names
# ###############################
# def get_names():
#     print 'get_names'
#     # open tab file
#     fn = os.path.join(os.path.dirname(__file__), 'new_data/NamesForAHRC.txt')
#     f = open(fn, 'r')
#     file_lines = f.readlines()
#     # clear any existing entries
#     cursor.execute('delete from domes_name;')
#     # get values from tab file - skip the first line
#     for (counter, line) in enumerate(file_lines): 
#         if counter == 0:
#             continue
#         else:
#             values = line_to_values(line)
#             if len(values) < 8:
#                 extra_values = 8 - len(values)
#                 for i in range(0, extra_values):
#                     values.append(None)
#             namesidx = check_null_field(values[0])
#             name = MySQLdb.escape_string(values[1])
#             county = county_dict.county_dict[values[2]]
#             phillimore = MySQLdb.escape_string(values[3])
#             namecode = MySQLdb.escape_string(values[4])
#             gendercode = values[4].replace('\\', '/') 
#             churchcode = MySQLdb.escape_string(values[5])
#             xrefs = MySQLdb.escape_string(values[6])
#             mysql_string = "INSERT INTO domes_name (namesidx, name, county, "
#             mysql_string += "namecode, gendercode, churchcode, xrefs) "
#             mysql_string += "VALUES (";
#             mysql_string += namesidx + ", '" + name + "', '" + county + "', '"
#             mysql_string += namecode + "', '" + gendercode + "', '"
#             mysql_string += churchcode + "', '" + xrefs + "');"
#             print mysql_string
#             cursor.execute(mysql_string)