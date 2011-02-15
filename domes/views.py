from operator import itemgetter
import random, re, urllib2, uuid
from django.conf import settings
from django.contrib.gis.geos import Point, Polygon
from django.contrib.gis.geos import fromstr
from django.contrib.gis.measure import D
from django.db.models import Count, Sum, Q
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import Template, RequestContext, loader, Context
from django.utils import simplejson
from domes.forms import TranslateForm
from domesday.domes.models import *
import csv
import util

################################
# Home page and map
################################

def homepage(request):
    no_search_form = True
    placeid = random.choice(random_places)
    place = Place.objects.get(id=placeid)
    areas = place.area.all()
    counties = place.county.all()
    manors = Manor.objects.filter(place__id=place.id).order_by('geld')
    if manors.count() > 1:
        manors_sorted = list(manors)
        manors = sorted(manors_sorted, key=lambda x: x.geld, reverse=True)
    tax_context = get_context(place.raw_value, "TAX")
    pop_context = get_context(place.population, "POPULATION")
    return render_to_response('domes/homepage.html', { 'place': place, \
              'areas': areas, 'counties': counties, 'manors': manors, \
              'has_image': True, 'tax_context': tax_context, \
              'pop_context': pop_context, 'no_search_form' : no_search_form }, \
              context_instance = RequestContext(request))

# TODO: see if Django can cache this.
def all_places_json(request):
    places = Place.objects.exclude(grid="XX0000").exclude(location__isnull=True)[:500]
    markers = []
    for place in places:
        place_dict = {}
        place_dict['lat'] = place.location.y
        place_dict['lng'] = place.location.x
        place_dict['grid'] = place.grid
        place_dict['vill'] = place.vill
        place_dict['vill_slug'] = place.vill_slug
        if place.hundred:
            place_dict['hundred'] = place.hundred.name
        county = place.county.all()[0].name
        place_dict['county'] = county
        place_dict['raw_value'] = place.raw_value
        place_dict['population'] = place.population
        markers.append(place_dict)
    json = simplejson.dumps(markers)
    return HttpResponse(json, mimetype='application/json')

def markers_within_bounds(request):
    swLat = request.GET.get('swLat')
    swLng = request.GET.get('swLng')
    neLat = request.GET.get('neLat')
    neLng = request.GET.get('neLng')
    centreLat = str(request.GET.get('centreLat'))
    centreLng = str(request.GET.get('centreLng'))
    centre = fromstr('POINT(%s %s)' % (centreLng, centreLat))
    boundaries = fromstr('POLYGON((%s %s,%s %s,%s %s,%s %s,%s %s))' % \
           (swLng, swLat, swLng, neLat, neLng, neLat, neLng, swLat, swLng, swLat))
    places = Place.objects.filter(location__within=boundaries).distance(centre).order_by('distance')
    markers = []
    for place in places:
        place_dict = {}
        place_dict['lat'] = place.location.y
        place_dict['lng'] = place.location.x
        place_dict['grid'] = place.grid
        place_dict['vill'] = place.vill
        place_dict['vill_slug'] = place.vill_slug
        if place.hundred:
            place_dict['hundred'] = place.hundred.name
            place_dict['hundred_slug'] = place.hundred.name_slug
        county = place.county.all()[0].name
        place_dict['county'] = county
        place_dict['value'] = place.value
        place_dict['distance'] = str(place.distance/1000).rstrip(" m")
        place_dict['raw_value'] = place.raw_value
        place_dict['population'] = place.population
        markers.append(place_dict)
    json = simplejson.dumps(markers)
    return HttpResponse(json, mimetype='application/json')

def map(request):
    places = Place.objects.exclude(grid="XX0000").exclude(location__isnull=True)
    return render_to_response('domes/map.html', { 'has_map' : True, 'places': places }, 
        context_instance = RequestContext(request))

################################
# Images
################################

def all_images(request):
    return render_to_response('domes/image.html', { }, \
                context_instance = RequestContext(request))

