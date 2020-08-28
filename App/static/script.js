const xScale = d3.scaleTime().range([0, width]);

const yScale = d3.scaleLinear().range([height, 0]);

const line = d3.line()
    .x(function(d) { return xScale(d[0]); })
    .y(function(d) { return yScale(d[1]); })

const svg = d3.select("body").append("svg")
  .attr('id', 'mainsvg')
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

drawChart(n);

document.getElementById("mainsvg").addEventListener("wheel", function (event) {
  if (event.deltaY < 0) { n -= 1; }
  else if (event.deltaY > 0) { n += 1; }
  if (n < 0) { n = 0; }
  else if (n >= orderedData.length) { n = orderedData.length-1; }
  drawChart(n);
});

function drawChart(n) {
  svg.selectAll("path").remove();
  svg.selectAll("g").remove();
  svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  workData = orderedData[n][0]
  predData = orderedData[n][1]

  dataLen = workData.concat(predData)
    
  xScale.domain(d3.extent(dataLen, function(d) { return d[0]; }));

  datamin = d3.min(dataLen.map(function(d) { return d[1]; }))
  datamax = d3.max(dataLen.map(function(d) { return d[1]; }))
  yScale.domain([datamin-(datamax-datamin)/frac, datamax]);

  svg.append("path")
      .data([workData])
      .attr("class", "lineblue")
      .attr("d", line);

  svg.append("path")
      .data([predData])
      .attr("class", "linered")
      .attr("d", line);

  svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(xScale));

  svg.append("g")
      .call(d3.axisLeft(yScale));
}