// Two series:
// https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/stock/demo/compare/
$(document).ready(function() {
  window.adjusting = false;

  function convertData(data) {
    data = $.map(data['results'], function(a) {
      var d = new Date(a['observed_at']).getTime();
       return [[d, a['measurement']]];
     });
   return data;
  };
  function tempChart() {
    var temp_url = '/api/measurements/?location=' + location_code + '&measurement_type=in_temp&page_size=1000';
    $.getJSON(temp_url, function (data) {
      // Create the chart
      Highcharts.stockChart('temp-container', {
        rangeSelector: {
          selected: 1
        },
        xAxis: {
          startOnTick: true,
          endOnTick: true,
          min: min_date,
          max: max_date,
          events: {
            setExtremes: function (e) {
              syncExtremes(e.min, e.max, 'temp-container');
            }
          }
        },
        title: {
          text: 'Temperatures (C)'
        },
        series: [{
          name: 'Temp',
          data: convertData(data),
          tooltip: {
            valueDecimals: 1
          }
        }]
      });
    });
  }

  function syncExtremes(min, max, source_chart_id) {
    if (!adjusting) {
    if (!window.adjusting) {
      window.adjusting = true;
      $.each($('.measurement-chart'), function(i, chart) {
        if (chart.id !== source_chart_id) {
          chart = $(chart).highcharts();
          chart.xAxis[0].setExtremes(min, max);
        }
      });
      window.adjusting = false;
    }
  }

  function weightChart(hog_code) {
    var temp_url = '/api/measurements/?location=' + location_code + '&hog='+hog_code+'&measurement_type=weight&page_size=1000';
    $.getJSON(temp_url, function (data) {
      // Create the chart
      var chart_id = 'weight-container-' + hog_code;
      Highcharts.stockChart(chart_id, {
        rangeSelector: {
          selected: 1
        },
        navigator: {
          enabled: false
        },
        xAxis: {
          startOnTick: true,
          endOnTick: true,
          min: min_date,
          max: max_date,
          events: {
            setExtremes: function (e) {
              syncExtremes(e.min, e.max, chart_id);
            }
          }
        },
        title: {
          text: 'Weight (g)'
        },
        series: [{
          name: 'Weight',
          data: convertData(data),
          tooltip: {
            valueDecimals: 1
          },
        }]
      });
    });
  }
  tempChart();
  $.each(hog_codes, function(i, code) {
    weightChart(code);
  });
});;
