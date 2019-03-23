// Two series:
// https://jsfiddle.net/gh/get/library/pure/highcharts/highcharts/tree/master/samples/stock/demo/compare/
$(document).ready(function() {
  window.adjusting = false;

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
    console.log(data);
    return data;
  }

  function tempChart() {
      // Create the chart
    return Highcharts.stockChart('temp-container', {
        rangeSelector: {
          selected: 0  // 1 month
        },
        xAxis: {
          type: 'datetime',
          startOnTick: false,
          endOnTick: false,
          min: min_date,
          max: max_date,
          events: {
            setExtremes: function (e) {
              syncExtremes(e.min, e.max, 'temp-container');
            }
          }
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
            tooltip: {
              valueDecimals: 1
            }
          },
          {
            name: 'Outside temp',
            tooltip: {
              valueDecimals: 1
            }
          },
        ]
    });
  }

  function syncExtremes(min, max, source_chart_id) {
    if (!window.adjusting) {
      window.adjusting = true;
      $.each($('.measurement-chart'), function(i, chart) {
        if (chart.id !== source_chart_id) {
          chart = $(chart).highcharts();
          var redraw = true;
          var animation = false;
          // XXX - if extremes are sufficiently low,
          chart.xAxis[0].setExtremes(min, max, redraw, animation);
        }
      });
      window.adjusting = false;
    }
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
          enabled: false
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
          min: initial_min_date.getTime(),
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
          tooltip: {
            valueDecimals: 1
          }
        }]
      });
  }

  function setSeriesData(chart, url, series_index) {
    $.getJSON(url, function (data) {
      chart.series[series_index].setData(getMeasurements(data));
    });
  }

  function updateChart(chart, metric, resolution, location_code, hog_code) {
    var url = buildUrl(metric, resolution, location_code, hog_code);
    var series_index = 0;
    if (metric === 'out_temp')
      series_index = 1;
    setSeriesData(chart, url, series_index);
  }

  chart = tempChart();
  updateChart(chart, 'in_temp', 'day', location_code);
  updateChart(chart, 'out_temp', 'day', location_code);
  $.each(hog_codes, function(i, hog_code) {
    chart = weightChart(hog_code, 'day');
    updateChart(chart, 'weight', 'day', location_code, hog_code);
  });
});;
