data = JSON.parse(formatArray(document.getElementById("data").innerHTML))
predictions = JSON.parse(formatArray(document.getElementById("predictions").innerHTML))

orderedData = orderData(data, predictions)

const chartSVG = createChartSVG();
drawChart(chartSVG);

function createChartSVG() {
	return d3.select("#chart").append("svg")
    	.attr("width", chartWidth + margin.left + margin.right)
    	.attr("height", chartHeight + margin.top + margin.bottom)
  		.append("g")
    	.attr("transform", `translate(${margin.left}, ${margin.top})`);
}

function drawChart(svg) {
	svg.selectAll("*").remove();
	const dataProp = pageData();

	var x = d3.scaleLinear().range([0, chartWidth]);
	var y = d3.scaleBand().rangeRound([0, chartHeight]).paddingInner(0.1);

	var xAxis = d3.axisBottom(x)
    	.ticks(ticks);
	var yAxis = d3.axisLeft(y)
    	.ticks(ticks);
	
  	x.domain([1, ticks]);
  	y.domain([d3.min(dataProp)-(d3.max(dataProp)-d3.min(dataProp))/2, d3.max(dataProp)]);

  	svg.append("g")
    	.attr("transform", `translate(0, ${chartHeight})`)
    	.call(xAxis);

    svg.append("text")             
      .attr("transform", `translate(${chartWidth / 2} ,${chartHeight + margin.top + 20})`)
      .style("text-anchor", "middle")
      .text("Properties");

  	svg.append("g")
    	.call(yAxis);

    svg.append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - (chartHeight / 2))
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text("Bedrooms");

  	svg.selectAll("bar")
    	.data(dataProp)
    	.enter()
    	.append("rect")
    	.style("fill", barColor)
    	.attr("y", d => y(d))
    	.attr("height", y.bandwidth())
    	.attr("width", d => x(d));
}

function pageData() {

}

/////////// Para el final
function setColor(layers) {
	var prices = [];
	layers.forEach (layer => {
		prices.push(layer.feature.properties.avgprice);
	});
	const max = d3.max(prices);
	const min = d3.min(prices);
	const scale = ((max-min)/gradient.length)+outlier;

	layers.forEach (layer => {
		const price = layer.feature.properties.avgprice;

		var count = 1;
		gradient.forEach(color => {
			if ((price <= min+scale*count && layer.options.color == defaultColor) || (count == gradient.length && price >= min+scale*count)) {
				layer.options.color = color;
				return;
			};
			count += 1;
		});

		if (layer.options.color == defaultColor) {
			layer.options.opacity = defaultOpacity;
			layer.options.fillOpacity = defaultOpacity;
		};
	});
}