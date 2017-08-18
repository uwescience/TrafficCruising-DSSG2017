function filter(specified_fhv, specified_day,specified_hour){
  var dataurl = '/data/'+specified_fhv+'/'+specified_day+'/'+specified_hour;
  $.ajax({
      url: dataurl,
      async: false,
      dataType : "json",
      success:  function(data) {
          frequencies = data;
      }});
}
