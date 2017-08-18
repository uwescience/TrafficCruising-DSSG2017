  //Produce map in my style
  var map = L.map('map', {
    center: [47.608013, -122.335167],
    maxZoom: 15,
    minZoom: 15,
    zoom: 15
  });
  var alreadyLegend = false;
  var legend;
  var array;

  function getColor(x) {
    return x < array[1] ? '#fced00' :
      x < array[2] ? '#82e434' :
      x < array[3] ? '#00d363' :
      x < array[4] ? '#00bf7d' :
      x < array[5] ? '#00a48b' :
      x < array[6] ? '#008a90' :
      x < array[7] ? '#1a6d90' :
      x < array[8] ? '#3b4e8d' :
      x < array[9] ? '#4d2883' :
      '#52006a';
  };

  function initializemap() {
    //L.tileLayer( 'https://api.mapbox.com/styles/v1/bmbejcek/cj4hmjhpe3lw12so50j0nls7f/tiles/256/{z}/{x}/{y}@2x?access_token=pk.eyJ1IjoiYm1iZWpjZWsiLCJhIjoiY2o0ZWd4MnhnMHZmMzJ3cnQ4d2ZrdnlqYSJ9.0KITBSwJ16BtTG7anJz5OA', {
    L.tileLayer('https://api.mapbox.com/styles/v1/bmbejcek/cj5vhhjge6iqa2rmkgqdzdq5c/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiYm1iZWpjZWsiLCJhIjoiY2o0ZWd4MnhnMHZmMzJ3cnQ4d2ZrdnlqYSJ9.0KITBSwJ16BtTG7anJz5OA', {
      subdomains: ['a', 'b', 'c']
    }).addTo(map);

    //Return color of line segment
  }

  function addlegend(fhv, day, hour) {
    var legendurl = '/legend/' + fhv + '/' + day + '/' + hour;
    $.ajax({
      url: legendurl,
      async: false,
      dataType: "json",
      success: function(data) {
        array = data;
      }
    });

    legend = L.control({
      position: 'bottomleft'
    });
    legend.onAdd = function(map) {

      var div = L.DomUtil.create('div', 'info legend');
      // loop through our density intervals and generate a label with a colored square for each interval
      div.innerHTML += '<p style= "text-align:center">CRUISING<br>VOLUME</p>'
      for (var i = 0; i < array.length; i++) {
        div.innerHTML +=
          '<i style="background:' + getColor(array[i]) + '"></i> ' +
          array[i] + ((array[i + 1] - 1) ? ' &ndash; ' + (array[i + 1] - 1) + '<br>' : '+');
      }

      return div;
    };

    legend.addTo(map);
  }

  function removelegend() {
    map.removeControl(legend);
  }

  function drawmap() {

    var fhv = '';
    $('.cruising_button.active').each(function() {
      fhv = $(this).attr('id');
    });

    var day = '';
    $('.day_button.active').each(function() {
      day = $(this).attr('id');
    });

    var hour = '';
    $('.time_button.active').each(function() {
      hour = $(this).attr('id');
    });

    filter(fhv, day, hour);
    //Plot Line Segments
    clearMap();

    if (alreadyLegend) {
      removelegend();
    }
    alreadyLegend = true;
    addlegend(fhv, day, hour);
    // for (var i=0; i < base_layer.length; ++i )
    //   {
    //     var pointList = [([base_layer[i].start_lat,base_layer[i].start_lon]),([base_layer[i].end_lat,base_layer[i].end_lon])];
    //     var polyline = new L.Polyline(pointList, { color: getColor(0), interactive: false, weight: 5, opacity: 1, smoothFactor: 1, lineCap: "square" }).addTo(map);
    //   }

    for (var i = 0; i < frequencies.length; ++i) {
      var pointList = [([frequencies[i].start_lat, frequencies[i].start_lon]), ([frequencies[i].end_lat, frequencies[i].end_lon])];
      var polyline = new L.Polyline(pointList, {
        color: getColor(frequencies[i].count),
        interactive: false,
        weight: 5,
        opacity: 1,
        smoothFactor: 1,
        lineCap: "square"
      }).addTo(map);
    }

    //Plot Intersections
    for (var i = 0; i < intersections.length; ++i) {
      //var markers = new L.CircleMarker(new L.LatLng(intersections[i].intersection_lat, intersections[i].intersection_lon),{fillOpacity: 1, color: 'white', radius: 4}).addTo(map);
    }

  }

  function clearMap() {
    for (i in map._layers) {
      if (map._layers[i]._path != undefined) {
        try {
          map.removeLayer(map._layers[i]);
        } catch (e) {
          console.log("problem with " + e + map._layers[i]);
        }
      }
    }
  }
