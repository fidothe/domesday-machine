var map; 
var place_name = "";
var infowindow = new google.maps.InfoWindow(); 

// Set up a basic map. Optionally supply a centre:
// otherwise default to centre of Britain.
function set_up_map(centre_lat,centre_lng) {
	var latlng;
	var zoom_level;
    if (!centre_lat && !centre_lng) {
        latlng = new google.maps.LatLng(52.36187505907603, -1.614990234375);
        zoom_level = 6;
    } else {
        latlng = new google.maps.LatLng(centre_lat, centre_lng);	
        zoom_level = 8;
    }
    var myOptions = {
      zoom: zoom_level,
      scrollwheel: false,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      maxZoom: zoom_level+1,
      minZoom: zoom_level-1
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}


// We want to show a particular place. Add a marker for that place,
// and fill in other markers inside the map's bounds.
function show_place (lat, lng, place_name, grid, county, zoom_level) {
	var latlng = new google.maps.LatLng(lat, lng);
    var myOptions = {
      zoom: zoom_level,
	  scrollwheel: false,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      maxZoom: zoom_level+1,
      minZoom: zoom_level-1
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	var marker = new google.maps.Marker({
	      position: latlng,
	      map: map,
	      title: place_name,
	      zIndex: 5
	  });
	// When the map boundaries move, add new markers within the bounds.
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lat(), centreLng:map.getCenter().lng() }, function(json){
        for (i=0;i<json.length;i++) {
	      if ((json[i].grid != grid) && (json[i].vill != place_name)) {
		      var map_marker = addMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].vill_slug, json[i].hundred, json[i].county, json[i].raw_value);
		      //map_marker.setMap(map);
	      }
        }
       });
    });
}

// Turn a long float into a readable number.
function roundNumber(num) {
	var result = Math.round(num*Math.pow(10,1))/Math.pow(10,1);
	return result;
}

// Create text for search results page.
// And add markers within bounds.
function search_page(results_html) {
    results_html.innerHTML = "Loading results...";
    var html_set = false;
    var places_html = '<ul>';
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lat(), centreLng:map.getCenter().lng(), order_by_distance:'false' }, function(json){
        for (i=0;i<json.length;i++) {
		      var map_marker = addMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].vill_slug, json[i].hundred, json[i].county, json[i].raw_value);
		      places_html += "<li><a href='/place/" + json[i].grid + "/" + json[i].vill_slug + "'>" + json[i].vill +
		          "</a>, " + json[i].hundred + ", " + json[i].county + ", " + 
		          roundNumber(json[i].distance) + " km</li>";
        }
// <li><a href="{% url place place.grid place.vill_slug %}">{{place.vill}}</a>, {% for county in place.county.all %}{{ county }} {% endfor %}</li>
        if (!html_set) {
	      results_html.innerHTML = places_html + "</ul>";
	      html_set = true;
        }
      });
    });
}

// **************************************
// Add individual markers to the map.
// **************************************

//TODO: work out what to do about colours.  
function addMarker(lat, lng, grid, vill, vill_slug, hundred, county, raw_value, colour) {
	var map_marker = createMarker(lat, lng, grid, vill, vill_slug, hundred, county, raw_value, colour);
	//var mm = new GMarkerManager(map, {maxZoom:19});
	//mm.addMarker(marker,0,17); 
    //alert('zoom level: ');
    map_marker.setMap(map);
}

// Create an individual marker. Marker size depends on raw value.
// Marker colour depends on status if supplied, else on hundred.
function createMarker(lat, lng, grid, vill, vill_slug, hundred, county, raw_value, colour) {
	    var latlng = new google.maps.LatLng(lat, lng);
		var html = "<strong><a href=/place/" + grid + "/" + vill_slug + ">" + vill + "</a></strong><br/>" + hundred + ", " + county;
	    if (colour == 'Y') {
		      colour = "BEBEBE";
	    }
        var width = 0;
        var height = 0;
		raw_value = parseFloat(raw_value);
		//TODO: tidy these up. 
		if (raw_value > 10.0) {
			  height = 48;
			  width = 36;
		} else if (raw_value > 5.0) {
			  height = 40;
			  width = 30;
		} else if (raw_value > 3.0) {
			  height = 32;
			  width = 24;
		} else if (raw_value > 1.0) {
			  height = 24;
			  width = 18;
	   } else {
			  height = 16;
			  width = 12;
		}
        var size = new google.maps.Size(width,height);
	    var image_url = "http://chart.apis.google.com/chart?cht=mm&chs=" + width + "x" + height + "&chco=FFFFFF," + colour + ",000000&ext=.png";
		var image = new google.maps.MarkerImage(image_url, size, new google.maps.Point(0,0), new google.maps.Point(12, 32));
	    var shadow = new google.maps.MarkerImage('http://chart.apis.google.com/chart?chst=d_map_pin_shadow', new google.maps.Size(40, 37),new google.maps.Point(0,0), new google.maps.Point(12,35));

		var marker = new google.maps.Marker({
	      position: latlng, 
	      title: vill,
	      icon: image,
	      shadow: shadow,
	      zindex: 1, 
	    });
	    google.maps.event.addListener(marker, 'click', function() {
		  infowindow.close(); 
		  infowindow.setContent(html); 
		  infowindow.setPosition(marker.getPosition());
	      infowindow.open(map,marker);
	    });
		return marker;
}

// **************************************
// Retrieve querystrings for GET requests
// **************************************

window.location.querystring = (function() {
    // by Chris O'Brien, prettycode.org 
    var collection = {};
    // Gets the query string, starts with '?'
     var querystring = window.location.search;
    // Empty if no query string
    if (!querystring) {
        return { toString: function() { return ""; } };
    }
    // Decode query string and remove '?' 
    querystring = decodeURI(querystring.substring(1));
   // Load the key/values of the return collection
    var pairs = querystring.split("&");
    for (var i = 0; i < pairs.length; i++) {
        // Empty pair (e.g. ?key=val&&key2=val2)
        if (!pairs[i]) {
            continue;
        }
        // Don't use split("=") in case value has "=" in it
        var seperatorPosition = pairs[i].indexOf("=");
        if (seperatorPosition == -1) {
            collection[pairs[i]] = "";
        }
        else {
            collection[pairs[i].substring(0, seperatorPosition)] 
                = pairs[i].substr(seperatorPosition + 1);
        }
    }
    // toString() returns the key/value pairs concatenated 
    collection.toString = function() {
        return "?" + querystring;
    };
    return collection;
})();