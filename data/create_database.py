# -*- coding: mac-roman -*-
##############################################################
# Script to convert Domesday tab-separated files to SQL
# BEWARE! - will OVERWRITE your existing database
##############################################################
import glob
import os
import psycopg2
import simplejson as json
import sys
import urllib2
from PIL import Image
from django.template.defaultfilters import slugify
import county_dict
import osgb
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

# Some entries in Places are duplicates. In here, we store
# the duplicate place IDs, used later for PlaceRef table. 
place_mapper = {}

# return the status of a place as defined in 
# John Palmer's encoding system
def place_status(place_name):
    place_name = place_name.strip("'")
    if place_name[0]=="`":
        status = "'No longer exists as a named location, but can be identified on the ground.'"
        place_name = place_name.replace("'","")
        place_name = place_name.replace("`","")
    elif place_name[0]=="{":
        status = "'Lost, can only be located approximately.'"
        place_name = place_name.replace("{","")
        place_name = place_name.replace("}","")
    else:
        status = "NULL" 
    if place_name!="NULL":
        place_name = "'%s'" % (place_name)
    return place_name, status

###############################
# Functions to do with places
###############################

def get_counties():
    '''Turns our county dictionary into database tables.'''
    print "get_counties()"  
    cursor.execute('delete from domes_county;')
    for key,value in county_dict.county_dict.items():
           sql_string = "INSERT INTO domes_county (short_code,name,name_slug) VALUES (%s,%s,%s)"
           name_slug = unicode(slugify(value))
           cursor.execute(sql_string, (key,value,name_slug))
    conn.commit()
    
def get_places():
    '''
    Turn PlacesForAHRC into a set of unique places - i.e. places with 
    unique name and grid combination.
    If we find multiple places with the same vill/grid combination (this is 
    quite common, as places are often listed under different counties or areas)
    we update the County/Area references, and store the IDs temporarily in the
    place_mapper dict, and use this to map from Manors to Places.
    '''
    print "get_places()"
    global place_mapper
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/PlacesForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_place;')
    for (counter, line) in enumerate(file_lines): 
           if counter==0:
               continue
           values = util.line_to_values(line,9)
           id = values[0]
           print id
           county = values[1]
           if not county: # TODO: check this
               continue
           else:
               county = util.postgres_escape(county, False)
           phillimore = util.postgres_escape(values[2], False)
           hundred = util.postgres_escape(values[3], False)
           hundred_slug = slugify(hundred)
           hundred, status = place_status(hundred)
           sql_string = "INSERT INTO domes_hundred (name,name_slug,status) SELECT "
           sql_string += hundred + ", '" + hundred_slug + "', " + status + " WHERE "
           sql_string += hundred + " NOT IN (SELECT NAME FROM domes_hundred);"
           cursor.execute(sql_string)
           vill = values[4]
           # `' = place no longer exists but can be identified on ground 
           # [] name inside brackets = lost, only approximately located
           if vill=="" or not vill:
                continue
           if vill[0]=="`":
                pass
           vill_slug = slugify(vill)[:49]
           vill = util.postgres_escape(vill, False)
           vill, status = place_status(vill)
           area = util.postgres_escape(values[5], False)
           area_slug = slugify(area)
           # Create an area entry if one doesn't exist already.
           if area!="NULL": 
               sql_string = "INSERT INTO domes_area (name,name_slug) SELECT "
               sql_string += area + ", '" + area_slug + "' WHERE "
               sql_string += area + " NOT IN (SELECT NAME FROM domes_area);"
               cursor.execute(sql_string)
           xrefs = util.postgres_escape(values[6], False)
           grid = util.postgres_escape(values[7], False)
           os_codes = util.postgres_escape(values[8], False)
           if grid!="NULL" and grid!=None:
               location = util.convert_os_to_coords(grid.strip("'"))
           else:
               grid="'XX0000'"
               location="NULL"
               # TODO: But! Sometimes there are places that cannot be
               # located on the ground. Sometimes, though, there are 
               # multiple possible places, referenced in PlaceForms.
               # This is the 'Great and Little Abington' problem. 
               # Deal with this somehow. 
           # Check for existing entries with the same name/grid/vill combo.
           sql_string = "SELECT * from domes_place WHERE grid="
           sql_string += grid + " AND vill=" + vill + ";"
           cursor.execute(sql_string)
           results = cursor.fetchall()
           if len(results)==0:
               sql_string = "INSERT INTO domes_place (id,phillimore,hundred_id,"
               sql_string += "vill,vill_slug,xrefs,grid,os_codes,location,status) VALUES ("
               sql_string += id + ", " + phillimore + ", " + hundred + ", "
               sql_string += vill + ", '" + vill_slug + "', " + xrefs + ", "
               sql_string += grid + ", " + os_codes + ", " + location + ", " + status + ");"
               cursor.execute(sql_string)
           else: # duplicate found - just update county and area refs with existing ID 
               place_mapper[id] = str(results[0][0])
               id = str(results[0][0])
           sql_string = "SELECT * from domes_place_county WHERE place_id="
           sql_string += id + " AND county_id=" + county + ";"
           cursor.execute(sql_string)
           results = cursor.fetchall()
           if len(results)==0:
              sql_string = "INSERT INTO domes_place_county (place_id,county_id) VALUES ("      
              sql_string += id + ", " + county + ");"
              cursor.execute(sql_string)
           sql_string = "SELECT * from domes_place_area WHERE area_id="
           sql_string += area + " AND place_id=" + id + ";"
           cursor.execute(sql_string)
           results = cursor.fetchall()
           if len(results)==0:
               sql_string = "INSERT INTO domes_place_area (place_id,area_id) VALUES ("      
               sql_string += id + ", " + area + ");"
    conn.commit()
    
