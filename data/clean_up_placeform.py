# Go through the Placeform file and find items with more than one Place attached.
# Then find the related Place so we can figure out what the hell is going on.
import os
import util

def line_to_values(line):
    line = line.strip('\n')
    line = line.decode("mac_roman")
    line = line.encode("utf-8")
    line = line.replace('"','')
    line = line.strip('\r')
    line = line.strip('\"')
    values = line.split('\t')
    return values

fn = os.path.join(os.path.dirname(__file__), 'new_data/PlacesForAHRC.txt')
f = open(fn, 'r')
p_file_lines = f.readlines()

fn = os.path.join(os.path.dirname(__file__), 'new_data/PlaceFormForAHRC.txt')
f = open(fn, 'r')
pf_file_lines = f.readlines()

place_array = []

for (counter, line) in enumerate(p_file_lines):
    place_array.append(line)

f = open('PlaceFormsForAnalysis.txt','w') 
line_previous = ''
printed_first_line = False
counter = 0

for (counter, line) in enumerate(pf_file_lines):
    line = line.strip("\n")
    line = line.strip("\r")
    if line.split("\t")[1]=='1':
        line_previous = line
        printed_first_line = False
        continue
    else:
        # Ooh, we like this line *and* the previous line!
        if printed_first_line:
            print >>f, line
        else:
            # Look up the entry in the Places file, and then output some headers too.
            placeid = line.split("\t")[0]
            print placeid
            for place in place_array:
                if placeid==place.split("\t")[0]:
                    print >>f, "\n"
                    print >>f, "ENTRY IN PLACE"
                    print >>f, place
                    continue
            print >>f, "ENTRIES IN PLACEFORM"
            counter +=1
            print >>f, line_previous
            print >>f, line
            printed_first_line = True
        line_previous = line

print counter