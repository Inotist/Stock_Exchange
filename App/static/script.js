const x = d3.scale.ordinal().rangeRoundBands([0, width], .05);
const y = d3.scale.linear().range([height, 0]);

const xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .ticks(10);

const yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
      .ticks(10);

const svg = d3.select("body").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

d3.json("", function(data) {
  data = orderedData[0]
	
  x.domain(data.map(function(d) { return d[0]; }));

  datamin = d3.min(data.map(function(d) { return d[1]; }))
  datamax = d3.max(data.map(function(d) { return d[1]; }))
  y.domain([datamin-(datamax-datamin)/frac, datamax]);

  console.log(datamin, datamax, data)

  svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
      .style("text-anchor", "end")
      .attr("dx", "-.8em")
      .attr("dy", "-.55em")
      .attr("transform", "rotate(-90)" );

  svg.append("g")
      .attr("class", "y axis")
      .call(yAxis)
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Price ($)");

  drawBar(data.slice(0,5), "steelblue")
  drawBar(data.slice(5,10), "red")

});