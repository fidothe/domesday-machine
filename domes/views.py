from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, RequestContext, loader, Context
from django.conf import settings
from domes.models import *
from domes.forms import EmailSignupForm
from django.db.models import Count
import re, urllib2, random
from django.utils import simplejson

################################
# Home page and map
################################

def homepage(request):
    # get all the grids with no vills, choose a random one
    placeidx = random.choice(random_places)
    place = Place.objects.get(placeidx=placeidx)
    manor = Manor.objects.get(structidx=place.structidx).get_interesting_queryset()
    other_vills = Place.objects.filter(structidx=place.structidx).exclude(vill=place.vill).order_by('vill')
    has_image = False
    try:
        tre_owners = TreOwner.objects.filter(structidx=place.structidx)
    except TreOwner.DoesNotExist:
        tre_owners = None
    try:
        image = Image.objects.get(structidx=place.structidx)
        has_image = True
    except Image.DoesNotExist:
        place_image = None
    try:
        livestock = Livestock.objects.get(structidx=place.structidx)
    except Livestock.DoesNotExist:
        livestock = None
    try:
        trw_owners = TrwOwner.objects.filter(structidx=place.structidx)
    except TrwOwner.DoesNotExist:
        trw_owners = None
    return render_to_response('domes/homepage.html', { 'has_map' : True, 'has_image': has_image, 'no_search_form' : True, 'place' : place, 'manor': manor, 'trw_owners': trw_owners, 'tre_owners':tre_owners, 'livestock':livestock}, context_instance = RequestContext(request))

def all_markers(request):
    query = "SELECT * FROM domes_place WHERE grid!='none' AND vill!='-' AND lat!='0.0' GROUP BY grid, vill"
    params = ()
    places = Place.objects.raw(query, params)
    markers = []
    for place in places:
        place_dict = {}
        place_dict['placeidx'] = str(place.placeidx)
        place_dict['lat'] = str(place.lat)
        place_dict['lng'] = str(place.lon)
        place_dict['vill'] = place.vill
        place_dict['grid'] = place.grid
        place_dict['hundred'] = place.hundred
        place_dict['county'] = place.county
        place_dict['waste86'] = place.waste86
        place_dict['holding'] = place.holding
        place_dict['units'] = place.units
        markers.append(place_dict)
    json = simplejson.dumps(markers)
    return HttpResponse(json, mimetype='application/json')

def all_places_json(request):
    term = request.GET.get('term', None)
    if term:
        query = "SELECT * FROM domes_place WHERE grid!='none' AND vill!='-' AND vill LIKE '%%" + term + "%%' GROUP BY vill"
        query.replace('%%', '%')
        print query
    else:
        query = "SELECT * FROM domes_place WHERE grid!='none' AND vill!='-' AND vill LIKE 'moddershall' GROUP BY vill"
    params = ()
    places = Place.objects.raw(query, params)
    markers = []
    for place in places:
        markers.append(place.vill)
    json = simplejson.dumps(markers)
    return HttpResponse(json, mimetype='application/json')

def markers_within_bounds(request):
    swLat = request.GET.get('swLat')
    swLng = request.GET.get('swLng')
    neLat = request.GET.get('neLat')
    neLng = request.GET.get('neLng')
    centreLat = request.GET.get('centreLat')
    centreLng = request.GET.get('centreLng')
    order_by_distance = request.GET.get('order_by_distance')
    if order_by_distance=='true':
       query = "SELECT lat, lng, vill, grid, waste86, holding, units, (SQRT(((lat-%s)*(lat-%s)) + ((lng-%s)*(lng-%s)))) AS distance FROM domes_place WHERE lat<%s AND lat>%s AND lon<%s AND lon>%s GROUP BY grid, vill ORDER BY distance;"
       params = [centreLat,centreLat,centreLng,centreLng,swLat,neLat,swLng,neLng]
       places = Place.objects.raw(query, params)
    else:
       places = Place.objects.filter(lat__range=(swLat, neLat),lon__range=(swLng, neLng))
       query = "SELECT * FROM domes_place WHERE lat<%s AND lat>%s AND lon<%s AND lon>%s GROUP BY grid, vill"
       params = [neLat,swLat,neLng,swLng]
       places = Place.objects.raw(query, params)
    markers = []
    for place in places:
        place_dict = {}
        place_dict['placeidx'] = str(place.placeidx)
        place_dict['lat'] = str(place.lat)
        place_dict['lng'] = str(place.lon)
        place_dict['vill'] = place.vill
        place_dict['grid'] = place.grid
        place_dict['hundred'] = place.hundred
        place_dict['county'] = place.county
        place_dict['waste86'] = place.waste86
        place_dict['holding'] = place.holding
        place_dict['units'] = place.units
        markers.append(place_dict)
    json = simplejson.dumps(markers)
    return HttpResponse(json, mimetype='application/json')

