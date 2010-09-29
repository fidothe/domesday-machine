from django.db import models
from django.contrib.gis.db import models

####################################
# Place-related tables
####################################

# Place - the basic unit. From PlacesForAHRC.txt
class Place(models.Model):
    placeidx = models.IntegerField(primary_key=True) 
    county = models.CharField(max_length=36, null=True, blank=True)
    phillimore = models.CharField(max_length=300, null=True, blank=True)
    hundred = models.CharField(max_length=300, null=True, blank=True)
    vill = models.CharField(max_length=300, null=True, blank=True)
    vill_slug = models.SlugField(null=True, blank=True)
    area = models.CharField(max_length=300, null=True, blank=True)
    xrefs = models.CharField(max_length=300, null=True, blank=True)
    os_refs = models.CharField(max_length=120, null=True, blank=True) # OS grid ref
    os_codes = models.CharField(max_length=120, null=True, blank=True) # 'uncertain', etc
    location = models.PointField(null=True, blank=True)
    objects = models.GeoManager()
    
# Place references - links Manors and Places. From ByPlaceForAHRC.txt
class PlaceRef(models.Model):
    structidx = models.IntegerField() 
    placeidx = models.IntegerField() 
    holding = models.FloatField(null=True, blank=True)
    units = models.CharField(max_length=20, null=True, blank=True)  

