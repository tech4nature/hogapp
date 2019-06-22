// Two series:
// https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/stock/demo/compare/
$(document).ready(function() {
  window.adjusting = false;
  window.minRange = 3 * 24 * 60 * 60 * 1000;
  function buildUrl(measurement_type, resolution, location_code, hog_code) {
    var url = '/api/measurements/?measurement_type=' + measurement_type;
    if (typeof location_code !== 'undefined')
      url += '&location=' + location_code;
    if (typeof hog_code !== 'undefined')
      url += '&hog=' + hog_code;
    if (typeof resolution !== 'undefined')
      url += '&resolution=' + resolution;
    return url;
  }

  function getMeasurements(data) {
    data = $.map(data, function(a) {
      var d = new Date(a['observed_at']).getTime();
      var point = [[d, a['measurement']]];
      return point;
    });
    return data;
  }

  function tempChart() {
    // Create the chart
    return Highcharts.stockChart('temp-container', {
        chart: {
          type: 'column'
        },
        rangeSelector: {
          selected: 0  // 1 month
        },
        xAxis: {
          type: 'datetime',
          minRange: window.minRange,
          startOnTick: false,
          endOnTick: false,
          min: min_date,
          max: max_date,
        },
        yAxis: {
          opposite: false,
          title: {
            text: "Temperature"
          }
        },
        title: {
          text: 'Temperatures (C)'
        },
        series: [
          {
            name: 'Inside temp',
            color: '#28a745',
            tooltip: {
              valueDecimals: 1
            }
          },
          {
            name: 'Outside temp',
            color: '#17a2b8',
            tooltip: {
              valueDecimals: 1
            }
          },
        ]
    });
  }

  function weightChart(hog_code) {
    // Create the chart
    var initial_min_date = new Date(max_date);
    initial_min_date.setMonth(initial_min_date.getMonth() - 1);
    var chart_id = 'weight-container-' + hog_code;
    console.log(initial_min_date, new Date(max_date));
    return Highcharts.chart(chart_id, {
        chart: {
          type: 'column'
        },
        rangeSelector: {
          selected: 1
        },
        navigator: {
          enabled: true
        },
        plotOptions: {
          series: {
            pointWidth: 10,
            groupPadding: 0
          }
        },
        xAxis: {
          type: 'datetime',
          startOnTick: false,
          endOnTick: false,
          min: min_date,
          max: max_date,
        },
        title: {
          text: 'Weight (g)'
        },
        series: [{
          name: 'Weight',
          color: '#ffc107',
          tooltip: {
            valueDecimals: 1
          }
        }]
      });
  }

  function setSeriesData(chart, url, series_index) {
    $.getJSON(url, function (data) {
      chart.series[series_index].setData(getMeasurements(data));
      //chart.redraw();
    });
  }

  function updateChart(chart_id, resolution, location_code, hog_code) {
    var metrics;
    if (chart_id == 'temp-container') {
      metrics = ['in_temp', 'out_temp'];
    } else if (chart_id.lastIndexOf('weight-container', 0) === 0) {
      metrics = ['weight'];
    }
    $chart = $('#' + chart_id);
    $chart.data('metrics', metrics);
    $.each(metrics, function(i, metric) {
      var url = buildUrl(metric, resolution, location_code, hog_code);
      var series_index = 0;
      setSeriesData($chart.highcharts(), url, i);
      $chart.data('resolution', resolution);
      $chart.data('location_code', location_code);
      $chart.data('hog_code', hog_code);
    });
  }

  function drawCharts() {
    if (typeof max_date !== 'undefined' && typeof min_date !== 'undefined' && typeof initial_resolution !== 'undefined') {
      if (typeof location_code !== 'undefined') {
        if($('#temp-container').length > 0) {
          chart = tempChart();
          updateChart('temp-container', initial_resolution, location_code);
        }
      }
      if (typeof hog_code !== 'undefined') {
        chart = weightChart(hog_code);
        updateChart('weight-container-' + hog_code, initial_resolution, location_code, hog_code);
      }
    }
  }

  function loadWall(hog_code, location_code, most_recent_id) {
    var url = '/card_wall_fragment?';
    if (typeof most_recent_id !== 'undefined') {
      url += 'most_recent_id=' + most_recent_id + '&';
    }
    if (typeof hog_code !== 'undefined') {
      url += 'hog=' + hog_code + '&';
    }
    if (typeof location_code !== 'undefined') {
      url += 'location=' + location_code + '&';
    }
    $.ajax({
      url: url
    }).done(
      function(data){
        $('#loading').hide();
        $('#card-wall').append(data);
      }
    );
  }
  var hog_code;
  var location_code;
  drawCharts();

  var most_recent_id;
  if (window.location.hash) {
    // subtract one so we jump to the right one
    most_recent_id = parseInt(window.location.hash.substring(1)) + 1;
  }
  loadWall(hog_code, location_code, most_recent_id);

  $(document.body).on('touchmove', onScroll); // for mobile
  $(window).on('scroll', onScroll);



  // Tooltip

  function setTooltip(btn, message) {
    $(btn).tooltip('hide')
      .attr('title', message)
      .tooltip('show');
  }

  function hideTooltip(btn) {
    setTimeout(function() {
      $(btn).tooltip('hide');
    }, 1000);
  }

  clipboard = new ClipboardJS('.measure-link');

  clipboard.on('error', function(e) {
    var link = $(e.trigger).next()
    link.css('visibility', 'visible');
    setTooltip(link, 'Press Ctrl+C to copy');
    hideTooltip(link);
  });

  clipboard.on('success', function(e) {
    var link = $(e.trigger).next()
    link.css('margin', 0);
    setTooltip(link, 'Copied!');
    hideTooltip(link);
  });
  function onScroll() {
    if($(window).scrollTop() + $(window).height() > $(document).height() - 50) {
      var loader = $('#load-more-cards');
      var most_recent_id = loader.data('most-recent-id');
      if (most_recent_id) {
        loader.remove();
        loadWall(hog_code, location_code, most_recent_id);
      }
   }
  }

});;