def image(request, county, number):
    number = urllib2.unquote(number)
    number_clean = number.lstrip("0")
    county_slug = urllib2.unquote(county)
    county_object = get_object_or_404(County, name_slug=county_slug)
    filepath = "%s/%s.png" % (county_object.short_code.lower(), number)
    images = Image.objects.filter(image=filepath)
    # Check for next/previous images
    next_number = int(number_clean)+1
    previous_number = int(number_clean)-1
    if len(str(next_number))==1: next_number = "0" + str(next_number)
    if len(str(previous_number))==1: previous_number = "0" + str(previous_number)
    next_path = "%s/%s.png" % (county_object.short_code.lower(), next_number)
    previous_path = "%s/%s.png" % (county_object.short_code.lower(), previous_number)
    has_previous_image = Image.objects.filter(image=next_path)
    has_next_image = Image.objects.filter(image=next_path)
    return render_to_response('domes/image.html', { 'images': images, \
        'county': county, 'number_clean' : number_clean, \
        'filepath' : filepath }, context_instance = RequestContext(request))

# TODO: would probably be better to put this in a template tag.
def get_context(size, context_type):
    if context_type == "POPULATION":
        if size > settings.POP_QUIN5:
             context = "very large"
        elif size > settings.POP_QUIN4:
             context = "quite large"
        elif size > settings.POP_QUIN3:
             context = "medium"
        elif size > settings.POP_QUIN2:
             context = "quite small"
        else:
             context = "very small"
    elif context_type == "TAX":
        if size > settings.TAX_QUIN5:
             context = "very large"
        elif size > settings.TAX_QUIN4:
             context = "quite large"
        elif size > settings.TAX_QUIN3:
             context = "medium"
        elif size > settings.TAX_QUIN2:
             context = "quite small"
        else:
             context = "very small"
    else:
        context = ''
    return context

################################
# Individual places and people
################################
def place(request, grid, vill_slug):
    grid = urllib2.unquote(grid)
    vill_slug = urllib2.unquote(vill_slug) 
    try: # Support old URLs.
        place = Place.objects.get(Q(grid=grid, vill_slug=vill_slug) | Q(grid=grid, vill=vill_slug))
    except Place.DoesNotExist:
        raise Http404
    areas = place.area.all()
    counties = place.county.all()
    manors = Manor.objects.filter(place__id=place.id).order_by('geld')
    if manors.count() > 1:
        manors_sorted = list(manors)
        manors = sorted(manors_sorted, key=lambda x: x.geld, reverse=True)
    tax_context = get_context(place.raw_value, "TAX")
    pop_context = get_context(place.population, "POPULATION")
    return render_to_response('domes/place.html', { 'place': place, \
              'areas': areas, 'counties': counties, 'manors': manors, \
              'has_image': True, 'tax_context': tax_context, 'pop_context': pop_context }, \
              context_instance = RequestContext(request))

def county(request, county_slug):
    county_slug = urllib2.unquote(county_slug) 
    try: # Support old URLs.
        county = County.objects.get(Q(name_slug=county_slug) | Q(name=county_slug))
    except County.DoesNotExist:
        raise Http404
    places = Place.objects.filter(county=county)
    if places.collect():
        centre = places.collect().centroid
    else:
        centre = None
    return render_to_response('domes/county.html', { 'places' : places, \
              'county' : county, 'centre': centre }, context_instance = RequestContext(request))

def hundred(request, hundred_slug):
    hundred_slug = urllib2.unquote(hundred_slug) 
    try: # Support old URLs.
        hundred = Hundred.objects.get(Q(name_slug=hundred_slug) | Q(name=hundred_slug))
    except Hundred.DoesNotExist:
        raise Http404
    places = Place.objects.filter(hundred=hundred)
    if places.collect():
        centre = places.collect().centroid
    else:
        centre = None
    return render_to_response('domes/hundred.html', { 'hundred': hundred, \
          'centre': centre, 'places' : places }, \
          context_instance = RequestContext(request))

