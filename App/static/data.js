// Convertir los datos a un formato que pueda utilizar por la app de visualización.
const data = JSON.parse(formatArray(document.getElementById("data").innerHTML));
const predictions = JSON.parse(formatArray(document.getElementById("predictions").innerHTML));
const smooth_predictions = JSON.parse(formatArray(document.getElementById("smooth_predictions").innerHTML));
const last_date = document.getElementById("last_date").innerHTML
const orderedData = orderData(data, predictions, smooth_predictions, last_date);

const quarterly_prediction = JSON.parse(formatJson(document.getElementById("quarterly_prediction").innerHTML));
var quarterly_info = ["",
                      "Quarterly Estimation",
                      "",
                      "Last quarter report: "+quarterly_prediction["start_date"],
                      "Clossing value: "+quarterly_prediction["last_clossing"],
                      "",
                      "Next quarter report: "+quarterly_prediction["destination_date"],
                      "Estimated value: "+quarterly_prediction["destination_value"].toFixed(2)]

var growth = ["",
              "Estimated growth from today until "+quarterly_prediction["destination_date"]+": ",
              (((quarterly_prediction["destination_value"]/data[data.length-1])*100)-100).toFixed(2)+"%",
              "",
              "",
              "* This should be taken as an estimation for trend rather than actual growth"]

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

// Tamaño y márgenes para el svg principal
var margin = {top: 50, right: 250, bottom: 200, left: 150}
var width = window.innerWidth - margin.left*2 - margin.right*2
var height = window.innerHeight - margin.top*2 - margin.bottom*2

const frac = 5 // Fracción en la que se muestra el valor mínimo con respecto al resto de valores visibles en el momento

var n = 0 // Inicializo el índice de los datos que se muestran en pantalla

// Leyenda del gráfico
var legend_keys = ["Real Closing Prices", "Predicted Closing Prices", "Smooth Prediction"]
var legend_colors = ["steelblue", "#10B998", "#6044DC"]