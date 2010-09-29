var map; 
var place_name = "";
var infowindow = new google.maps.InfoWindow(); 

function set_up_map() {
    var latlng = new google.maps.LatLng(52.36187505907603, -1.614990234375);
    var myOptions = {
      zoom: 6,
      scrollwheel: false,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
}

function addMarker(lat, lng, grid, vill, hundred, county, holding, units, waste86, colour) {
	var map_marker = createMarker(lat, lng, grid, vill, hundred, county, holding, units, colour);
    map_marker.setMap(map);
}

function show_place (lat, lng, place_name, grid, county, zoom_level) {
	var latlng = new google.maps.LatLng(lat, lng);
    var myOptions = {
      zoom: zoom_level,
	  scrollwheel: false,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      //alert("places = Place.objects.filter(lat__range=("+ bounds.getSouthWest().lat() + ", " + bounds.getNorthEast().lat() + "),lon_range=(" + bounds.getSouthWest().lng() + ", " + bounds.getNorthEast().lng() + "))");
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lng(), centreLng:map.getCenter().lng(), order_by_distance:'false'}, function(json){
        for (i=0;i<json.length;i++) {
	      if ((json[i].grid != grid) && (json[i].vill != place_name)) {
		      var map_marker = createMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].hundred, json[i].county, json[i].holding, json[i].units, json[i].waste86);
		      map_marker.setMap(map);
	      }
        }
        var marker = new google.maps.Marker({
           position: latlng, 
           map: map, 
           title: place_name,
           zIndex: 5
         });
       });
    });
}

function search_page(results_html) {
    results_html.innerHTML = "Loading results...";
    var html_set = false;
    var places_html = '<ul>';
	google.maps.event.addListener(map, 'tilesloaded', function() {
      var bounds = map.getBounds();
      $.getJSON("/markers_within_bounds/", { swLat:bounds.getSouthWest().lat(), swLng:bounds.getSouthWest().lng(),neLat:bounds.getNorthEast().lat(), neLng:bounds.getNorthEast().lng(), centreLat:map.getCenter().lng(), centreLng:map.getCenter().lng(), order_by_distance:'false' }, function(json){
        for (i=0;i<json.length;i++) {
		      var map_marker = createMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].hundred, json[i].county, json[i].holding, json[i].units, json[i].waste86);
		      map_marker.setMap(map);
		      places_html += "<li><a href='/place/" + json[i].grid + "/" + json[i].vill + "'>" + json[i].vill + "</a>, " + json[i].county + ", value " + json[i].holding + " " + json[i].units + "</li>";
        }
        if (!html_set) {
	      results_html.innerHTML = places_html + "</ul>";
	      html_set = true;
        }
      });
    });
}

function whole_map() {
	    var latlng = new google.maps.LatLng(52.36187505907603, -1.614990234375);
	    var myOptions = {
	      zoom: 7,
	      scrollwheel: false,
	      center: latlng,
	      mapTypeId: google.maps.MapTypeId.ROADMAP
	    };
        map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
        markers = []
        $.getJSON("/all_markers/", {}, function(json) {
          for (i=0;i<json.length;i++) {
		      var map_marker = createMarker(json[i].lat, json[i].lng, json[i].grid, json[i].vill, json[i].hundred, json[i].county, json[i].holding, json[i].units, json[i].waste86);
		      markers.push(map_marker);
          }
        });
		//for(var i = 0; i < places_json.places.length ; i++) {
		//     var latlng = new google.maps.LatLng(places_json.places[i].lat, places_json.places[i].lon);
	    //	   var title = places_json.places[i].vill;
		//     var html = "<strong><a href=/place/" + places_json.places[i].grid + "/" + encodeURI(places_json.places[i].vill) + ">" + places_json.places[i].vill + "</a></strong><br/>" + places_json.places[i].county;
		//     var marker = createMarker(latlng, title, html, colour);
		//     markers.push(marker);
		//}
		var markerCluster = new MarkerClusterer(map, markers, {maxZoom: 10});
}

// Create an individual marker
function createMarker(lat, lng, grid, vill, hundred, county, holding, units, colour) {
	    var latlng = new google.maps.LatLng(lat, lng);
		var html = "<strong><a href=/place/" + grid + "/" + encodeURI(vill) + ">" + vill + "</a></strong><br/>" + hundred + ", " + county + ", value " + holding + " " + units;
	    if (colour == 'Y') {
		      colour = "BEBEBE";
	    }
	    var image_url = "http://chart.apis.google.com/chart?cht=mm&chs=24x32&chco=FFFFFF," + colour + ",000000&ext=.png";
		var image = new google.maps.MarkerImage(image_url, new google.maps.Size(24, 32),new google.maps.Point(0,0), new google.maps.Point(12, 32));
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