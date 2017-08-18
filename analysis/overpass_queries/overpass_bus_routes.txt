//overpass turbo query for visualizing bus routes

//config
[out:json][timeout:60];

//get all nodes and ways associated with bus routes connected to our area
(
  relation["type"="route"]["route"="bus"](poly:'47.5990545 -122.339534 47.5990545 -122.325 47.6048794 -122.324 47.6135283 -122.3286935 47.616282 -122.333556 47.6166472 -122.3381133 47.6096411 -122.346');
);

// print results
out body;
>;
out skel qt;

