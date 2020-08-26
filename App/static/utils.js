function formatArray(text) {
	return text.replace(/\. /g,' ').replace(/\s+/g,' ').replace(/ ]/g, "]").replace(/ /g, ", ");
}

function orderData(data, predictions) {
	weekday = new Date().getDay()
	date = new Date()
	dateInUse = [weekday, date]

	const dataProp = new Array();

	for (i = data.length; i >= 5; i--) {
		dateInUse = syncDateDown(dateInUse[0], dateInUse[1])

		dataSeq1 = data.slice(i-5, i)
		dateInUse2 = dateInUse.slice()
		for (f = 4; f >= 0; f--) {
			dataSeq1[f] = [appendDate(dateInUse2[1]), dataSeq1[f]]
			dateInUse2 = syncDateDown(dateInUse2[0], dateInUse2[1])
		}

		dataSeq2 = predictions[i-1]
		dateInUse2 = dateInUse.slice()
		dataSeq2 = dataSeq2.map(function(d) {
			dateInUse2 = syncDateUp(dateInUse2[0], dateInUse2[1])
			return [appendDate(dateInUse2[1]), d]
		})

		dataSeq = dataSeq1.concat(dataSeq2)

		dataProp.push(dataSeq)
	}
	return dataProp
}

function syncDateDown(weekday, date) {
	weekday -= 1
	newDate = new Date(date)
	newDate.setDate(newDate.getDate()-1)

	if (weekday == 0) {
		weekday = 5
		newDate.setDate(newDate.getDate()-2)
	}
	else if (weekday == 6) {
		weekday = 5
		newDate.setDate(newDate.getDate()-1)
	}
	return [weekday, newDate]
}

function syncDateUp(weekday, date) {
	weekday += 1
	newDate = new Date(date)
	newDate.setDate(newDate.getDate()+1)

	if (weekday == 0) {
		weekday = 1
		newDate.setDate(newDate.getDate()+1)
	}
	else if (weekday == 6) {
		weekday = 1
		newDate.setDate(newDate.getDate()+2)
	}
	return [weekday, newDate]
}

function appendDate(date) {
	const ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(date)
	const mo = new Intl.DateTimeFormat('en', { month: 'short' }).format(date)
	const da = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(date)

	return `${da}-${mo}-${ye}`
}

function drawBar(data, color) {
	svg.selectAll("bar")
		.data(data)
    	.enter().append("rect")
    	.style("fill", color)
    	.attr("x", function(d) { return x(d[0]); })
    	.attr("width", x.rangeBand())
    	.attr("y", function(d) { return y(d[1]); })
    	.attr("height", function(d) { return height - y(d[1]); });
}