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
		newDataSeq1 = new Array()
		dateInUse2 = dateInUse.slice()
		for (f = 4; f >= 0;) {
			if (dateInUse2[0] == 6 || dateInUse2[0] == 0) {
				newDataSeq1.unshift([appendDate(dateInUse2[1]), dataSeq1[f]])
			}
			else {
				newDataSeq1.unshift([appendDate(dateInUse2[1]), dataSeq1[f]])
				f--
			}
			dateInUse2 = syncDateDown(dateInUse2[0], dateInUse2[1])
		}

		dataSeq2 = predictions[i-1]
		newDataSeq2 = new Array()
		dateInUse2 = dateInUse.slice()
		for (f = 0; f <=4;) {
			dateInUse2 = syncDateUp(dateInUse2[0], dateInUse2[1])

			if (dateInUse2[0] == 6 || dateInUse2[0] == 0) {
				newDataSeq2.push([appendDate(dateInUse2[1]), dataSeq2[f-1]])
			}
			else {
				newDataSeq2.push([appendDate(dateInUse2[1]), dataSeq2[f]])
				f++
			}
		}

		dataSeq = newDataSeq1.concat(newDataSeq2)
		dataProp.push(dataSeq)
	}
	return dataProp
}

function syncDateDown(weekday, date) {
	weekday -= 1
	if (weekday == -1) {
		weekday = 6
	}
	newDate = new Date(date)
	newDate.setDate(newDate.getDate()-1)

	return [weekday, newDate]
}

function syncDateUp(weekday, date) {
	weekday += 1
	if (weekday == 7) {
		weekday = 0
	}
	newDate = new Date(date)
	newDate.setDate(newDate.getDate()+1)

	return [weekday, newDate]
}

function appendDate(date) {
	const ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(date)
	const mo = new Intl.DateTimeFormat('en', { month: 'short' }).format(date)
	const da = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(date)

	return `${da}-${mo}-${ye}`
}

const parseTime = d3.timeParse("%d-%b-%Y")