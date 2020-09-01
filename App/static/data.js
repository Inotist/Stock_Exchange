const data = JSON.parse(formatArray(document.getElementById("data").innerHTML));
const predictions = JSON.parse(formatArray(document.getElementById("predictions").innerHTML));
const smooth_predictions = JSON.parse(formatArray(document.getElementById("smooth_predictions").innerHTML));
const orderedData = orderData(data, predictions, smooth_predictions);

orderedData.forEach(function (d) {
  d[0].forEach(function (f) {
    f[0] = parseTime(f[0]);
  });
  d[1].forEach(function (f) {
    f[0] = parseTime(f[0]);
  });
  if (d.length == 3) {
  	d[2].forEach(function (f) {
      f[0] = parseTime(f[0]);
  	});
  };
})

var margin = {top: 50, right: 250, bottom: 200, left: 150}
var width = window.innerWidth - margin.left*2 - margin.right*2
var height = window.innerHeight - margin.top*2 - margin.bottom*2

const frac = 5 // Fracción en la que se muestra el valor mínimo con respecto al resto de valores visibles en el momento

var n = 0 // Inicializo el índice de los datos que se muestran en pantalla

var legend_keys = ["Real Closing Prices", "Predicted Closing Prices", "Smooth Prediction"]
var legend_colors = ["steelblue", "#10B998", "#6044DC"]