def map(request):
    return render_to_response('domes/map.html', { 'has_map' : True, }, context_instance = RequestContext(request))

################################
# Individual places and people
################################
def image(request):
    return render_to_response('domes/image.html', { }, context_instance = RequestContext(request))
		
################################
# Individual places and people
################################
def place(request, grid, vill_slug):
    vill_slug = urllib2.unquote(vill_slug)
    grid = urllib2.unquote(grid)
    place = get_object_or_404(Place, grid=grid)
    placerefs = PlaceRef.objects.filter(place=place)
    manors = Manor.objects.filter(placeref__place__id=place.id)
    #query = "sum(holding) as total_holding from domes_place where vill=%s and grid=%s group by grid,vill"
    #params = (grid,vill)
    #total_holding = Place.objects.raw(query, params)
    #comment_place = Place.objects.filter(grid=grid,vill_slug=vill_slug).order_by('structidx')[0]
    # Tell the template whether we have a map
    # if grid != "none":
    #     has_map = True
    # else:
    #     has_map = False
    # # Next: get the structidx for each place object into an array
    # # and work out the total holding in geld
    # place_structidxs = []
    # total_holding = 0.0
    # for place in places:
    #     place_structidxs.append(place.structidx)
    #     if place.units == "geld":
    #         try:
    #             holding = float(place.holding)
    #         except ValueError:
    #             holding = 0.0
    #         total_holding += holding
    # # Now: return a dictionary of dictionaries. Each inner dictionary is one Domesday entry
    # uber_struct = []
    # has_image = False
    # for place_structidx in place_structidxs:
    #     try:
    #         image = Image.objects.get(structidx=place_structidx)
    #         has_image = True
    #     except Image.DoesNotExist:
    #         place_image = None
    #     place_dict = {}
    #     place_dict['hundred'] = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).hundred
    #     place_dict['phillimore'] = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).phillimore
    #     place_dict['area'] = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).area
    #     place_dict['county'] = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).county
    #     place_dict['waste86'] = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).waste86
    #     place_dict['structidx'] = place_structidx
    #     lat = '52.5'
    #     lng = '0.0'
    #     grid = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).grid
    #     place_Person = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).vill
    #     county = Place.objects.get(structidx=place_structidx, vill_slug=vill_slug).county
    #     manor = Manor.objects.get(structidx=place_structidx)
    #     place_dict['manor'] = manor.get_interesting_queryset()
    #     place_dict['other_vills'] = Place.objects.filter(structidx=place_structidx).exclude(vill_slug=vill_slug).order_by('vill')
    #     place_dict['tre_owners'] = TreOwner.objects.filter(structidx=place_structidx)
    #     try:
    #         place_dict['livestock'] = Livestock.objects.get(structidx=place_structidx)
    #     except Livestock.DoesNotExist:
    #         place_dict['livestock'] = None
    #     place_dict['trw_owners'] = TrwOwner.objects.filter(structidx=place_structidx)
    #     print place_structidx
    #     uber_struct.append(place_dict)   
    # phillimore = None
    # description_text = []      
    # form = EmailSignupForm()
    #return render_to_response('domes/place.html', { 'comment_place': comment_place, 'vill': vill, 'lat': lat, 'lng': lng, 'grid':grid, 'place_Person':place_Person, 'county': county, 'total_holding': total_holding, 'place_structidxs': place_structidxs, 'uber_struct' : uber_struct, 'description_text' : description_text, 'phillimore_array' : phillimore, 'has_map' : has_map, 'has_image' : has_image, }, context_instance = RequestContext(request))
    return render_to_response('domes/place.html', { 'place': place, 'manors': manors }, context_instance = RequestContext(request))

