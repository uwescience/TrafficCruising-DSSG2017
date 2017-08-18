function drawchart(width) {
  var vhf = '';
  var day = '';
  var time = '';
  $('.cruising_button.active').each(function() {
    vhf = $(this).attr('id');
  });
  $('.day_button.active').each(function() {
    day = $(this).attr('id');
  });
  $('.time_button.active').each(function() {
    time = $(this).attr('id');
  });
  if(vhf=='Parking')
  {var url = "chart_data_cruising/" + day + "/" + time;}
  else
  {var url = "chart_data_vhf/" + day + "/" + time;}

  var vlSpec = {
    "$schema": "https://vega.github.io/schema/vega-lite/v2.json",
    "width": 500,
    "height": 120,
    "padding": 10,
    "data": {
    "url":url},
    "layer": [{
        "mark": {
          "type": "area",
          "interpolate": "monotone"
        },
        "encoding": {
          "x": {
            "field": "time",
            "type": "temporal",
            "axis": {
              "format": "%I%p",
              "labelAngle": 0,
              "title": "TIME",
              "tickCount": 23
            }
          },
          "y": {
            "field": "count",
            "type": "quantitative",
            "axis": {
              "title": "CRUISING VOLUME"
            }
          },
          "color": {
            "value": "#1bbc9b"
          },
          "opacity": {
            "value": 0.5
          }
        }
      },{
        "mark": {
          "type": "line",
          "interpolate": "monotone"
        },
        "encoding": {
          "x": {
            "field": "time",
            "type": "temporal",
            "axis": null
          },
          "y": {
            "field": "count",
            "type": "quantitative",
            "axis": null
          },
          "color": {
            "value": "#16a086"
          },
          "opacity": {
            "value": 1
          }
        }
      },
      {
        "mark": {
          "type": "circle",
          "interpolate": "monotone"
        },
        "encoding": {
          "x": {
            "field": "time",
            "type": "temporal",
            "axis": null
          },
          "y": {
            "field": "count",
            "type": "quantitative",
            "axis": {
                "labels": "false"
            }
          },
          "color": {
            "value": "#FFFFFF"
          },
          "opacity": {
            "value": 1
          },
          "tooltip": {"field": "count","type": "quantitative"}
        }
      },{
    "mark": "rect",
    "encoding": {
      "x": {
          "field": "start",
          "aggregate": "min",
          "type": "temporal"},
      "x2": {
          "field": "end",
          "aggregate": "max",
          "type": "temporal"},
      "opacity": {"value": 0.2},
      "color": {"value":"purple"}
    }
  }
    ],
    "config": {
      "axis": {
        "domainColor": "#FFFFFF",
        "labelColor": "#FFFFFF",
        "titleColor": "#FFFFFF",
        "titlePadding": 10,
        "gridOpacity": 0,
        "tickColor": "#FFFFFF",
        "titleFont": "Montserrat"
      }
    }
  };

  var opt = {
    mode: "vega-lite",

  };

  vega.embed("#chart", vlSpec, opt);
}
