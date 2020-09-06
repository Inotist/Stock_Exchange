var theme = "dark";
document.body.style.background = "#02021A";

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

drawChart(n, theme);

document.getElementById("mainsvg").addEventListener("wheel", function (event) {
  if (event.deltaY > 0) { n -= 1; }
  else if (event.deltaY < 0) { n += 1; }
  if (n < 0) { n = 0; }
  else if (n >= orderedData.length) { n = orderedData.length-1; }
  drawChart(n, theme);
});

function drawChart(n, theme) {
  svg.selectAll("path").remove();
  svg.selectAll("g").remove();
  svg.append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  workData = orderedData[n][0]
  predData = orderedData[n][1]

  dataLen = workData.concat(predData)

  if (n == 0) {
    smoothPred = orderedData[n][2]
    dataLen = dataLen.concat(smoothPred)
  }
    
  xScale.domain(d3.extent(dataLen, function(d) { return d[0]; }));

  datamax = d3.max(dataLen.map(function(d) { return d[1]; }))
  datamin = d3.min(dataLen.map(function(d) { return d[1]; }))
  datamin = datamin-(datamax-datamin)/frac
  yScale.domain([datamin, datamax]);

  workDataFill = fillPath(workData.slice(), datamin)
  predDataFill = fillPath(predData.slice(), datamin)

  svg.append("path")
    .data([workDataFill])
    .attr("class", "lineblue")
    .attr("d", line);

  svg.append("path")
    .data([predDataFill])
    .attr("class", "linegreen")
    .attr("d", line);

  if (n == 0) {
    svg.append("path")
      .data([smoothPred])
      .attr("class", "linepurple")
      .attr("d", line);
  }

  if (theme == "dark") {
    elements = document.getElementsByClassName("text");
    for (i = 0; i < elements.length; i++) {
      elements[i].classList.add("whitetext")
    };

    svg.append("g")
      .attr("class", "whitetext")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(xScale));

    svg.append("g")
      .attr("class", "whitetext")
      .call(d3.axisLeft(yScale));

    var lineLegend = svg.selectAll(".lineLegend").data(legend_keys)
      .enter().append("g")
      .attr("class","lineLegend")
      .attr("transform", function (d,i) {
        return "translate(" + width + "," + (i*20)+")";
      });

    var quarterlyLegend = svg.selectAll(".quarterlyInfo").data(quarterly_info)
      .enter().append("g")
      .attr("class","lineLegend")
      .attr("transform", function (d,i) {
        return "translate(" + width + "," + (i*20)+")";
      });

    var growthLegend = svg.selectAll(".quarterlyInfo").data(growth)
      .enter().append("g")
      .attr("class","lineLegend")
      .attr("transform", function (d,i) {
        if (i != 2) {
          return "translate(" + width + "," + (i*20)+")";
        }
        else {
          return "translate(" + (width+90) + "," + (i*30)+")";
        }
      });
  }
  else {
    elements = document.getElementsByClassName("text");
    for (i = 0; i < elements.length; i++) {
      elements[i].classList.remove("whitetext")
    };

    svg.append("g")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(xScale));

    svg.append("g")
      .call(d3.axisLeft(yScale));

    var lineLegend = svg.selectAll(".lineLegend").data(legend_keys)
      .enter().append("g")
      .attr("transform", function (d,i) {
        return "translate(" + width + "," + (i*20)+")";
      });

    var quarterlyLegend = svg.selectAll(".quarterlyInfo").data(quarterly_info)
      .enter().append("g")
      .attr("transform", function (d,i) {
        return "translate(" + width + "," + (i*20)+")";
      });

    var growthLegend = svg.selectAll(".quarterlyInfo").data(growth)
      .enter().append("g")
      .attr("transform", function (d,i) {
        if (i != 2) {
          return "translate(" + width + "," + (i*20)+")";
        }
        else {
          return "translate(" + (width+90) + "," + (i*30)+")";
        }
      });
  }

  lineLegend.append("text").text(function (d) {return d;})
    .attr("transform", "translate(60,9)");

  lineLegend.append("rect")
    .attr("fill", function (d, i) { return legend_colors[i]; })
    .attr("transform", "translate(45,0)")
    .attr("width", 10).attr("height", 10);

  quarterlyLegend.append("text").text(function (d) {return d;})
    .style("font-weight", function (d, i) {
      if (i == 1) {
        return "bold"
      }
    })
    .style("font-size", function (d, i) {
      if (i == 1) {
        return "24px"
      }
    })
    .attr("transform", "translate(-"+ width +","+ (height+margin.top) +")");

  growthLegend.append("text").text(function (d) {return d;})
    .style("fill", function (d, i) {
      n = parseFloat(d.slice(0,d.length-1))
      if (i == 2 && n > 0) {
        return "#10B998"
      }
      else if (i == 2 && n < 0) {
        return "#E42727"
      }
    })
    .style("font-size", function (d, i) {
      if (i == 2) {
        return "34px"
      }
      if (i == 5) {
        return "12px"
      }
    })
    .attr("transform", "translate(-"+ (width-400) +","+ (height+margin.top) +")");
}

function fillPath(path, min) {
  path.push([path[path.length-1][0], min]);
  path.push([path[0][0], min]);
  path.push(path[0]);

  return path;
}

function light() {
  document.body.style.background = "white";
  theme = "light"
  drawChart(n, "light");
}

function dark() {
  document.body.style.background = "#02021A";
  theme = "dark"
  drawChart(n, "dark");
}