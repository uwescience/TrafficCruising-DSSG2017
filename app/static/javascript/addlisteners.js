$('#Monday').addClass("active");
$('#All').addClass("active");
$('#Parking').addClass("active");
initializemap();
drawmap();
drawchart($(window).width());

$(window).load(function() {
  $('button.day_button').click(function() {
  $('button.day_button').removeClass("active");
  $(this).addClass("active");
  drawmap();
  drawchart($(window).width());
  });
});

$(window).load(function() {
  $('button.time_button').click(function() {
  $('button.time_button').removeClass("active");
  $(this).addClass("active");
  drawmap();
  drawchart($(window).width());
  });
});

$(window).load(function() {
  $('button.cruising_button').click(function() {
  $('button.cruising_button').removeClass("active");
  $(this).addClass("active");
  drawmap();
  drawchart($(window).width());
  });
});

$(window).resize(function() {
    drawchart($(this).width());
});