def name(request, namesidx, name_slug):
    person = get_object_or_404(Person, namesidx=namesidx)
    places_lord66 = Place.objects.filter(manors__lord66=person)
    places_overlord66 = Place.objects.filter(manors__overlord66=person)
    places_lord86 = Place.objects.filter(manors__lord86=person)
    places_teninchief = Place.objects.filter(manors__teninchief=person)  
    all_places = places_lord66 | places_overlord66 | places_lord86 | places_teninchief
    if all_places.collect():
        centre = all_places.collect().centroid
    else:
        centre = None
    colour_lord66 = '6699FF' # pale blue
    colour_overlord66 = '0066CC' # dark blue 
    colour_lord86 = 'FF6666' # pale red
    colour_teninchief = 'CC0000' # dark red
    num_pre_conquest = sum([lord.place.count() for lord in person.lord66.all()])
    num_pre_conquest += sum([lord.place.count() for lord in person.overlord66.all()])
    num_post_conquest = sum([lord.place.count() for lord in person.lord86.all()])
    num_post_conquest += sum([lord.place.count() for lord in person.teninchief.all()])
    return render_to_response('domes/name.html', { 'person': person, \
       'places_lord66' : places_lord66, 'places_overlord66' : places_overlord66, 
       'places_lord86' : places_lord86, 'places_teninchief' : places_teninchief, 
       'centre': centre, 'colour_lord66': colour_lord66, \
       'colour_overlord66': colour_overlord66, 'colour_lord86': colour_lord86, \
       'colour_teninchief' : colour_teninchief, 'num_pre_conquest': num_pre_conquest,\
       'num_post_conquest': num_post_conquest, 'centre': centre }, \
            context_instance = RequestContext(request))

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
    return render_to_response('domes/search.html', { 'geo' : geo, \
      'text' : text, 'has_map' : has_map, }, context_instance = RequestContext(request))

################################
# Statistics listings
################################
def stats(request):
    top_pop = Place.objects.all()
    return render_to_response('domes/stats.html', { 'top_pop' : top_pop[:9], }, 
           context_instance = RequestContext(request))

################################
# Place listings - counties & places
################################
def all_counties(request):
    counties = County.objects.exclude(short_code="LAN") 
    # Exclude Lancashire - it didn't exist :( and so has no places.
    return render_to_response('domes/all_counties.html', { 'counties' : counties, }, 
                 context_instance = RequestContext(request))

def all_places(request):
    index_char = request.GET.get('indexChar', 'a')
    places = Place.objects.filter(vill__istartswith=index_char).order_by('vill')
    return render_to_response('domes/all_places.html', { 'places' : places }, 
                 context_instance = RequestContext(request))

def all_names(request):
    index_char = request.GET.get('indexChar', 'a')
    people = Person.objects.filter(name__istartswith=index_char).order_by('name')
           #Q(lord66__isnull=False) | Q(overlord66__isnull=False) \
            #   | Q(lord86__isnull=False) | Q(teninchief__isnull=False)
    return render_to_response('domes/all_names.html', { 'people' : people, }, 
               context_instance = RequestContext(request))

################################
# Translation pages
################################

def translate(request, county=None):
    if county:
        county = get_object_or_404(County.objects, name_slug=county)
        # Get all entries with no associated EnglishTranslations
        entries = Manor.objects.filter(county=count)
    else: 
        entries = Manor.objects.filter()
    translated = int (EnglishTranslation.objects.count() / Manor.objects.count())
    top_users = User.objects.all()
    return render_to_response('domes/translate.html', { 'translated': translated, 
           'top_users' : top_users }, context_instance = RequestContext(request))

def crowdsource(request, structidx):
    manor = Manor.objects.get(structidx=structidx)
    # TODO: add logic to check if there is a translation already.
    # if manor.englishtranslation is not None: 
    #     return HttpResponseRedirect('/translate/')
    if request.method == 'POST': 
        if request.user.is_authenticated():
            user = request.user
        else:
            user = None
        form = TranslateForm(request.POST) 
        if form.is_valid(): 
            text = form.cleaned_data['transcription']
            ip_address = "127.0.0.1"
            #ip_address = request.META['HTTP_X_FORWARDED_FOR']
            et = EnglishTranslation.objects.create(text=text,
               user=user, manor_id=structidx, user_ip=ip_address)
            et.save()
            return HttpResponseRedirect('/translated/') 
    else:
        form = TranslateForm() # An unbound form
    return render_to_response('domes/crowdsource.html', { 'manor': manor,
         'form': form, }, context_instance = RequestContext(request))

def translated(request):
    return render_to_response('domes/translated.html', {}, context_instance = RequestContext(request))
        
################################
# Generic pages
################################

def book(request):
    return render_to_response('domes/book.html', { }, context_instance = RequestContext(request))

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

####################################
# Cropping files.
####################################
    