# Manors. Stats for population & value. From ManorsForAHRC.txt
class Manor(models.Model):
    structidx = models.IntegerField(primary_key=True)    
    county = models.CharField(max_length=30, null=True, blank=True, verbose_name="County")   
    phillimore = models.CharField(max_length=100, null=True, blank=True, verbose_name="Phillimore") 
    headofmanor = models.CharField(max_length=100, null=True, blank=True, verbose_name="Head of manor [manorial centre of group, used for aggregating data]")   
    geld = models.FloatField(null=True, blank=True, verbose_name="Geld [units liable for taxation and other public services in 1066 and 1086]")  
    gcode = models.CharField(max_length=100, null=True, blank=True, verbose_name="Gcode [code for variations in formulae in recording tax units]")  
    villtax = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Villtax [payment by vill when geld on the Hundred is 20 shillings (in old pence): Little Domesday on]") 
    taxedon = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Taxed on [assessment units on which tax is actually paid]")
    lordsland = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Lords land [tax units on the lord's demesne: 'lordship hides']") 
    newland = models.FloatField(max_length=100, null=True, blank=True, verbose_name="New land [additional, unassessed carucates or hides, often described as 'inland' or as carucates in non-carucated areas]")  
    ploughlands = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Ploughlands ['Land for' so many ploughs, often interpreted as the area of arable land, sometimes as a new tax assessment]") 
    pcode = models.CharField(max_length=100, null=True, blank=True, verbose_name="Code [code for variations in formulae in recording ploughland data: see Coding]") 
    lordsploughs = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Lords' ploughs [number of ploughteams attributed to the lord of the manor, the teams assumed to comprise 8 oxen]") 
    mensploughs = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Mens' ploughs [number of ploughteams attributed to the men on the manor, the teams assumed to comprise 8 oxen]")    
    totalploughs = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Total ploughs [total number of ploughteams attributed to the holding]")    
    lordsploughspossible = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Lords' ploughs possible [additional number of lord's ploughteams needed to bring the estate to full working capacity]")    
    mensploughspossible = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Mens' ploughs possible [additional number of men's ploughteams needed to bring the estate to full working capacity]")   
    totalploughspossible = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Total ploughs possible [total number of additional ploughteams needed to bring the estate to full working capacity]")  
    villagers = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Villagers [number of villagers (villeins) on the holding]")   
    smallholders = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Smallholders [number of smallholders (bordars) on the holding]")   
    slaves = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Male slaves [number of male slaves on the holding]") 
    femaleslaves = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Female slaves [number of female slaves on the holding]")   
    freemen = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Freemen [number of Freemen (sokemen) on the holding]")  
    free2men = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Free men [number of free men (liberi homines) on the holding]")    
    priests = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Priests [number of priests on the holding]")    
    cottagers = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Cottagers [number of cottagers on the holding (cottagers with small 'c'  in Phillimore)]")    
    otherpop = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Other population [number of any major population group confined to a few counties (eg, pigmen in Devon)]") 
    miscpop = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Miscellaneous population [miscellaneous population not recorded among groups with separate data fields]")   
    miscpopcategories = models.CharField(max_length=100, null=True, blank=True, verbose_name="Misc. pop. categories [categories of miscellaneous population recorded in MiscPop field]")    
    burgesses = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Burgesses [number of burgesses among the urban or rural population]") 
    mills = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Mills [number of mills on the holding]")  
    millvalue = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Mill value [value of mills on the holding]")  
    meadow = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Meadow [amount of meadow]")  
    meadowunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Meadow units [units in which meadow is recorded]")  
    pasture = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Pasture [amount of pasture]")   
    pastureunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pasture units [units in which pasture is recorded]")   
    woodland = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Woodland [amount of woodland]")    
    woodlandunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Woodland units [units in which woodland is recorded]")    
    fisheries = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Fisheries [number of fisheries, fishponds]")  
    salthouses = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Salthouses [number of salt-houses]") 
    payments = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Payments [total of payments other than mills for 1086 not included in the valuation]") 
    paymentsunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Payment units [total of payments other than mills for 1086 not included in the valuation]")   
    churches = models.CharField(max_length=100, null=True, blank=True, verbose_name="Churches [total of payments other than mills for 1086 not included in the valuation]") 
    churchland = models.CharField(max_length=100, null=True, blank=True, verbose_name="Churchland [land attached to church or priest]") 
    value86 = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value in 1086 [value of the holding to its lord in 1086]")  
    value66 = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value in 1066 [value of the holding to its lord in 1066]")  
    valueqr = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value circa 1070  [value of the holding to its lord, circa 1070")   
    value_string = models.CharField(max_length=100, null=True, blank=True, verbose_name="Values [standardised form of the formulae used to record values: see Coding ]")    
    render = models.CharField(max_length=100, null=True, blank=True, verbose_name="Renders in addition [payment over and above the stated value of the holding]")   
    waste = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste [coded form of the formulae used to record waste]") 
    waste66 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste in 1066 [code for recorded waste for 1066: see Coding]")  
    wasteqr = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste circa 1070 [code for recorded waste, circa 1070: see Coding]")    
    waste86 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste circa 1086 [code for recorded waste for 1086: see Coding]")
    duplicates = models.CharField(max_length=100, null=True, blank=True, verbose_name="Duplicates [code for entry duplicated in whole or in part elsewhere]")   
    subholdings = models.CharField(max_length=100, null=True, blank=True, verbose_name="Subholdings [subholdings whose data is aggregated with manorial totals (Y)]")   
    notes = models.CharField(max_length=400, null=True, blank=True, verbose_name="Notes [notes on problems with the data]")
    def get_interesting_queryset(self):
        for field in Manors._meta.fields:
            if field.value_to_string(self) is None or field.value_to_string(self) == "N" or field.value_to_string(self) == "0" or field.value_to_string(self) == "-" or field.value_to_string(self) == "X" or field.value_to_string(self) == "":
                delattr(self, str(field.name))
        return self
    def other_vills(self):
        other_vills = Place.objects.filter(structidx=self.structidx).order_by('vill')
        return other_vills
    def total_population(self):
        population = (int(self.villagers) + int(self.smallholders) + int(self.slaves) + int(self.femaleslaves) + 
                      int(self.freemen) + int(self.free2men) + int(self.priests) + int(self.cottagers) + int(self.otherpop) + 
                      int(self.miscpop) + int(self.burgesses))
        return population

####################################
# People-related tables
####################################
# Owner in 1066. TREForAHRC.txt
class TreOwners(models.Model):
    tre_id = models.IntegerField(primary_key=True)
    structidx = models.IntegerField()
    subidx = models.IntegerField()
    county = models.CharField(max_length=36, null=True, blank=True)
    phillimore = models.CharField(max_length=300, null=True, blank=True)
    overlord66 = models.CharField(max_length=300, null=True, blank=True, verbose_name="Overlord in 1066")
    lord66 = models.CharField(max_length=300, null=True, blank=True, verbose_name="Lord in 1066")
    idxoverlord66 = models.CharField(max_length=300, null=True, blank=True)
    idxlord66 = models.CharField(max_length=300, null=True, blank=True)
    holding = models.FloatField(null=True, blank=True)
    units = models.CharField(max_length=120, null=True, blank=True)
    value66 = models.FloatField(null=True, blank=True)
    value66qr86 = models.FloatField(null=True, blank=True)
    v66code = models.CharField(max_length=120, null=True, blank=True)
    def get_places(self):
        places = Place.objects.filter(structidx=self.structidx).exclude(vill="-").order_by('vill')
        return places
    def get_fields(self):
        return [(field.verbose_name, field.value_to_string(self)) for field in TreOwners._meta.fields]
    def get_interesting_queryset(self):
        for field in Manors._meta.fields:
            if field.value_to_string(self) is None or field.value_to_string(self) == "N" or field.value_to_string(self) == "0" or field.value_to_string(self) == "-" or field.value_to_string(self) == "X" or field.value_to_string(self) == "":
                delattr(self, str(field.name))
        return self

# Owner in 1086. From TREForAHRC.txt
class TrwOwners(models.Model):
    trw_id = models.IntegerField(primary_key=True)
    structidx = models.IntegerField(null=True, blank=True)
    subidx = models.IntegerField(null=True, blank=True)
    county = models.CharField(max_length=36, null=True, blank=True)
    phillimore = models.CharField(max_length=300, null=True, blank=True)
    teninchief = models.CharField(max_length=300, null=True, blank=True, verbose_name="Tenant-in-chief in 1066")
    lord86 = models.CharField(max_length=300, null=True, blank=True, verbose_name="Lord in 1086")
    demesne86 = models.CharField(max_length=300, null=True, blank=True)
    holding = models.CharField(max_length=300, null=True, blank=True)
    units = models.CharField(max_length=120, null=True, blank=True)
    value86 = models.CharField(max_length=120, null=True, blank=True)
    v86code = models.CharField(max_length=120, null=True, blank=True)
    waste86 = models.CharField(max_length=120, null=True, blank=True)
    idxTinC = models.CharField(max_length=120, null=True, blank=True)
    idxLord86 = models.CharField(max_length=120, null=True, blank=True)
    def get_places(self):
        places = Place.objects.filter(structidx=self.structidx).exclude(vill="-").order_by('vill')
        return places
    def get_all_fields(self):
        return [(field.verbose_name, field.value_to_string(self)) for field in TrwOwners._meta.fields]
    def get_fields(self):
        interesting_fields = []
        interesting_fields.append((str(self.lord86.verbose_name).rstrip(), self.lord86.value_to_string))
        return interesting_fields
    def get_interesting_queryset(self):
        for field in Manors._meta.fields:
            if field.value_to_string(self) is None or field.value_to_string(self) == "N" or field.value_to_string(self) == "0" or field.value_to_string(self) == "-" or field.value_to_string(self) == "X" or field.value_to_string(self) == "":
                delattr(self, str(field.name))
        return self

##  Livestock. From domesdaystatistics_livestock.tab 
# class Livestock(models.Model):
#     structidx = models.IntegerField()
#     county = models.CharField(max_length=36, null=True, blank=True)
#     phillimore = models.CharField(max_length=300, null=True, blank=True)
#     cobs_1086 = models.IntegerField(null=True, blank=True)  
#     cobs_1066 = models.IntegerField(null=True, blank=True)  
#     cattle_1086 = models.IntegerField(null=True, blank=True)    
#     cattle_1066 = models.IntegerField(null=True, blank=True)    
#     cows_1086 = models.IntegerField(null=True, blank=True)  
#     cows_1066 = models.IntegerField(null=True, blank=True)  
#     pigs_1086 = models.IntegerField(null=True, blank=True)  
#     pigs_1066 = models.IntegerField(null=True, blank=True)  
#     sheep_1086 = models.IntegerField(null=True, blank=True) 
#     sheep_1066 = models.IntegerField(null=True, blank=True) 
#     goats_1086 = models.IntegerField(null=True, blank=True) 
#     goats_1066 = models.IntegerField(null=True, blank=True) 
#     beehives_1086 = models.IntegerField(null=True, blank=True)  
#     beehives_1066 = models.IntegerField(null=True, blank=True)  
#     wild_mares_1086 = models.IntegerField(null=True, blank=True)    
#     wild_mares_1066 = models.IntegerField(null=True, blank=True)    
#     other_1086 = models.CharField(max_length=120, null=True, blank=True)    
#     other_code_1086 = models.CharField(max_length=120, null=True, blank=True)   
#     other_1066 = models.CharField(max_length=120, null=True, blank=True)    
#     other_codes_1066 = models.CharField(max_length=120, null=True, blank=True)
         
# # County statistics - from domesdaystatistics_totals_query.tab
# class County(models.Model):
#     short_code = models.CharField(max_length=120, primary_key=True)    
#     geld = models.CharField(max_length=120, null=True, blank=True)  
#     land = models.CharField(max_length=120, null=True, blank=True)  
#     lordsploughs = models.CharField(max_length=120, null=True, blank=True)  
#     mensploughs = models.CharField(max_length=120, null=True, blank=True)   
#     totalploughs = models.CharField(max_length=120, null=True, blank=True)  
#     villagers = models.CharField(max_length=120, null=True, blank=True) 
#     smallholders = models.CharField(max_length=120, null=True, blank=True)  
#     slaves = models.CharField(max_length=120, null=True, blank=True)    
#     ancill = models.CharField(max_length=120, null=True, blank=True)    
#     freemen = models.CharField(max_length=120, null=True, blank=True)   
#     free_men = models.CharField(max_length=120, null=True, blank=True)  
#     priests = models.CharField(max_length=120, null=True, blank=True)   
#     cotts = models.CharField(max_length=120, null=True, blank=True) 
#     burgesses = models.CharField(max_length=120, null=True, blank=True) 
#     other = models.CharField(max_length=120, null=True, blank=True) 
#     misc = models.CharField(max_length=120, null=True, blank=True)  
#     mills = models.CharField(max_length=120, null=True, blank=True) 
#     mvalue = models.CharField(max_length=120, null=True, blank=True)    
#     val66 = models.CharField(max_length=120, null=True, blank=True) 
#     valqr = models.CharField(max_length=120, null=True, blank=True) 
#     val86 = models.CharField(max_length=120, null=True, blank=True) 
#     churches = models.CharField(max_length=120, null=True, blank=True)  
#     chland = models.CharField(max_length=120, null=True, blank=True)
#     name = models.CharField(max_length=120, null=True, blank=True) 
#     circuit = models.IntegerField(null=True, blank=True)
# 
#     def places(self):
#         places = Place.objects.filter(county__exact=self.short_code).order_by('vill')
#         return places

# Names
class Name(models.Model):
    namesidx = models.IntegerField(primary_key=True, verbose_name="ID") # these map to LordIdx etc
    name = models.CharField(max_length=100, null=True, blank=True, verbose_name="Name")     
    county = models.CharField(max_length=36, null=True, blank=True, verbose_name="County")   
    phillimore = models.CharField(max_length=1000, null=True, blank=True, verbose_name="Phillimore")         
    namecode = models.CharField(max_length=5, null=True, blank=True, verbose_name="Name code")  
    gendercode = models.CharField(max_length=5, null=True, blank=True, verbose_name="Gender code")  
    churchcode = models.CharField(max_length=5, null=True, blank=True, verbose_name="Church code")  
    xrefs = models.CharField(max_length=5, null=True, blank=True, verbose_name="Cross-refs")
    def churchtype(self):
        churchtype = ChurchCode.objects.filter(short_code__exact=self.churchcode)
        return churchtype.name

class ChurchCode(models.Model):
    short_code = models.CharField(max_length=1, primary_key=True)
    name = models.CharField(max_length=50)

################################################
# Images
################################################

class Image(models.Model):
    structidx = models.IntegerField() 
    county = models.CharField(max_length=36, null=True, blank=True)   
    phillimore = models.CharField(max_length=100, null=True, blank=True)         
    imagesub = models.CharField(max_length=30, null=True, blank=True)  
    image = models.CharField(max_length=30, null=True, blank=True) #filename
    marked = models.CharField(max_length=30, null=True, blank=True)  
    x1 = models.IntegerField(null=True, blank=True)
    y1 = models.IntegerField(null=True, blank=True)
    x2 = models.IntegerField(null=True, blank=True)
    y2 = models.IntegerField(null=True, blank=True)

################################################
# Email addresses of interested people
################################################

class EmailSignup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

################################################
# Raw text - from the .rtf file, imported by
# Python script (not currently used)
################################################

class RawText(models.Model):
           id = models.CharField(primary_key=True, max_length=100)
           text = models.CharField(max_length=5000)