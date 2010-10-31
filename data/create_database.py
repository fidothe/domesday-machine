##############################################################
# Script to convert Domesday tab-separated files to SQL
# BEWARE! - will OVERWRITE your existing database
##############################################################
import county_dict
import json
#import MySQLdb
#import MySQLdb.cursors
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

###############################
# Places
###############################

def get_counties():
    print "get_counties()"	
    cursor.execute('delete from domes_county;')
    for key,value in county_dict.county_dict.items():
           sql_string = "INSERT INTO domes_county (short_code,name) VALUES (%s,%s) "
           cursor.execute(sql_string, (key,value))
    conn.commit()
	
def get_places():
    print "get_places()"
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
           county = values[1]
           if not county: # TODO: check this
               continue
           else:
               county = util.postgres_escape(county, False)
           phillimore = util.postgres_escape(values[2], False)
           hundred = util.postgres_escape(values[3], False)
           vill = values[4]
           # `' = place no longer exists but can be identified on ground 
           # [] name inside brackets = lost, only approximately located
           if vill=="" or not vill:
                continue
           if vill[0]=="`":
                pass
           vill_slug = slugify(vill)[:49]
           vill = util.postgres_escape(vill, False)
           area = util.postgres_escape(values[5], False)
           xrefs = util.postgres_escape(values[6], False)
           grid = util.postgres_escape(values[7], False)
           os_codes = util.postgres_escape(values[8], False)
           if grid!="NULL" and grid!=None:
               location = util.convert_os_to_coords(grid.strip("'"))
           sql_string = "INSERT INTO domes_place (id,county_id,phillimore,hundred,"
           sql_string += "vill,vill_slug,area,xrefs,grid,os_codes,location) VALUES ("
           sql_string += id + ", " + county + ", " + phillimore + ", " + hundred + ", "
           sql_string += vill + ", '" + vill_slug + "', " + area + ", " + xrefs + ", "
           sql_string += grid + ", " + os_codes + ", " + location + ");"
           cursor.execute(sql_string)
    conn.commit()

	#INSERT INTO domes_place (id,county_id,phillimore,hundred,vill,vill_slug,area,xrefs,grid,os_codes,location) VALUES
