const data = JSON.parse(formatArray(document.getElementById("data").innerHTML));
const predictions = JSON.parse(formatArray(document.getElementById("predictions").innerHTML));
const orderedData = orderData(data, predictions);

var margin = {top: 50, right: 250, bottom: 200, left: 150}
var width = window.innerWidth - margin.left*2 - margin.right*2
var height = window.innerHeight - margin.top*2 - margin.bottom*2

const frac = 5 // Fracción en la que se muestra el valor mínimo con respecto al resto de valores visibles en el momento