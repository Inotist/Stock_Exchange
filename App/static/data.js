const data = JSON.parse(formatArray(document.getElementById("data").innerHTML));
const predictions = JSON.parse(formatArray(document.getElementById("predictions").innerHTML));
const orderedData = orderData(data, predictions);

const margin = {top: 20, right: 20, bottom: 70, left: 40}
const width = 600 - margin.left - margin.right
const height = 300 - margin.top - margin.bottom

const frac = 5 // Fracción en la que se muestra el valor mínimo con respecto al resto de valores visibles en el momento