def county(request, county_Person):
    county_Person = urllib2.unquote(county_Person)
    query = "SELECT placeidx, hundred, grid, holding, units, vill, count(*) AS count FROM domes_place WHERE county=%s AND vill!='-' GROUP BY grid, vill"
    params = (county_Person,)
    places = Place.objects.raw(query, params)
    return render_to_response('domes/county.html', { 'county_Person' : county_Person, 'places' : places, 'has_map' : True,  }, context_instance = RequestContext(request))

def hundred(request, hundred_Person):
    hundred_Person = urllib2.unquote(hundred_Person)
    query = "SELECT placeidx, county, grid, holding, units, vill, count(*) AS count FROM domes_place WHERE hundred=%s AND vill!='-' GROUP BY grid, vill"
    params = (hundred_Person,)
    places = Place.objects.raw(query, params)
    return render_to_response('domes/hundred.html', { 'hundred_Person' : hundred_Person, 'places' : places, 'has_map' : True,  }, context_instance = RequestContext(request))

def owner(request, owner_Person):
    owner_Person = urllib2.unquote(owner_Person)
#    query = "SELECT structidx FROM domes_TreOwner WHERE lord66=%s"
 #   params = (owner_Person,)
 #   lord66_places = TreOwner.objects.raw(query, params)
    lord66_owners = TreOwner.objects.filter(lord66=owner_Person)
    lord66_places = []
    for owner in lord66_owners:
        actual_places = Place.objects.filter(structidx=owner.structidx)
        for actual_place in actual_places:
            lord66_places.append(actual_place)
    overlord66_owners = TreOwner.objects.filter(overlord66=owner_Person)
    overlord66_places = []
    for owner in overlord66_owners:
        actual_places = Place.objects.filter(structidx=owner.structidx)
        for actual_place in actual_places:
            overlord66_places.append(actual_place)
    lord86_owners = TrwOwner.objects.filter(lord86=owner_Person)
    lord86_places = []
    for owner in lord86_owners:
        actual_places = Place.objects.filter(structidx=owner.structidx)
        for actual_place in actual_places:
            lord86_places.append(actual_place)
    teninchief86_owners = TrwOwner.objects.filter(teninchief=owner_Person)
    teninchief86_places = []
    for owner in teninchief86_owners:
        actual_places = Place.objects.filter(structidx=owner.structidx)
        for actual_place in actual_places:
            teninchief86_places.append(actual_place)
    return render_to_response('domes/owner.html', { 'owner_Person' : owner_Person, 'lord66_places' : lord66_places, 'overlord66_places' : overlord66_places, 'lord86_places' : lord86_places, 'teninchief86_places' : teninchief86_places, 'has_map' : True,  }, context_instance = RequestContext(request))

def person(request, Personidx, Person_slug):
    person = Person.objects.get(Personsidx=Personidx)
    lord66_owners = TreOwner.objects.filter(idxlord66=Personidx)
    lord66_places = []
    for owner in lord66_owners:
          placerefs = owner.get_places()
    #     for actual_place in actual_places:
    #         lord66_places.append(actual_place)
    # overlord66_owners = TreOwner.objects.filter(idxoverlord66=Personidx)
    # overlord66_places = []
    # for owner in overlord66_owners:
    #     actual_places = Place.objects.filter(structidx=owner.structidx)
    #     for actual_place in actual_places:
    #         overlord66_places.append(actual_place)
    # lord86_owners = TrwOwner.objects.filter(idxlord86=Personidx)
    # lord86_places = []
    # for owner in lord86_owners:
    #     actual_places = Place.objects.filter(structidx=owner.structidx)
    #     for actual_place in actual_places:
    #         lord86_places.append(actual_place)
    # teninchief86_owners = TrwOwner.objects.filter(idxteninchief=Personidx)
    # teninchief86_places = []
    # for owner in teninchief86_owners:
    #     actual_places = Place.objects.filter(structidx=owner.structidx)
    #     for actual_place in actual_places:
    #         teninchief86_places.append(actual_place)
    # return render_to_response('domes/person.html', { 'person_Person' : person_Person, 'lord66_places' : lord66_places, 'overlord66_places' : overlord66_places, 'lord86_places' : lord86_places, 'teninchief86_places' : teninchief86_places, 'has_map' : True,  }, context_instance = RequestContext(request))
    return render_to_response('domes/person.html', { 'person' : person, 'placerefs': placerefs, 'has_map' : True,  }, context_instance = RequestContext(request))

