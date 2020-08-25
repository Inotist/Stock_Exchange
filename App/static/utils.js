function formatArray(text) {
	return text.replace(/\. /g,' ').replace(/\s+/g,' ').replace(/ ]/g, "]").replace(/ /g, ", ");
}

function orderData(data, predictions) {
	const dataProp = new Array();
	for (i = data.length; i >= 5; i--) {
		dataSeq = new Array();
		dataSeq.push(data.slice(i-5, i))
		dataSeq.push(predictions[i-1])
		dataProp.push(dataSeq)
	}
	return dataProp
}