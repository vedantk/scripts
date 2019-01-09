# The input is a stream. The "col" variable is defined as the
# column of the input containing numbers to average.

BEGIN {
	sum = 0
	idx = 0
}

{
	if ($col ~ /^[0-9]+(\.[0-9]+)?$/) {
		sum += $col
		inputs[idx] = $col
		idx += 1
	}
}

END {
	mean = sum / idx

	sum_of_squares = 0
	for (input in inputs) {
		sum_of_squares += (inputs[input] - mean)^2
	}
	variance = sum_of_squares / idx
	stddev = sqrt(variance)

	sum_of_logs = 0
	for (input in inputs) {
		sum_of_logs += log(inputs[input])
	}
	geomean = exp(sum_of_logs / idx)

	print "Mean: " mean
	print "Stddev: " stddev
	print "Geomean: " geomean
}