###############################
# Place references
###############################
def get_placerefs():
    print "get_placerefs()"
    # open tab file
    fn = os.path.join(os.path.dirname(__file__), 'new_data/ByPlace For AHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_placeref;')
    # get values from tab file 
    for (counter, line) in enumerate(file_lines): 
           if counter==0:
               continue
           values = util.line_to_values(line,13)
           manor_id = values[1]
           holding = values[9]
           units = util.postgres_escape(values[10])
           place_id = values[12]
           if not place_id:
               continue
           sql_string = "INSERT INTO domes_placeref (manor_id, place_id, holding, units) "
           sql_string += "VALUES (%s,%s,%s,%s)"
           cursor.execute(sql_string, (manor_id, place_id, holding, units))
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
            # print sql_string % (structidx,county,phillimore,headofmanor,duplicates,subholdings,notes,\
            #               waste,waste66,wasteqr,waste86,geld,gcode,villtax,\
            #               taxedon,value86,value66,valueqr,value_string,render,lordsland,\
            #               newland,ploughlands,pcode,lordsploughs,mensploughs,totalploughs,lordsploughspossible, \
            #               mensploughspossible,totalploughspossible,villagers,smallholders,slaves,femaleslaves,freemen, \
            #               free2men,priests,cottagers,otherpop,miscpop,miscpopcategories,burgesses,\
            #               mills,millvalue,meadow,meadowunits,pasture,pastureunits,woodland,\
            #               woodlandunits,fisheries,salthouses,payments,paymentsunits,churches,churchland)
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
gender_codes = {
'M': 'Male',
'm': 'Male',
'F': 'Female',
None:None,
'i':'i' 
#155860 "Durham (St Cuthbert), monks of"    "LIN"   "3,4"       "i" "a" - Ask JP about this
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
                print xrefs
                xrefs1 = xrefs.decode("utf-8")
            xrefs = util.postgres_escape(xrefs1)
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
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TRE For AHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_treowner;')
    unique_names, match_names = util.get_unique_names()
    missing_lord66 =  ['62450', '272000', '495170', '252200', '120810', '476750', '576050', '399450', '382300', '431700', '23350', '23300', '85500', '114700', '165150', '48700', '171720', '397560', '156850', '185950', '524260', '519100', '167070', '532050', '120750', '372010', '126950', '259390']
    missing_overlord66 = ['50830', '159250', '344670', '574150', '50650', '156850', '532050', '530050', '160400', '126950', '259390', '259380', '344560']
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:   
            values = util.line_to_values(line,14)
            tre_id = values[0]
            structidx = values[1]
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
                    #print 'idxlord66 not in unique_names'
                    match_found = False
                    for potential_match in match_names:
                       if idxlord66==potential_match['matchidx']:
                           idxlord66=potential_match['unique']
                           match_found = True
                           break
                    if not match_found:
                       #print 'match not found for idxlord66 ' + str(idxlord66)
                       #missing_lord66.append(idxlord66)
                       if idxlord66 not in missing_lord66:
                            missing_lord66.append(idxlord66)
            sql_string = "INSERT INTO domes_treowner (tre_id,manor_id, " 
            sql_string += "overlord66_id,lord66_id) VALUES (%s,%s,%s,%s)" 
            cursor.execute(sql_string, (tre_id,structidx,idxoverlord66,idxlord66))
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
    fn = os.path.join(os.path.dirname(__file__), 'new_data/TRW For AHRC.txt')
    f = open(fn, 'r')
    file_lines = f.readlines()
    cursor.execute('delete from domes_trwowner;')
    unique_names, match_names = util.get_unique_names()
    missing_teninchief = []
    missing_lord86 = []
    for (counter, line) in enumerate(file_lines): 
        if counter == 0:
            continue
        else:   
            values = util.line_to_values(line,15)
            trw_id = values[0]
            structidx = values[1]
            demesne86 = util.postgres_escape(demesne_code[values[7]])
            idxteninchief = values[13]
            if idxteninchief in missing_teninchief:
                continue
            if idxteninchief!='305150':
                continue # Text with this one, which is not found in unique_names
            print 'idxteninchief is ' + str(idxteninchief)
            if (idxteninchief not in unique_names):
                print 'idxteninchief not in unique_names'
                match_found = False
                for potential_match in match_names:
                   if idxteninchief==potential_match['matchidx']:
                       #print 'found potential match!'
                       idxteninchief=potential_match['unique']
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
                       break
                if not match_found:
                    if idxlord86 not in missing_lord86:
                        missing_lord86.append(idxlord86)
            sql_string = "INSERT INTO domes_trwowner (trw_id,manor_id,demesne86,"
            sql_string += "teninchief_id,lord86_id) VALUES (%s,%s,%s,%s,%s)"
            cursor.execute(sql_string, (trw_id,structidx,demesne86,idxteninchief,idxlord86))
    print "missing lord86s", missing_lord86
    print "missing teninchiefs", missing_teninchief
    conn.commit()

###############################
# Images
###############################
def get_images():
    print 'get_images()'
    fn = os.path.join(os.path.dirname(__file__), 'new_data/Images For AHRC.txt')
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
            # don't add entries that don't have a corresponding manor id
            sql_string = 'SELECT COUNT(*) AS COUNT FROM domes_manor WHERE structidx=' + structidx
            cursor.execute(sql_string)
            count = cursor.fetchone()[0]
            if count > 0:
                sql_string = "INSERT INTO domes_image (manor_id,phillimore,imagesub,image,"
                sql_string += "marked,x1,y1,x2,y2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor.execute(sql_string, (structidx,phillimore,imagesub,image,marked,x1,y1,x2,y2))
    conn.commit()
                
###############################
# Call all the functions...
###############################
# Get places 
get_counties()
get_places() # fails

get_manors() # works
get_livestock() # works
get_placerefs() # dependent on places

# Get images
get_images() # problem of missing structidxs! ???

# Get people
get_people() # works
#get_peoplenotes() # incomplete
get_treowners() # works
get_trwowners() # 

conn.commit()
cursor.close()
conn.close()