def get_placerefs():
    '''Map place IDs to manor IDs. Replaces duplicate place IDs using place mapper.'''
    print "get_placerefs()"
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ByPlaceForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_manor_place;')
    # get values from tab file 
    for (counter, line) in enumerate(file_lines): 
           if counter==0:
               continue
           values = util.line_to_values(line,13)
           manor_id = values[1]
           place_id = values[12]
           if not place_id:
               continue
           # Check if this place ID has been stored in our mapper, replace it if so
           if place_id in place_mapper.keys():
               place_id = place_mapper[place_id]
           sql_string = "INSERT INTO domes_manor_place (manor_id, place_id) SELECT "
           sql_string += manor_id + ", " + place_id + " WHERE ("
           sql_string += manor_id + ", " + place_id + ") NOT IN "
           sql_string += "(SELECT manor_id, place_id FROM domes_manor_place);"
           cursor.execute(sql_string)
    conn.commit()

###############################
# Manors
###############################
def get_manors():
    print "get_manors()"
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ManorsForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_manor;')
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            values = util.line_to_values(line,56)
            # basics
            structidx = values[0]
            county = values[1] 
            phillimore = util.postgres_escape(values[2])
            headofmanor = values[3]
            # print headofmanor
            # print util.postgres_escape(headofmanor)
            # headofmanor = None
            waste = util.postgres_escape(values[49])
            waste66 = util.postgres_escape(values[50])
            wasteqr = util.postgres_escape(values[51])
            waste86 = util.postgres_escape(values[52])
            duplicates = util.postgres_escape(values[53])
            subholdings = util.postgres_escape(values[54])
            notes = util.postgres_escape(values[55])
            # valuation
            geld = values[4]
            gcode = util.postgres_escape(values[5])
            villtax = values[6]
            taxedon = values[7]
            value86 = values[44]
            value66 = values[45]
            valueqr = values[46]
            value_string = util.postgres_escape(values[47])
            render = util.postgres_escape(values[48])
            # land
            lordsland = values[8]
            newland = values[9]
            ploughlands = values[10]
            pcode = util.postgres_escape(values[11])
            lordsploughs = values[12]
            mensploughs = values[13]
            totalploughs = values[14]
            lordsploughspossible = values[15]
            mensploughspossible = values[16]
            totalploughspossible = values[17] #30
            # people
            villagers = values[18]
            smallholders = values[19]
            slaves = values[20]
            femaleslaves = values[21]
            freemen = values[22]
            free2men = values[23]
            priests = values[24]
            cottagers = values[25]
            otherpop = values[26]
            miscpop = values[27]
            miscpopcategories = util.postgres_escape(values[28])
            burgesses = values[29]#42
            #other stuff in the manor - mills, pasture etc
            mills = values[30]
            millvalue = values[31]
            meadow = util.postgres_escape(values[32])
            meadowunits = util.postgres_escape(values[33])
            pasture = util.postgres_escape(values[34])
            pastureunits = util.postgres_escape(values[35])
            woodland = util.postgres_escape(values[36])
            woodlandunits = util.postgres_escape(values[37])
            fisheries = values[38]
            salthouses = values[39]
            payments = values[40]
            paymentsunits = util.postgres_escape(values[41])
            churches = values[42]
            churchland = values[43]#56
            sql_string = "INSERT INTO domes_manor (structidx, county_id, phillimore, headofmanor,"
            sql_string += "duplicates, subholdings, notes, waste, waste66, wasteqr, waste86,"
            sql_string += "geld,gcode,villtax,taxedon,value86,value66,valueqr,value_string,render,"#20
            sql_string += "lordsland,newland,ploughlands,"
            sql_string += "pcode,lordsploughs,mensploughs,totalploughs,lordsploughspossible,"
            sql_string += "mensploughspossible,totalploughspossible,"#30
            sql_string += "villagers,smallholders,slaves,femaleslaves,"
            sql_string += "freemen,free2men,priests,cottagers,otherpop,miscpop,miscpopcategories,burgesses,"
            sql_string += "mills,millvalue,meadow,meadowunits,"#46
            sql_string += "pasture,pastureunits,woodland,woodlandunits,fisheries,salthouses,payments,"
            sql_string += "paymentsunits,churches,churchland) VALUES ("#56
            sql_string += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            sql_string += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            sql_string += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
            sql_string += "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_string, (structidx,county,phillimore,headofmanor,duplicates,subholdings,notes,\
                          waste,waste66,wasteqr,waste86,geld,gcode,villtax,\
                          taxedon,value86,value66,valueqr,value_string,render,lordsland,\
                          newland,ploughlands,pcode,lordsploughs,mensploughs,totalploughs,lordsploughspossible, \
                          mensploughspossible,totalploughspossible,villagers,smallholders,slaves,femaleslaves,freemen, \
                          free2men,priests,cottagers,otherpop,miscpop,miscpopcategories,burgesses,\
                          mills,millvalue,meadow,meadowunits,pasture,pastureunits,woodland,\
                          woodlandunits,fisheries,salthouses,payments,paymentsunits,churches,churchland))
    conn.commit()

