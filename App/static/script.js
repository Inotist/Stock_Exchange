const xScale = d3.scaleTime().range([0, width]);

const yScale = d3.scaleLinear().range([height, 0]);

const line = d3.line()
    .x(function(d) { return xScale(d[0]); })
    .y(function(d) { return yScale(d[1]); })

const svg = d3.select("body").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

workData = orderedData[0]
workData.forEach(function (d) {
  d[0] = parseTime(d[0]);
});
	
xScale.domain(d3.extent(workData, function(d) { return d[0]; }));

datamin = d3.min(workData.map(function(d) { return d[1]; }))
datamax = d3.max(workData.map(function(d) { return d[1]; }))
yScale.domain([datamin-(datamax-datamin)/frac, datamax]);

svg.append("path")
    .data([workData])
    .attr("class", "line")
    .attr("d", line);

svg.append("g")
    .attr("transform", "translate(0," + height + ")")
    .call(d3.axisBottom(xScale));

svg.append("g")
    .call(d3.axisLeft(yScale));

//drawLines(workData.slice(0,5), "steelblue");
//drawLines(workData.slice(5,10), "red");