//this query generates both nodes (intersections) and ways linking those intersections (though the set of ways is incomplete and will have to be supplemented with a manual search).

//config
[out:json];

//find all roads (ways) in our area
way[~'highway'~'(primary|motorway_link|trunk|unclassified|secondary|tertiary)',i](poly:'47.5990545 -122.339534 47.5990545 -122.325 47.6048794 -122.324 47.6135283 -122.3286935 47.616282 -122.333556 47.6166472 -122.3381133 47.6096411 -122.346')-> .ways;

//get all nodes associated with them
.ways > -> .nodes;

//isolate intersection nodes
node(w.ways)[~'(highway|crossing)'~'(traffic_signals|stop)',i][highway!='crossing'] -> .int;

//remove extraneous nodes (may want to keep 1710594753)
(.int; - node(id:2700939603,2700939605,1710594753,3669043686,53086663,53086664,53086666,53086667,53086670,53086671,53086673,53070140,53070139,53070138,53070135,53070134,53201468,53203470,53144746,53247506,53155734,53200381,53070534,53200379,53070531,53184116,53070522,53208938,1926509619,1926509541,1710594762,1710594756,53129286,53082159,4032154590,53128667,53129297,53088986,1710594754,3295705106,53088988,53088990,53088992,53088997,53088998,53088999,53082266,53166904,53225171,53114050,53166871,53129298,53184117,53205958,699288163,53200379,53142974,53099752,30345078,53194070,53194069);) -> .int;

//include others manually by ID (some of these are from 1-2 levels outward of sensors)
node(id:53160855,53142141,825293231,825293232,53114273,53114269,53114260,53071878,53071879,1806527515,53071883,289462720,53114230,1806299915,53155725,53144256,1827149469,53155727,1178349141,53141794) -> .manual;
//add some more (these are all from 1-2 levels outward of sensors)
node(id:53207669,53142103,53221390,53119471,53200379,699288163,53144266,1926509564,2507567756,289461267,132880545,53168038,289460726,53082157,53168044) -> .manual2;

//combine node sets
(.int; .manual; .manual2;) -> .int;
//.int out; //uncomment this to export/explore all intersections

//get all ways associated with intersections, now that theyve been curated
way(bn.int) -> .ways2;
//.ways2 out; //uncomment this to export/explore SOME ways

//get more ways (uncomment the next two lines to see additional metadata)
//(.nodes; .ways;) -> .all;
//.all out;

//export/explore all nodes in view, if you want to focus on an area (make sure view is small)
/*node({{bbox}}); out;*/