################################
# Search
################################
def search(request):
    geo = request.GET.get('geo', None)
    text = request.GET.get('text', None)
    if geo: 
         has_map = True
    else: 
         has_map = False
    return render_to_response('domes/search.html', { 'geo' : geo, 'text' : text, 'has_map' : has_map, }, context_instance = RequestContext(request))

################################
# Statistics listings
################################
def stats(request):
    counties = County.objects.exclude(short_code="LAN").order_by('Person')
    return render_to_response('domes/stats.html', { 'counties' : counties, }, context_instance = RequestContext(request))

################################
# Place listings - counties & places
################################
def all_counties(request):
    counties = County.objects.exclude(short_code="LAN") # exclude Lancashire because it has no places
    return render_to_response('domes/all_counties.html', { 'counties' : counties, }, context_instance = RequestContext(request))

def all_places(request):
    index_char = request.GET.get('indexChar', 'a')
    places = Place.objects.filter(vill__istartswith=index_char).order_by('vill')
    return render_to_response('domes/all_places.html', { 'places' : places }, context_instance = RequestContext(request))

def all_people(request):
    index_char = request.GET.get('indexChar', 'a')
    people = Person.objects.filter(Person__istartswith=index_char).order_by('name')
    return render_to_response('domes/all_people.html', { 'people' : people, }, context_instance = RequestContext(request))

def translate(request):
    return render_to_response('domes/translate.html', {}, context_instance = RequestContext(request))

def book(request):
    image_entries = Image.objects.filter(county="MDX", image="mdx/05.png")
    super_struct = {}
    super_struct['image_Person'] = "mdx/05.png"
    annotate_array = []
    annotate = {}
    for image_entry in image_entries: 
        annotate['structidx'] = image_entry.structidx
       # print image_entry.structidx
        annotate['top'] = image_entry.y1
        annotate['left'] = image_entry.x1
        annotate['width'] = (image_entry.x2 - image_entry.x1)
        annotate['height'] = (image_entry.y2 - image_entry.y1)
        associated_places = Place.objects.filter(structidx=image_entry.structidx)
        place_array = []
        for associated_place in associated_places:
            place_array.append(associated_place.vill)
            print associated_place.vill
        annotate['places'] = place_array
      #  print 'annotate', annotate
        annotate_array.append(annotate)
        print 'appending to array...'
        print 'annotate_array', annotate_array
    super_struct['entries'] = annotate_array
    return render_to_response('domes/translate.html', { 'super_struct' : super_struct, }, context_instance = RequestContext(request))

def forum(request):
    return render_to_response('domes/forum.html', { }, context_instance = RequestContext(request))

####################################
# API
####################################
def api(request):
    return render_to_response('domes/api.html', context_instance = RequestContext(request))

####################################
# General pages - FAQ and to-do list
####################################
def about(request):
    return render_to_response('domes/about.html', context_instance = RequestContext(request))
 
def help(request):
    return render_to_response('domes/help.html', context_instance = RequestContext(request))   

# To-do list    
def todo(request):
    return render_to_response('domes/todo.html', context_instance = RequestContext(request))


########## NON-VIEW FUNCTIONS ####################

################################
# Text
################################

