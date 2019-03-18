// Two series:
// https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/stock/demo/compare/
$(document).ready(function() {
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
          title: {
              text: 'Temperatures (C)'
          },
          series: [{
              name: 'Temp',
              data: convertData(data),
              tooltip: {
                  valueDecimals: 1
              },
          }]
      });
    });
  }

  function weightChart(hog_code) {
    var temp_url = '/api/measurements/?location=' + location_code + '&hog='+hog_code+'&measurement_type=weight&page_size=1000';
    $.getJSON(temp_url, function (data) {
      // Create the chart
      Highcharts.stockChart('weight-container-' + hog_code, {
          rangeSelector: {
              selected: 1
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
