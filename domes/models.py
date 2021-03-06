from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User

####################################
# Place-related tables
####################################
class County(models.Model):
    short_code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=100)
    name_slug = models.SlugField()
    def __unicode__(self):
        return self.name
    @models.permalink
    def get_absolute_url(self):
        return ('domes.views.county', (), {
            'county_slug': self.name_slug })
    
class Area(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_slug = models.SlugField()
    def __unicode__(self):
        return self.name
        
class Hundred(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    name_slug = models.SlugField()
    status = models.CharField(max_length=100, null=True, blank=True)
    def __unicode__(self):
        return self.name
    @models.permalink
    def get_absolute_url(self):
        return ('domes.views.hundred', (), {
            'hundred_slug': self.name_slug })
            
# Place. From PlacesForAHRC.txt
class Place(models.Model):
    id = models.IntegerField(primary_key=True) 
    county = models.ManyToManyField(County,related_name='county')
    area = models.ManyToManyField(Area,related_name='area')
    hundred = models.ForeignKey(Hundred, null=True)
    phillimore = models.CharField(max_length=300, null=True, blank=True)
    vill = models.CharField(max_length=300)
    vill_slug = models.SlugField()
    xrefs = models.CharField(max_length=300, null=True, blank=True)
    grid = models.CharField(max_length=120, null=True, blank=True) # OS grid ref
    os_codes = models.CharField(max_length=120, null=True, blank=True) # 'uncertain', etc
    location = models.PointField(null=True, blank=True)
    objects = models.GeoManager()
    status = models.CharField(max_length=100, null=True, blank=True)
    def __unicode__(self):
        return self.vill
    class Meta:
        ordering = ('hundred', 'vill')
    @property
    def value(self):
        manors = Manor.objects.filter(place__id=self.id)
        total = {}
        for manor in manors:
            if not manor.geld:
                 continue
            else:
                 manor_geld = manor.geld / manor.place.count()
            if manor.gcode in total.keys():
                 total[manor.gcode] += manor_geld
            else:
                 total[manor.gcode] = manor_geld
        return total
    @property
    def raw_value(self):
        manors = Manor.objects.filter(place__id=self.id)
        total = 0.0
        for manor in manors:
            manor_total = 0.0
            if manor.geld:
                manor_total += manor.geld
            manor_total = manor_total / manor.place.count()
            total += manor_total           
        return total
    @property
    def population(self):
        manors = Manor.objects.filter(place__id=self.id)
        people = 0.0
        for manor in manors:
            manor_people = 0.0
            people_types = [manor.villagers, manor.smallholders, manor.slaves,\
                        manor.femaleslaves, manor.freemen, manor.free2men,\
                        manor.priests, manor.cottagers, manor.otherpop,\
                        manor.miscpop, manor.burgesses]
            for p in people_types: 
                if p: manor_people += p
            manor_people = manor_people / manor.place.count()
            people += manor_people
        return people 
    @models.permalink
    def get_absolute_url(self):
        return ('domes.views.place', (), {
            'grid': self.grid,
            'vill_slug': self.vill_slug })
    
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
    @models.permalink
    def get_absolute_url(self):
        return ('domes.views.name', (), {
            'namesidx': self.namesidx,
            'name_slug': self.name_slug })

####################################
# Manor-related tables
####################################
# Manors - a reference to a place in a Domesday entry.
# Everything hangs off this. From ManorsForAHRC.txt
# But never exposed per se in front-end. 
class Manor(models.Model):
    structidx = models.IntegerField(primary_key=True)  
    place = models.ManyToManyField(Place, null=True, related_name="manors")
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
        if (self.cobs_1066 is not None or self.cattle_1066 is not None or \
            self.cows_1066 is not None or self.pigs_1066 is not None\
            or self.sheep_1066 is not None or self.goats_1066 is not None \
            or self.beehives_1066 is not None \
            or self.wild_mares_1066 is not None or self.other_1066 is not None):
            return True
        return False
    def has_livestock_1086(self):
        if (self.cobs_1086 is not None or self.cattle_1086 is not None \
            or self.cows_1086 is not None or self.pigs_1086 is not None \
            or self.sheep_1086 is not None or self.goats_1086 is not None \
            or self.beehives_1086 is not None \
            or self.wild_mares_1086 is not None or self.other_1086 is not None\
            or self.other_code_1086 is not None):
            return True
        return False  

################################################
# Image-related tables
################################################
# Files for JP to mark up. 
class ImageFile(models.Model):
    # The relevant filename. Save like 01.png
    filename = models.CharField(max_length=30, unique=True)
    county = models.ForeignKey(County)
    raw_width = models.IntegerField()
    raw_height = models.IntegerField()
    is_complete = models.BooleanField(default=False)
    def __unicode__(self):
        return "%s, %s"% (self.county.name, self.filename.split(".")[0])
    @models.permalink
    def get_absolute_url(self):
        file_url =  "%s_%s" % (self.county.name_slug, self.filename.split(".")[0])
        return ('domes.views.crop_file', (), {
            'file_id': file_url })
    class Meta:
        ordering = ('county', 'filename')
        unique_together = ("filename", "county")

class Image(models.Model):
    manor = models.ForeignKey(Manor)      
    phillimore = models.CharField(max_length=100, null=True, blank=True)         
    imagesub = models.CharField(max_length=30, null=True, blank=True)  
    image = models.CharField(max_length=30, null=True, blank=True) # The relevant filename. 
    ld_file = models.ForeignKey(ImageFile, null=True, blank=True)
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

class EnglishTranslation(models.Model):
    manor = models.OneToOneField(Manor)
    text = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True)
    user_ip = models.IPAddressField()
    last_edited = models.DateField(auto_now=True)
    created = models.DateField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    created = models.DateField(auto_now_add=True)
    objects = models.Manager()
    def __unicode__(self):
        return u'%s' % self.user
    def get_absolute_url(self):
        return ('profiles_profile_detail', (), { 'username': self.user.username })
    def translations(self):
        translations = EnglishTranslation.objects.filter(user=self.user)
        return translations
    get_absolute_url = models.permalink(get_absolute_url)
    
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