###############################
# Livestock
###############################
def get_livestock():
    print "get_livestock()"
    fn = os.path.join(os.path.dirname(__file__), 'new_data/LivestockAnna.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            values = util.line_to_values(line,23)
            structidx = values[0]
            cobs_1086 = values[3]
            cobs_1066 = values[4]
            cattle_1086  = values[5]
            cattle_1066 = values[6]
            cows_1086 = values[7]
            cows_1066 = values[8]
            pigs_1086 = values[9]
            pigs_1066 = values[10]
            sheep_1086 = values[11]
            sheep_1066 = values[12]
            goats_1086  = values[13]
            goats_1066  = values[14]
            beehives_1086 = values[15]
            beehives_1066 = values[16]
            wild_mares_1086 = values[17]
            wild_mares_1066 = values[18]
            other_1086 = values[19]
            other_code_1086 = util.postgres_escape(values[20])
            other_1066 = values[21]
            other_codes_1066 = util.postgres_escape(values[22]) 
            sql_string = "UPDATE domes_manor SET cobs_1086=%s, cobs_1066=%s, "
            sql_string += "cattle_1086=%s, cattle_1066=%s, cows_1086=%s, cows_1066=%s, pigs_1086=%s, "
            sql_string += "pigs_1066=%s, sheep_1086=%s, sheep_1066=%s, goats_1086=%s, goats_1066=%s, "
            sql_string += "beehives_1086=%s, beehives_1066=%s, wild_mares_1086=%s, wild_mares_1066=%s, "
            sql_string += "other_1086=%s, other_code_1086=%s, other_1066=%s, other_codes_1066=%s "
            sql_string += " WHERE structidx=%s;"
            cursor.execute(sql_string, (cobs_1086, cobs_1066, \
                           cattle_1086, cattle_1066, cows_1086, cows_1066, pigs_1086, pigs_1066, sheep_1086, sheep_1066, \
                           goats_1086, goats_1066, beehives_1086, beehives_1066, wild_mares_1086, wild_mares_1066, \
                           other_1086, other_code_1086, other_1066, other_codes_1066, structidx))
    conn.commit()

###############################
# Names
###############################
# Ask JP about xrefs: 'see Ansager the Breton', etc. 
#NameCode   code (L) for unidentified personal name-element, recorded in its Latin form
#GenderCode male or female (M/F)
church_codes = {
'a': 'English abbeys', 
'b': 'English archbishops and bishops', 
'c': 'English canons', 
'd': 'Other English clergy and institutions', 
'e': 'Foreign bishops', 
'f': 'Foreign monasteries', 
'g': 'Foreign nunneries', 
'h': 'Minsters & other landowning churches', 
'n': 'English nunneries', 
None:None,
}
#Apart from M/F, the Gender field records two other values: blanks (783 records), which are cross-references; 
#and dashes (630), which are institutional names. At present both are recorded as "None". Removing "None" 
# would be OK for cross-references (Xref would be better) but wrong for institutions which - despite "None" 
# - do map the data for those institutions if my spot checks are representative: can you label them 
# Xref & Church respectively?
#155860 "Durham (St Cuthbert), monks of"    "LIN"   "3,4"       "i" "a" - Ask JP about this
gender_codes = {
'M': 'Male',
'm': 'Male',
'F': 'Female',
None: 'None',
'-': 'Institution',
'i':'i' 
}
def get_people():
    print 'get_people()'
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/UniqueNames.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_person;')
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:
            values = util.line_to_values(line,6)
            #print values
            namesidx = values[0]
            name = values[1]
            if name is None:
                continue
            name_slug = slugify(name)[:49]
            name = util.postgres_escape(name)
            name = name.decode("utf-8")
            namecode = util.postgres_escape(values[2])
            gendercode = util.postgres_escape(gender_codes[values[3]])
            churchcode = util.postgres_escape(church_codes[values[4]])
            #print namecode, gendercode, churchcode
            xrefs = values[5]
            if xrefs:
                #print xrefs
                xrefs = xrefs.decode("utf-8").encode("utf-8")
            xrefs = util.postgres_escape(xrefs)
            sql_string = "INSERT INTO domes_person (namesidx, name, name_slug, "
            sql_string += "namecode, gendercode, churchcode, xrefs) "
            sql_string += " VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql_string, (namesidx, name, name_slug,\
                                  namecode, gendercode, churchcode, xrefs))
    conn.commit()

def get_peoplenotes():
    print 'get_peoplenotes()'
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ids.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_namenotes;')
    for (counter, line) in enumerate(file_lines): 
        continue
    
###############################
# TREOwners
###############################
# TODO: append 'probable' to the match, if appropriate

def get_treowners():
    print "get_treowners()"
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TREForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_manor_lord66;')
    cursor.execute('delete from domes_manor_overlord66;')
    unique_names, match_names = util.get_unique_names()
    missing_lord66 = ['114700', '120750', '120810', '126950', '156850',\
               '165150', '167070', '171720', '185950', '23300', '23350',\
                '252200', '259390', '272000', '372010', '382300', '397560',\
                '399450', '431700', '476750', '48700', '495170', '519100',\
                '524260', '532050', '576050', '62450', '85500']
    missing_overlord66 = ['126950', '156850', '159250', '160400', '259380',\
                   '259390', '344560', '344670', '50650', '50830', '530050',\
                   '532050', '574150']
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:   
            values = util.line_to_values(line,14)
            tre_id = values[0]
            structidx = values[1]
            if not structidx:
                continue
            idxoverlord66 = values[7]
            if idxoverlord66 in missing_overlord66:
                continue
            if idxoverlord66 is not None:
                if (idxoverlord66 not in unique_names): # if this ID isn't in our unique list
                    match_found = False
                    for potential_match in match_names: 
                       if idxoverlord66==potential_match['matchidx']:
                           idxoverlord66=potential_match['unique']
                           match_found = True
                           break
                    if not match_found:
                        #print 'match not found for idxoverlord66 ' + str(idxoverlord66)
                        if idxoverlord66 not in missing_overlord66:
                             missing_overlord66.append(idxoverlord66)
            idxlord66 = values[8]
            if idxlord66 in missing_lord66:
                continue
            if idxlord66 is not None:
                if (idxlord66 not in unique_names):
                    match_found = False
                    for potential_match in match_names:
                       if idxlord66==potential_match['matchidx']:
                           idxlord66=potential_match['unique']
                           match_found = True
                           break
                    if not match_found:
                       #missing_lord66.append(idxlord66)
                       if idxlord66 not in missing_lord66:
                            missing_lord66.append(idxlord66)
            if idxlord66:
                sql_string = "SELECT manor_id from domes_manor_lord66 WHERE manor_id="
                sql_string += structidx + " AND person_id=" + idxlord66 + ";"
                cursor.execute(sql_string)
                if not cursor.fetchall():
                    sql_string = "INSERT INTO domes_manor_lord66 (manor_id, person_id) VALUES ("
                    sql_string += structidx + ", " + idxlord66 + ");"
                    cursor.execute(sql_string)
            if idxoverlord66:
                sql_string = "SELECT manor_id from domes_manor_overlord66 WHERE manor_id="
                sql_string += structidx + " AND person_id=" + idxoverlord66 + ";"
                cursor.execute(sql_string)
                if not cursor.fetchall():
                    sql_string = "INSERT INTO domes_manor_overlord66 (manor_id, person_id) VALUES ("
                    sql_string += structidx + ", " + idxoverlord66 + ");"
                    cursor.execute(sql_string)
    print "missing lord66s", missing_lord66
    print "missing overlord66s", missing_overlord66
    conn.commit()

###############################
# TRWOwners
###############################
demesne_code = {
'Y': 'Held by the tenant-in-chief', 
'y': 'Held by the tenant-in-chief', 
'N': 'Subinfeudated', 
'E': 'Escheated',
'F': 'Farmed royal manor',
None:None
}
def get_trwowners():
    print "get_trwowners()"
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TRWForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_manor_lord86;')
    cursor.execute('delete from domes_manor_teninchief;')
    unique_names, match_names = util.get_unique_names()
    missing_lord86 = [None, '140050', '150500', '258850', '278150', '298890',\
         '322550', '373650', '39050', '405550', '414040', '519750', '554950',\
         '62450', '85555', '92360']
    missing_teninchief = [None, '10350', '10400', '106500', '106550', \
         '141150', '183350', '20150', '239550', '287950', '288050', '352600',\
         '425400', '440530', '444200', '501850', '519750', '82260', '85600',\
         '92360']
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:   
            values = util.line_to_values(line,15)
            trw_id = values[0]
            structidx = values[1]
            #demesne86 = util.postgres_escape(demesne_code[values[7]])
            idxteninchief = values[13]
            if idxteninchief in missing_teninchief:
                continue
            if idxteninchief not in unique_names:
                match_found = False
                for potential_match in match_names:
                   if idxteninchief==potential_match['matchidx']:
                       idxteninchief=potential_match['unique']
                       match_found = True
                       break
                if not match_found:
                    if idxteninchief not in missing_teninchief:
                        missing_teninchief.append(idxteninchief)
            idxlord86 = values[14]
            if idxlord86 in missing_lord86:
                continue
            if (idxlord86 not in unique_names):
                match_found = False
                for potential_match in match_names:
                   if idxlord86==potential_match['matchidx']:
                       idxlord86=potential_match['unique']
                       match_found = True
                       break
                if not match_found:
                    if idxlord86 not in missing_lord86:
                        missing_lord86.append(idxlord86)
            if idxlord86:
                sql_string = "SELECT manor_id from domes_manor_lord86 WHERE manor_id="
                sql_string += structidx + " AND person_id=" + idxlord86 + ";"
                cursor.execute(sql_string)
                if not cursor.fetchall():
                    sql_string = "INSERT INTO domes_manor_lord86 (manor_id, person_id) VALUES ("
                    sql_string += structidx + ", " + idxlord86 + ");"
                    cursor.execute(sql_string)
            if idxteninchief:
                sql_string = "SELECT manor_id from domes_manor_teninchief WHERE manor_id="
                sql_string += structidx + " AND person_id=" + idxteninchief + ";"
                cursor.execute(sql_string)
                if not cursor.fetchall():
                    sql_string = "INSERT INTO domes_manor_teninchief (manor_id, person_id) VALUES ("
                    sql_string += structidx + ", " + idxteninchief + ");"
                    cursor.execute(sql_string)
    print "missing lord86s", missing_lord86
    print "missing teninchiefs", missing_teninchief
    conn.commit()

###############################
# Images
###############################
def get_images():
    print 'get_images()'
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ImagesForAHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    # clear any existing entries
    cursor.execute('delete from domes_image;')
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:   
            values = util.line_to_values(line,10)
            structidx = values[0]
            county = values[1]
            phillimore = util.postgres_escape(values[2])
            imagesub = util.postgres_escape(values[3])
            if not values[4]:
                continue
            image = util.postgres_escape(values[4].replace('\\', '/'))
            marked = util.postgres_escape(values[5])
            x1 = values[6]
            y1 = values[7]
            x2 = values[8]
            y2 = values[9]
            ld_file = None
            # don't add entries that don't have a corresponding manor id
            sql_string = 'SELECT COUNT(*) AS COUNT FROM domes_manor WHERE structidx=' + structidx
            cursor.execute(sql_string)
            count = cursor.fetchone()[0]
            if count > 0:
                sql_string = "INSERT INTO domes_image (manor_id,phillimore,imagesub,image,ld_file_id,"
                sql_string += "marked,x1,y1,x2,y2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql_string, (structidx,phillimore,imagesub,image,ld_file,marked,x1,y1,x2,y2))
    conn.commit()

def get_imagefiles():
    print 'get_imagefiles()'
    # For each file in these three directories
    # Create an ImageFile entry with relevant filename and county entries
    cursor.execute('delete from domes_imagefile;')
    for county in ['Ess','Nfk','Suf']:
        print "----------" + county + "----------" 
        current_dir = '/Users/anna/domesday/web/domesday/media/images/%s' % county
        for pathAndFilename in glob.iglob(os.path.join(current_dir, '*.png')):
            title, ext = os.path.splitext(os.path.basename(pathAndFilename)) 
            print title, ext
            new_filename = title.split("_")[-1] 
            new_filename = new_filename + ext
            if new_filename[0]=='0' and len(new_filename.split(".")[0])==3:
                new_filename = new_filename[1:]
            os.rename(pathAndFilename, os.path.join(current_dir, new_filename))
            raw_width, raw_height = Image.open(pathAndFilename).size
            sql_string = "INSERT INTO domes_imagefile (filename,county_id," + \
                            "raw_width,raw_height,is_complete) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql_string, (new_filename,county.upper(),raw_width,raw_height,False))
    conn.commit()
                
###############################
# Call all the functions...
###############################
# # Get places 
# get_counties()
#get_places() 
# get_manors() 
# get_livestock() 
#get_placerefs() 
 
# Get images
#get_images() 
get_imagefiles()

# Get people
#get_people() 
#get_peoplenotes() # incomplete
# get_treowners() 
# get_trwowners()

conn.commit()
cursor.close()
conn.close()

