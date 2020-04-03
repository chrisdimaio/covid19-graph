$.getJSON("data/options.json", function(result) {
  var $dropdown = $("#states");
  $.each(result, function() {
    $dropdown.append($("<option />").val(this.dataset).text(this.name));
  });
});

var state_selector = document.getElementById("states");
state_selector.addEventListener("change", function() {
  updateData("data/" + state_selector.options[state_selector.selectedIndex].value);
});

lineChartData = {
  labels: [],
  datasets: [{
    label: "New Cases",
    borderColor: window.chartColors.blue,
    backgroundColor: window.chartColors.blue,
    fill: false,
    data: [],
    yAxisID: 'y-axis-1',
  }
  ,{
    label: 'New Deaths',
    borderColor: window.chartColors.red,
    backgroundColor: window.chartColors.red,
    fill: false,
    data: [],
    yAxisID: 'y-axis-1'
  }
  ,{
    label: 'Death Rate',
    borderColor: window.chartColors.yellow,
    backgroundColor: window.chartColors.yellow,
    fill: false,
    data: [],
    yAxisID: 'y-axis-2'
  }
]
};

window.onload = function() {
  var ctx = document.getElementById('canvas').getContext('2d');
  window.myLine = Chart.Line(ctx, {
    data: lineChartData,
    options: {
      responsive: true,
      hoverMode: 'index',
      stacked: false,
      title: {
        display: true,
        text: 'Chart.js Line Chart - Multi Axis'
      },
      scales: {
        yAxes: [{
          type: 'linear',
          display: true,
          position: 'left',
          id: 'y-axis-1',

          scaleLabel: {
              display: true,
              labelString: "Number of people"
          },

          ticks: {
              stepSize: 1000
          }
        }, {
          type: 'linear',
          display: true,
          position: 'right',
          id: 'y-axis-2',
          scaleLabel: {
              display: true,
              labelString: "Death rate"
          },

          gridLines: {
            drawOnChartArea: false,
            },
          ticks: {
              beginAtZero: true,

              callback: function(value, index, values) {
                  return value + '%';
              }
          }
        }],
      }
    }
  });
};

function numberWithCommas(n) {
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function updateData(url){
  $.getJSON(url, function(data){
    // Remove all the days up until the first death.
    if(data.first_death > 0){
      predeath_days = data.first_death - 1;
    } else {
      predeath_days = 0;
    }
    window.myLine.options.title.text = data.title;

    // Cases, deaths, and dates are all the same length.
    last = data.cases.length - 1;
    document.getElementById("t_cases").innerHTML = numberWithCommas(data.cases[last]);
    document.getElementById("t_deaths").innerHTML = numberWithCommas(data.deaths[last]);

    lineChartData.labels = data.dates.slice(predeath_days);
    lineChartData.datasets[0].data = data.new_cases.slice(predeath_days);
    lineChartData.datasets[1].data = data.new_deaths.slice(predeath_days);
    lineChartData.datasets[2].data = data.rates.slice(predeath_days);
  }).done(function() {
    window.myLine.update();
  }).fail(function(e) {
    console.log( e );
  });
};
updateData("data/us.json");