def text(request):
    county_Person = request.GET.get('county', None)
    if county_Person: 
        county = get_object_or_404(County.objects, Person=county_Person)
        county_Person = county.Person
        places = Place.objects.filter(county=county.short_code).exclude(vill="-")
        has_map = True
        text_all = RawText.objects.filter(id__contains=county.short_code).order_by('id')
        new_text = []
        for text in text_all:
            text.id = text.id.split("-")[1]
            #text.text = markup_text(text.text)
            new_text.append(text)
    else:
        county_Person = "Choose a county"
        has_map = False
        new_text = []
        places = []
    # exclude Lancashire because it has no places
    counties = County.objects.exclude(short_code="LAN")
    return render_to_response('domes/text.html', { 'text_all' : new_text, 'places' : places, 'counties' : counties, 'county_Person' : county_Person, 'has_map' : True, }, context_instance = RequestContext(request))


def get_phillimore_text(id):
    phillimore = parse_phillimore(str(place.phillimore)) 
    #phillimore = natsort(phillimore)
    description_text = []
    for i, ph in enumerate(phillimore):
       ph = str(place.county) + "-" + ph 
       phillimore[i] = ph
       try:
           entry_text = RawText.objects.filter(id__icontains=ph)
           for entry in entry_text:
               #final_text = #markup_text(entry.text, place.area)
               entry.id = entry.id.split("-")[1]
               description_text.append(entry)
       except RawText.DoesNotExist:
               pass   
    return description_text 

def markup_text(some_text):
    return some_text

def sortedDictValues1(adict):
    items = adict.items()
    items.sort()
    return [value for key, value in items]

# Mark up the phillimore references into a usable list
# - handles strings like "1,16. 14,14. 29,10;12"
def parse_phillimore(phillimore_text):
        temp_list = phillimore_text.split(". ")
        phillimore_list = []
        for t in temp_list:
            #check for dashes
            dash_list = t.split("-")
            if (len(dash_list) > 1):
                dash_list[0] = dash_list[0].replace("(", "")
                phillimore_list.append(dash_list[0])
                split_by_comma = dash_list[0].split(",")
                after_dash = split_by_comma[0] + "," + dash_list[1]
                after_dash = after_dash.replace(")", "")
            else:
                #check for semi-colons
                semicolon_list = t.split(";")
                if (len(semicolon_list) > 1):
                     semicolon_list[0] = semicolon_list[0].replace("(", "")
                     phillimore_list.append(semicolon_list[0])
                     split_by_comma = semicolon_list[0].split(",")
                     after_semicolon = split_by_comma[0] + "," + semicolon_list[1]
                     after_semicolon = after_semicolon.replace(")", "")
                     phillimore_list.append(after_semicolon)
                else:
                     phillimore_list.append(t)

        return phillimore_list

# Mark up the manor fields
def process_manor_fields(manordict):
    return manordict

# Handle the plain-text markup in the Phillimore text
def markup_text(text, placePerson):
    text = text.replace( '<', '<span class="individual-known">')
    text = text.replace( '>', '</span>')
    text = text.replace( '[=', '<span class="landowner">')
    text = text.replace( '=]', '</span>')
    text = text.replace( '[*', '<span class="individual-known">')
    text = text.replace( '*]', '</span>')
    text = text.replace( '^[', '<span class="inferred">')
    text = text.replace( ']^', '</span>')
    text = text.replace( '[!1!', '<span class="satellite-exon">')
    text = text.replace( '!1!]', '</span>')
    text = text.replace( '[!2!', '<span class="satellite-monachorum">')
    text = text.replace( '!2!]', '</span>')
    text = text.replace( '[!3!', '<span class="satellite-augustines">')
    text = text.replace( '!3!]', '</span>')
    text = text.replace( '[!4!', '<span class="satellite-icc">')
    text = text.replace( '!4!]', '</span>')
    text = text.replace( '[!5!', '<span class="satellite-ely">')
    text = text.replace( '!5!]', '</span>')
    text = text.replace( '[!6!', '<span class="satellite-bury">')
    text = text.replace( '!6!]', '</span>')
    text = text.replace( '\n', '<br/>')
    return text

def natsort(list_):
    # decorate
    tmp = [ (int(re.search('\d+', i).group(0)), i) for i in list_ ]
    tmp.sort()
    # undecorate
    return [ i[1] for i in tmp ]

