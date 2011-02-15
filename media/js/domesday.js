var map; 
var place_name = "";
var infowindow = new google.maps.InfoWindow(); 
var colours = ['FF0000', 'FFCCCC', '009966', 'FFFF66', '5B59BA'];
var h_colours = []; // associative array for hundreds <-> colours
var counter = 0;
var use_cluster = false; // Use MarkerClusterer for pages with many markers.



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
      maxZoom: zoom_level+2,
      minZoom: zoom_level-1
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}
// 
// function whole_map() {
// 	var center = new google.maps.LatLng(52.36187505907603, -1.614990234375);
// 	var options = {
// 	  'zoom': 7,
// 	  scrollwheel: false,
// 	  'center': center,
// 	  'mapTypeId': google.maps.MapTypeId.ROADMAP
// 	};
//     var markers = [];
// 	var map = new google.maps.Map(document.getElementById("map_canvas"), options);
// 	google.maps.event.addListener(map, 'tilesloaded', function() {
// 	    $.getJSON("/all_places_json/", function(json){
// 	      for (i=0;i<json.length;i++) {
// 		      // TODO: perhaps hundred boundaries in different colours
// 		      // var map_marker = createMarker(json[i].lat, json[i].lng, json[i].grid, 
// 		      // 			                   json[i].vill, json[i].vill_slug, json[i].hundred, 
// 		      // 		                       json[i].county, json[i].population);
// 			  var myLatlng = new google.maps.LatLng(json[i].lat, json[i].lng);
// 			  var map_marker = new google.maps.Marker({'position': myLatlng});
// 			  markers.push(map_marker);
// 	        }
// 		    alert(markers.length);
// 			var mc = new MarkerClusterer(map,markers);
// 	     });
// 	});
// }
var markers = new Array();

// We want to show a particular place. Add a marker for that place,
// and fill in other markers inside the map's bounds.
function show_place (lat, lng, place_name, slug, grid, hundred, county, population, zoom_level) {
	var latlng = new google.maps.LatLng(lat, lng);
    var myOptions = {
      zoom: zoom_level,
	  scrollwheel: false,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      maxZoom: zoom_level+2,
      minZoom: zoom_level-1
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	var marker = addMarker(lat, lng, grid, place_name, slug, hundred, county, population, "FF6666");
	markers.push(marker);
	// When the map boundaries move, add new markers within the bounds.
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lat(), centreLng:map.getCenter().lng() }, function(json){
        for (i=0;i<json.length;i++) {
	      if ((json[i].grid != grid) && (json[i].vill != place_name)) {
		      var map_marker = addMarker(json[i].lat, json[i].lng, json[i].grid, 
			                   json[i].vill, json[i].vill_slug, json[i].hundred, 
		                       json[i].county, json[i].population.toFixed(0));
			  markers.push(map_marker);
	      }
        }
       });
    });
    return markers;
}

// Turn a long float into a readable number.
function roundNumber(num) {
	var result = Math.round(num*Math.pow(10,1))/Math.pow(10,1);
	return result;
}

// Create text for search results page.
// And add markers within bounds.
function search_page(results_html) {
    var html_set = false;
    var places_html = '<ul>';
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lat(), centreLng:map.getCenter().lng(), order_by_distance:'false' }, function(json){
        for (i=0;i<json.length;i++) {
		      var map_marker = addMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].vill_slug, json[i].hundred, json[i].county, json[i].population.toFixed(0));
		      places_html += "<li><a href='/place/" + json[i].grid + "/" + json[i].vill_slug + "'>" + json[i].vill +
		          "</a>, " + json[i].hundred + ", " + json[i].county + ", " + 
		          roundNumber(json[i].distance) + " km</li>";
        }
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

//TODO: Enable per-hundred colouring for "whole map" page?
function addMarker(lat, lng, grid, vill, vill_slug, hundred, county, population, colour) {
	//alert(colour);
	if (colour==undefined) {
		colour = "6699FF";
		var use_hundreds = false;
		if (use_hundreds) {
			if (h_colours[hundred]==undefined) {
	             h_colours[hundred] = colours[counter];
	             colour = colours[counter];
	             counter += 1;
	             if (counter>=colours.length) {
	                 counter=0;
	             }	 
	        }
	   }
    }
	var map_marker = createMarker(lat, lng, grid, vill, vill_slug, hundred, county, population, colour);
    map_marker.setMap(map);
}

function get_context(number, context_type) {
 //   alert(number + context_type);
    var width = 0;
    var height = 0;
    var context = '';
	if (context_type=="POPULATION") {
	 if (number > 34.0) {
			  height = 32;
			  width = 24;
			  context = "very large";
		} else if (number > 20.0) {
			  height = 28;
			  width = 21;
			  context = "quite large";
		} else if (number > 11.0) {
			  height = 24;
			  width = 18;
			  context = "medium";
		} else if (number > 5.46) {
			  height = 20;
			  width = 15;
			  context = "quite small";
	   } else if (number==0) {
			  height = 16;
			  width = 12;
			  context = "not given";
	    } else {
				  height = 16;
				  width = 12;
				  context = "very small";
		    }
	}
	return [height, width, context];
}

// Create an individual marker. Marker size depends on raw value.
// Marker colour depends on status if supplied, else on hundred.
function createMarker(lat, lng, grid, vill, vill_slug, hundred, county, population, colour) {
	    var latlng = new google.maps.LatLng(lat, lng);
        if (colour==undefined) {
	        colour="3366CC";
        }
		var html = "<strong><a href=/place/" + grid + "/" + vill_slug + ">" + vill + "</a></strong><br/>";
		if (hundred!=undefined) {
		    html += hundred + ", ";			
		} 
		html += county + "<br/>Population: " + population;
		population = parseFloat(population); 
        var results = get_context(population, "POPULATION");
        var height = results[0];
        var width = results[1];
        var context = results[2];
		html += " (" + context + ")";
	    var image_url = "http://chart.apis.google.com/chart?cht=mm&chs=" + width + "x" + 
	                         height + "&chco=FFFFFF," + colour + ",000000&ext=.png";
		var image = new google.maps.MarkerImage(image_url, new google.maps.Size(width,height), 
		               new google.maps.Point(0,0), new google.maps.Point(width/2,height));
        var shadowOrigin = new google.maps.Point(Math.ceil(height*0.3), Math.ceil(height*0.9));
        var shadowDimensions = new google.maps.Size(height, Math.ceil(height*0.9));
	    var shadow = new google.maps.MarkerImage('http://chart.apis.google.com/chart?chst=d_map_pin_shadow', 
	                 new google.maps.Size(40,37), new google.maps.Point(0,0), shadowOrigin, 
	                 shadowDimensions);
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

// **************************************
// Get random number in a range.
// **************************************
function randomFromTo(from, to){
       return Math.floor(Math.random() * (to - from + 1) + from);
}