def crop_all(request):
    essex_files = ImageFile.objects.filter(county="ESS")
    norfolk_files = ImageFile.objects.filter(county="NFK")
    suffolk_files = ImageFile.objects.filter(county="SUF")
    return render_to_response('domes/crop_files.html', { 'essex_files' : essex_files, 
      'suffolk_files' : suffolk_files, 'norfolk_files' : norfolk_files  },
      context_instance = RequestContext(request))

def crop_file(request, file_id):
    file_id = file_id.split("_")
    county = get_object_or_404(County.objects, name_slug=file_id[0])
    filename = file_id[1] + '.png'
    image_file = get_object_or_404(ImageFile.objects, county=county, filename=filename)
    images_markup = Image.objects.filter(ld_file=image_file)
    image_width = int(image_file.raw_width / settings.CROP_SCALE_FACTOR)
    image_height = int(image_file.raw_height / settings.CROP_SCALE_FACTOR)
    return render_to_response('domes/crop.html', { 'image' : image_file, \
               'images_markup' : images_markup, 'image_width' : image_width, \
               'image_height' : image_height }, 
               context_instance = RequestContext(request))

def crop_results(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=crop_results.csv'
    writer = csv.writer(response)
    image_files = ImageFile.objects.all()
    writer.writerow(['Filename', 'Structidx', \
                      'X1', 'X2', 'Y1', 'Y2'])
    for image_file in image_files:
        for image in image_file.image_set.all():
             writer.writerow([ "%s/%s" % (image_file.county, image_file.filename), image.manor.structidx, \
                image.x1, image.x2, image.y1, image.y2])
    return response
    
def load_tags(request):
    photo_id = request.GET.get("photoID")
    ids = photo_id.split("_")
    county = County.objects.get(short_code__iexact=ids[0])
    image_file = ImageFile.objects.get(county=county, filename=ids[1])
    images = Image.objects.filter(ld_file=image_file)
    results_list = []
    for image in images: 
        results = {}
        results["id"] = image.id
        results["photoid"] = photo_id
        results["message"] = image.manor.structidx
        # Scale width and height for client-side display.
        results["x"] = float(image.x1 / settings.CROP_SCALE_FACTOR)
        results["y"] = float(image.y1 / settings.CROP_SCALE_FACTOR)
        results["height"] = float((image.y2-image.y1) / settings.CROP_SCALE_FACTOR)
        results["width"] = float((image.x2-image.x1) / settings.CROP_SCALE_FACTOR)
        results_list.append(results)
    json = simplejson.dumps(results_list)
    return HttpResponse(json, mimetype='application/json')

def save_tags(request):
    photo_id = request.GET.get("photoID")
    ids = photo_id.split("_")
    structidx = request.GET.get("message")
    # The X/Y coordinates. Multiply by scale factor.
    client_x = int(request.GET.get("x"))
    client_y = int(request.GET.get("y"))
    client_width = int(request.GET.get("width"))
    client_height = int(request.GET.get("height"))
    x = client_x * settings.CROP_SCALE_FACTOR
    y = client_y * settings.CROP_SCALE_FACTOR
    x2 = (client_x + client_width) * settings.CROP_SCALE_FACTOR
    y2 = (client_y + client_height) * settings.CROP_SCALE_FACTOR
    county = County.objects.get(short_code__iexact=ids[0])
    image_file = get_object_or_404(ImageFile.objects, county=county, filename=ids[1])
    manor = get_object_or_404(Manor.objects, structidx=structidx)
    new_image, created = Image.objects.get_or_create(manor=manor, \
              image=ids[1], ld_file=image_file, 
              x1=x, y1=y, x2=x2, y2=y2)
    json = simplejson.dumps(new_image.id)
    return HttpResponse(json, mimetype='application/json')
    
def delete_tags(request):
    image_id = request.GET.get("id")
    Image.objects.get(id=image_id).delete()
    json = simplejson.dumps("ok")
    return HttpResponse(json, mimetype='application/json')

def all_tags(request):
    json = simplejson.dumps('yes')
    return HttpResponse(json, mimetype='application/json')
    
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

random_places = [52456, 38396,  8326, 25661, 22771, 58621, \
     58171, 38721, 15286,  9781,  9766, 25931,  2661, 70051, 56916, \
     12201, 60251, 43791,  7826, 49196,  5061, 65551, 29646, 36971, 57416,\
     61166]