###### Textbase markup (from guide.rtf)
#   [=  =]  Landholders inserted into each entry based upon the fief heading
#   [*  *]  Individual accorded a known byPerson, or other identified material; the identifications are explained in the Notes
#   <   >   Individual accorded an estate Person in the absence of a known byPerson; the identification is explained in the Notes
#   ^[  ]^  Information inferred from another part of the text.
#   [!1!    !1!]    Not in Domesday Book, from satellite text (Exon.)
#   [!2!    !2!]    Not in Domesday Book, from satellite text (Domesday Monachorum)
#   [!3!    !3!]    Not in Domesday Book, from satellite text (St Augustines)
#   [!4!    !4!]    Not in Domesday Book, from satellite text (ICC)
#   [!5!    !5!]    Not in Domesday Book, from satellite text(Ely Inquisition)
#   [!6!    !6!]    Not in Domesday Book, from satellite text (Feudal Book of Bury)
# <12a> Folio numbers are recorded in chevrons

random_places = [ 6010,  6090,  6110,  6130,  6140,  6160,  6170,  6220,  6240,  6260,  6270,  6300,  6320,  6340,  6350,  6380,  6430,  6460,  6500,  6510,  6520,  6530,  6560,  6570,  6620,  6640,  6670,  6770,  6830,  6840,  6850,  6870,  6880,  6910,  7000,  7010,  7050,  7060,  7100,  7150,  7160,  7180,  7230,  7350,  7380,  7440,  7500,  7660,  7670,  7790,  7900,  7910,  7920,  7960,  7970,  7980,  8070,  8080,  8100,  8110,  215040,  215050,  215070,  215150,  215190,  215280,  215310,  215320,  215380,  215390,  215410,  215420,  215430,  215440,  215480,  215500,  215540,  215550,  215620,  215630,  215670,  215680,  215700,  215710,  215820,  215830,  215840,  215890,  215930,  215950,  215990,  216020,  216040,  216050,  216200,  216220,  216300,  216330,  216340,  216350,  216420,  216530,  216540,  216610,  216620,  216630,  216660,  216730,  216750,  216770,  216980,  217000,  217120,  217170,  217180,  217210,  217220,  217360,  217390,  217400,  226520,  226730,  226740,  226820,  226840,  226850,  226940,  226990,  227000,  227200,  227220,  227240,  227300,  227330,  227520,  227610,  227620,  227630,  227680,  227700,  227740,  227780,  227860,  227870,  227880,  227900,  227920,  228190,  228310,  228370,  228430,  228450,  228500,  228510,  228560,  228970,  229110,  229120,  229180,  229310,  229370,  229410,  229420,  229530,  229560,  229570,  229610,  229650,  229670,  229770,  229780,  229790,  229820,  230000,  230090,  230100,  230110,  230130,  230160,  230290,  67600,  67630,  67640,  67840,  67850,  67860,  67870,  67910,  67940,  67970,  68030,  68040,  68050,  68070,  68080,  68100,  68150,  68180,  68200,  68210,  68220,  68230,  68270,  68290,  68300,  68310,  68330,  68390,  68400,  68410,  68430,  68460,  68480,  68510,  68520,  68540,  68560,  68660,  68670,  68690,  68710,  68730,  68750,  68790,  68810,  50650,  50740,  50750,  50760,  50770,  50780,  50810,  50820,  50840,  50850,  50860,  50870,  50880,  50920,  50930,  50940,  50950,  50960,  50980,  50990,  51010,  51020,  51030,  51040,  51050,  51060,  51080,  51090,  51100,  51120,  51140,  51160,  51170,  51200,  51210,  51220,  51230,  51240,  51250,  51270,  51290,  51300,  51310,  51320,  51330,  51360,  51380,  51390,  51420,  51430,  51450,  51460,  51470,  51480,  51500,  51510,  51520,  51530,  51540,  51550,  77580,  77600,  77620,  77640,  77660,  77670,  77690,  77700,  77710,  77720,  77730,  77780,  77800,  77830,  77890,  77940,  77950,  77960,  78030,  78040,  78060,  78080,  78090,  78100,  78110,  78140,  78230,  78240,  78250,  78280,  78290,  78330,  78340,  78420,  78430,  78520,  78560,  78600,  78660,  78670,  78680,  78720,  78770,  78800,  78910,  78930,  78980,  79030,  79070,  79080,  79090,  79100,  79110,  79160,  79180,  79220,  79250,  79260,  79300,  79310,  128300,  128320,  128340,  128350,  128360,  128370,  128380,  128390,  128410,  128420,  128430,  128440,  128450,  128460,  128470,  128480,  128500,  128510,  128520,  128530,  128540,  128550,  128560,  128570,  128580,  128590,  128600,  128610,  128620,  128630,  128650,  128660,  128670,  128680,  128690,  128700,  128710,  128720,  128730,  128740,  128750,  128760,  128770,  128780,  128790,  128810,  128820,  128840,  128850,  128870,  128880,  128890,  128900,  128910,  128920,  128930,  128940,  128950,  128970,  128980,  182835,  183010,  183030,  183060,  183150,  183200,  183230,  183250,  183290,  183350,  183440,  183460,  183500,  183570,  183633,  183636,  183640,  183650,  183700,  183710,  183830,  183850,  183890,  183930,  184040,  184050,  184230,  184340,  184420,  184540,  184570,  184590,  184890,  185050,  185160,  185260,  185340,  185540,  185650,  185760,  185910,  185920,  185990,  186000,  186190,  186270,  186280,  186310,  186320,  186340,  186360,  186370,  186600,  186670,  186830,  186880,  186940,  187000,  187090,  187100,  106170,  106180,  106190,  106210,  106290,  106310,  106320,  106340,  106350,  106390,  106400,  106630,  106660,  106680,  106690,  106700,  106740,  106820,  106840,  106920,  107100,  107170,  107250,  107290,  107320,  107370,  107500,  107550,  107590,  107630,  107640,  107670,  107680,  107690,  107700,  107730,  107750,  107900,  108130,  108150,  108190,  108200,  108210,  108240,  108270,  108430,  108580,  108620,  108690,  108850,  108900,  108980,  109160,  109250,  109370,  109410,  109480,  109530,  109570,  109580,  27335,  27370,  27400,  27480,  27500,  27510,  27530,  27550,  27580,  27600,  27630,  27700,  27730,  27740,  27760,  27790,  27800,  27820,  27850,  27900,  27910,  27920,  27940,  27970,  27980,  28000,  28010,  28020,  28040,  28070,  28130,  28140,  28180,  28210,  28250,  28260,  28270,  28290,  28340,  28380,  28400,  28420,  28430,  28440,  28450,  28470,  28480,  28520,  28590,  28630,  28650,  28660,  28680,  28690,  28700,  28730,  28740,  28760,  28800,  28810,  103980,  103990,  104020,  104040,  104050,  104080,  104100,  104110,  104130,  104140,  104170,  104190,  104230,  104250,  104260,  104290,  104320,  104340,  104350,  104360,  104370,  104390,  104400,  104420,  104430,  104450,  104470,  104480,  104540,  104570,  104580,  104590,  104600,  104610,  104640,  104650,  104660,  104670,  104680,  104710,  104730,  104740,  104780,  104840,  104860,  104870,  104890,  104910,  104970,  104990,  105030,  105050,  105080,  105150,  105250,  105260,  105300,  105360,  105370,  105400,  310,  500,  755,  855,  890,  930,  940,  970,  1020,  1040,  1050,  1060,  1070,  1080,  1100,  1130,  1180,  1190,  1200,  1220,  1230,  1240,  1280,  1310,  1320,  1330,  1340,  1350,  1370,  1375,  1430,  1450,  1475,  1480,  1490,  1510,  1540,  1560,  1570,  1590,  1600,  1610,  1620,  1640,  1650,  1660,  1670,  1680,  1730,  1760,  1770,  1780,  1810,  1820,  1840,  1850,  1860,  1870,  1880,  1890,  ]