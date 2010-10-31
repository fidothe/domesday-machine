##############################################################
# Turning NamesForAHRC into a unique list of people
# Acard (of Ivry) is the same as Acard of Ivry 
# Create a bridging table between UniqueNames and NamesIdx's
# We'll use this in TREOwners and TRWOwners
##############################################################
import os, sys
import util

names_in = os.path.join(os.path.dirname(__file__), 'new_data/NamesForAHRC.txt')
names_file = open(names_in, 'r')
file_lines = names_file.readlines()
unique_people = []
name_matches = []
print len(file_lines)-1," lines in file"
for (counter, line) in enumerate(file_lines): 
    if counter == 0:
        continue
    else:
        values = util.line_to_values(line,8)
        row = []
        probable = False
        row.append(values[0]) #NamesIdx
        if (c in values[1] for c in '(){}<>'): # only a probable match if any of these chars are there
            probable = True
        stripped_name = values[1].replace("(", "").replace(")", "").replace("{", "").replace("}", "").replace("<", "").replace(">", "")
        row.append(stripped_name) #Name
        # (ditch phillimore and county refs, in cols 2 and 3)
        row.append(values[4]) #NameCode
        row.append(values[5]) #GenderCode
        row.append(values[6]) #ChurchCode
        row.append(values[7]) #Xrefs
        match_found = False
        #print 'looking up ' + name
        for d in unique_people: # unique names already found
            if (stripped_name==d[1] and row[3]==d[3]): #check for identical (stripped) name and gender
                match_found = True
                #print name + ' is already listed'
                name_match = []
                # this person is already listed in all_values: add to our bridging table
                name_match.append(d[0].decode("utf-8").encode("mac_roman"))
                name_match.append(row[0].decode("utf-8").encode("mac_roman"))
                name_matches.append(name_match)
        if match_found is False:
            #print 'adding ' + name
            decoded_row = []
            for d in row:
                decoded_row.append(d.decode("utf-8").encode("mac_roman"))
            unique_people.append(decoded_row)
            
print len(unique_people)," unique names found"
print len(name_matches)," matches found"

unique_names_path = os.path.join(os.path.dirname(__file__), 'new_data/UniqueNames.txt')
name_matches_path = os.path.join(os.path.dirname(__file__), 'new_data/NameMatches.txt')

unique_names_file = open(unique_names_path, 'w')
unique_names_file.write('NamesIdx\tName\tNameCode\tGenderCode\tChurchCode\tXrefs\n')
unique_names_file.writelines('\t'.join(i) + '\n' for i in unique_people)   

name_matches_file = open(name_matches_path, 'w')
name_matches_file.write('UniqueNameIdx\tNameIdx\n')
name_matches_file.writelines('\t'.join(i) + '\n' for i in name_matches)

names_file.close()
name_matches_file.close()
unique_names_file.close()
