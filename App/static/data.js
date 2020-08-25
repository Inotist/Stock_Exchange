const ticks = 10 // Sensibilidad del gráfico
const days = 10 // Número de días que se muestran a la vez

const margin = {top: 20, right: 20, bottom: 70, left: 40} // Márgenes del gráfico de barras con respecto al svg en el que se encuentra
const chartWidth = 1000 - margin.left - margin.right // Ancho del svg donde se va a pintar el gráfico de barras (solo se debe editar el número, los márgenes se vuelven a sumar en la creación del svg)
const chartHeight = 500 - margin.top - margin.bottom // Alto del svg donde se va a pintar el gráfico de barras (solo se debe editar el número, los márgenes se vuelven a sumar en la creación del svg)

const barColor = "#DB5E44" // Color de las barras del gráfico