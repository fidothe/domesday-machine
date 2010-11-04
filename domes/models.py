from django.db import models
from django.contrib.gis.db import models

####################################
# Place-related tables
####################################
class County(models.Model):
    short_code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)
    name_slug = models.SlugField()
    def __unicode__(self):
        return self.name

class Hundred(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_slug = models.SlugField()
    status = models.CharField(max_length=100, null=True, blank=True)
    def __unicode__(self):
        return self.name
    
# Place. From PlacesForAHRC.txt
class Place(models.Model):
    id = models.IntegerField(primary_key=True) 
    county = models.ForeignKey(County)
    phillimore = models.CharField(max_length=300, null=True, blank=True)
    hundred = models.ForeignKey(Hundred, null=True)
    vill = models.CharField(max_length=300)
    vill_slug = models.SlugField()
    area = models.CharField(max_length=300, null=True, blank=True)
    xrefs = models.CharField(max_length=300, null=True, blank=True)
    grid = models.CharField(max_length=120, null=True, blank=True) # OS grid ref
    os_codes = models.CharField(max_length=120, null=True, blank=True) # 'uncertain', etc
    location = models.PointField(null=True, blank=True)
    objects = models.GeoManager()
    status = models.CharField(max_length=100, null=True, blank=True)
    def __unicode__(self):
        return self.vill
    @property
    def value(self):
        manors = Manor.objects.filter(place__id=self.id)
        total = {}
        for manor in manors:
            if not manor.geld:
                 continue
            if manor.gcode in total.keys():
                 total[manor.gcode] += manor.geld
            else:
                 total[manor.gcode] = manor.geld
        return total
    @property
    def raw_value(self):
        manors = Manor.objects.filter(place__id=self.id)
        total = 0.0
        for manor in manors:
            if manor.geld:
                total += manor.geld
        return total
    
####################################
# People-related tables
####################################

# People. From UniqueNames.txt, generated from NamesForAHRC.txt
class Person(models.Model):
    namesidx = models.IntegerField(primary_key=True, verbose_name="ID") # these map to LordIdx etc
    name = models.CharField(max_length=300, verbose_name="Name")     
    name_slug = models.SlugField()        
    namecode = models.CharField(max_length=5, null=True, blank=True, verbose_name="Name code")  
    gendercode = models.CharField(max_length=10, null=True, blank=True, verbose_name="Gender code")  
    churchcode = models.CharField(max_length=100, null=True, blank=True, verbose_name="Church code")  
    xrefs = models.CharField(max_length=300, null=True, blank=True, verbose_name="Cross-refs")
    def __unicode__(self):
        return self.name

####################################
# Manor-related tables
####################################
# Manors - a reference to a place in a Domesday entry.
# Everything hangs off this. From ManorsForAHRC.txt
class Manor(models.Model):
    structidx = models.IntegerField(primary_key=True)  
    place = models.ManyToManyField(Place, null=True, related_name="place")
    county = models.ForeignKey(County)  
    phillimore = models.CharField(max_length=100, null=True, blank=True, verbose_name="Phillimore") 
    headofmanor = models.CharField(max_length=100, null=True, blank=True, verbose_name="Head of manor [manorial centre of group, used for aggregating data]")
    duplicates = models.CharField(max_length=100, null=True, blank=True, verbose_name="Duplicates [code for entry duplicated in whole or in part elsewhere]")   
    subholdings = models.CharField(max_length=100, null=True, blank=True, verbose_name="Subholdings [subholdings whose data is aggregated with manorial totals (Y)]")   
    notes = models.CharField(max_length=400, null=True, blank=True, verbose_name="Notes [notes on problems with the data]")
    waste = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste [coded form of the formulae used to record waste]") 
    waste66 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste in 1066 [code for recorded waste for 1066: see Coding]")  
    wasteqr = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste circa 1070 [code for recorded waste, circa 1070: see Coding]")    
    waste86 = models.CharField(max_length=100, null=True, blank=True, verbose_name="Waste circa 1086 [code for recorded waste for 1086: see Coding]")
    geld = models.FloatField(null=True, blank=True, verbose_name="Geld [units liable for taxation and other public services in 1066 and 1086]")  
    gcode = models.CharField(max_length=100, null=True, blank=True, verbose_name="Gcode [code for variations in formulae in recording tax units]")  
    villtax = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Villtax [payment by vill when geld on the Hundred is 20 shillings (in old pence): Little Domesday on]") 
    taxedon = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Taxed on [assessment units on which tax is actually paid]")
    value86 = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value in 1086 [value of the holding to its lord in 1086]")  
    value66 = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value in 1066 [value of the holding to its lord in 1066]")  
    valueqr = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Value circa 1070  [value of the holding to its lord, circa 1070")   
    value_string = models.CharField(max_length=100, null=True, blank=True, verbose_name="Values [standardised form of the formulae used to record values: see Coding ]")    
    render = models.CharField(max_length=100, null=True, blank=True, verbose_name="Renders in addition [payment over and above the stated value of the holding]")   
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
    meadow = models.CharField(max_length=100, null=True, blank=True, verbose_name="Meadow [amount of meadow]")  
    meadowunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Meadow units [units in which meadow is recorded]")  
    pasture = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pasture [amount of pasture]")   
    pastureunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Pasture units [units in which pasture is recorded]")   
    woodland = models.CharField(max_length=100, null=True, blank=True, verbose_name="Woodland [amount of woodland]")    
    woodlandunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Woodland units [units in which woodland is recorded]")    
    fisheries = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Fisheries [number of fisheries, fishponds]")  
    salthouses = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Salthouses [number of salt-houses]") 
    payments = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Payments [total of payments other than mills for 1086 not included in the valuation]") 
    paymentsunits = models.CharField(max_length=100, null=True, blank=True, verbose_name="Payment units [total of payments other than mills for 1086 not included in the valuation]")   
    churches = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Churches [total of payments other than mills for 1086 not included in the valuation]") 
    churchland = models.FloatField(max_length=100, null=True, blank=True, verbose_name="Churchland [land attached to church or priest]") 
    cobs_1086 = models.IntegerField(null=True, blank=True)  
    cobs_1066 = models.IntegerField(null=True, blank=True)  
    cattle_1086  = models.IntegerField(null=True, blank=True)  
    cattle_1066 = models.IntegerField(null=True, blank=True)  
    cows_1086 = models.IntegerField(null=True, blank=True)  
    cows_1066 = models.IntegerField(null=True, blank=True)  
    pigs_1086 = models.IntegerField(null=True, blank=True)  
    pigs_1066 = models.IntegerField(null=True, blank=True)  
    sheep_1086 = models.IntegerField(null=True, blank=True)  
    sheep_1066 = models.IntegerField(null=True, blank=True)  
    goats_1086  = models.IntegerField(null=True, blank=True)  
    goats_1066  = models.IntegerField(null=True, blank=True)  
    beehives_1086 = models.IntegerField(null=True, blank=True)  
    beehives_1066 = models.IntegerField(null=True, blank=True)  
    wild_mares_1086 = models.IntegerField(null=True, blank=True)  
    wild_mares_1066 = models.IntegerField(null=True, blank=True)  
    other_1086 = models.IntegerField(null=True, blank=True)  
    other_code_1086 = models.CharField(max_length=100, null=True, blank=True)  
    other_1066 = models.IntegerField(null=True, blank=True)  
    other_codes_1066 = models.CharField(max_length=100, null=True, blank=True)
    lord66 = models.ManyToManyField(Person, null=True, related_name="lord66")
    overlord66 = models.ManyToManyField(Person, null=True, related_name="overlord66")
    lord86 = models.ManyToManyField(Person, null=True, related_name="lord86")
    teninchief = models.ManyToManyField(Person, null=True, related_name="teninchief")
    def total_people(self):
        total_people = self.villagers + self.smallholders + self.slaves + self.femaleslaves \
            + self.freemen + self.free2men + self.priests \
            + self.cottagers + self.otherpop + self.miscpop + self.burgesses
        return total_people
    def has_ploughland(self):
        if (self.ploughlands or self.lordsploughs or self.lordsploughspossible \
            or self.mensploughs or self.mensploughspossible):
            return True
        return False
    def has_other_land(self):
        if (self.lordsland or self.newland or self.meadow or self.pasture \
            or self.woodland or self.mills or self.fisheries \
            or self.salthouses or self.churches or self.churchland):
            return True
        return False
    def has_livestock_1066(self):
        if (self.cobs_1066 or self.cattle_1066 or self.cows_1066 or self.pigs_1066 \
            or self.sheep_1066 or self.goats_1066 or self.beehives_1066 \
            or self.wild_mares_1066 or self.other_1066 or self.other_codes_1066):
            return True
        return False
    def has_livestock_1066(self):
        if (self.cobs_1086 or self.cattle_1086 or self.cows_1086 or self.pigs_1086 \
            or self.sheep_1086 or self.goats_1086 or self.beehives_1086 \
            or self.wild_mares_1086 or self.other_1086 or self.other_code_1086):
            return True
        return False  

# Place references - links Manors and Places. From ByPlaceForAHRC.txt
# class PlaceRef(models.Model):
#     manor = models.ForeignKey(Manor)
#     place = models.ForeignKey(Place)
#     holding = models.FloatField(null=True, blank=True)
#     units = models.CharField(max_length=100, null=True, blank=True)


################################################
# Image-related tables
################################################
class Image(models.Model):
    manor = models.ForeignKey(Manor)
    phillimore = models.CharField(max_length=100, null=True, blank=True)         
    imagesub = models.CharField(max_length=30, null=True, blank=True)  
    image = models.CharField(max_length=30, null=True, blank=True) #filename
    marked = models.CharField(max_length=30, null=True, blank=True)  
    x1 = models.IntegerField(null=True, blank=True)
    y1 = models.IntegerField(null=True, blank=True)
    x2 = models.IntegerField(null=True, blank=True)
    y2 = models.IntegerField(null=True, blank=True)
    def county(self):
       filepath = self.image.split("/")[0]
       county = County.objects.get(short_code__iexact=filepath)
       return county
    def fullnum(self): # image number with leading zeroes
       file_array = self.image.split("/")[1]
       file_array = file_array.split(".")[0]
       return file_array
    def filenum(self): # image number with no leading zeroes
       file_array = self.image.split("/")[1]
       file_array = file_array.split(".")[0]
       file_array = file_array.lstrip("0")
       return file_array

################################################
# Email addresses of interested people
################################################

class EmailSignup(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()

################################################
# Raw text - from the .rtf file, imported by
# Python script (not currently used, due to 
# copyright issues)
################################################

class RawText(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    text = models.CharField(max_length=5000)