from psycopg2.extensions import adapt  
import osgb
import os
import sys

# most of our functions use 
def postgres_escape(string_value, inbuilt_escaping=True):
    string_value = str(adapt(string_value))
    if inbuilt_escaping: 
        string_value = string_value.strip("'")
        if string_value=="NULL":
            string_value = None
    return string_value

# deal with lines that end too soon
def add_trailing_tabs(values, length):
    if len(values) < length:
        extra_values = length - len(values)
        for i in range(0, extra_values):
            values.append('')
    return values

# convert tab-separated line into standard array
# sort encoding, strip quotes and newline chars
def line_to_values(line, length):
    line = line.strip('\n')
    line = line.decode("mac_roman")
    line = line.encode("utf-8")
    line = line.replace('"','')
    line = line.strip('\r')
    line = line.strip('\"')
    values = line.split('\t')
    values = add_trailing_tabs(values, length)  
    new_values = []
    for value in values:
        value = value.strip()
        if value=="" or value=="-" or value=="NULL" or value=="--" \
           or value=="?" or value=="??" or value=="???"\
           or value=="--" or value=='null':
            value = None 
        new_values.append(value)   
    return new_values
    
# convert OS code into Geodjango-friendly string
def convert_os_to_coords(oscode):
    lon, lat = osgb.osgb_to_lonlat(oscode)
    value_string = "ST_GeomFromText('POINT(" + str(lon) + " " + str(lat) + ")',4326)"
    return value_string

def get_unique_names():
    # load up our list of unique and matching names
    fn_unique = os.path.join(os.path.dirname(__file__), 'new_data/UniqueNames.txt')
    fn_matches = os.path.join(os.path.dirname(__file__), 'new_data/NameMatches.txt')
    file_unique = open(fn_unique, 'r')
    lines_unique = file_unique.readlines()
    file_matches = open(fn_matches, 'r')
    lines_matches = file_matches.readlines()
    # list of all unique IDs
    unique_names = []
    # list of all matched names and IDs
    match_names = []
    for (counter, line) in enumerate(lines_unique): 
        if counter == 0:
            continue
        line = line.split("\t")
        unique = line[0]
        unique_names.append(unique)
    for (counter, line) in enumerate(lines_matches): 
        if counter == 0:
            continue
        match = {}
        line = line.strip("\n")
        line = line.split("\t")
        match['unique'] = line[0]
        match['matchidx'] = line[1]
        match_names.append(match)
    print 'found ' + str(len(unique_names)) + " unique names and " + str(len(match_names)) + " matching names"
    #sys.exit()
    return unique_names, match_names