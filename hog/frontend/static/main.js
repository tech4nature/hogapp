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
    if (!window.adjusting && (max - min) > window.minRange) {
      window.adjusting = true;
      // adjust x-axis resolution we get from server based on zoom level
      $.each($('.measurement-chart'), function(i, chart) {
        $chart = $(chart);
        hc_chart = $(chart).highcharts();
        var update_data = false;
        var hour = 60 * 60 * 1000;
        var one_day = 24 * 60 * 60 * 1000;
        if ($chart.data('resolution') == 'day' && (max - min) < 7 * one_day) {
          $chart.data('resolution', 'hour');
          update_data = true;
        } else if ($chart.data('resolution') == 'hour' && (max - min) >= 7 * one_day) {
          $chart.data('resolution', 'day');
          update_data = true;
        }
        if (update_data) {
          updateChart(
            $chart.attr('id'),
            $chart.data('resolution'),
            $chart.data('location_code'),
            $chart.data('hog_code'));
        }
        // make all other charts match the same zoom level
        if (chart.id !== source_chart_id) {
          var redraw = true;
          var animation = false;
          hc_chart.xAxis[0].setExtremes(min, max, redraw, animation);
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

  chart = tempChart();
  updateChart('temp-container', initial_resolution, location_code);
  $.each(hog_codes, function(i, hog_code) {
    chart = weightChart(hog_code);
    updateChart('weight-container-' + hog_code, initial_resolution, location_code, hog_code);
  });
});;
