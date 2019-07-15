# The input is a stream. The "col" variable is defined as the
# column of the input containing numbers to average.

BEGIN {
	sum = 0
	idx = 0
	min = -log(0)
	max = log(0)
}

{
	if ($col ~ /^-?[0-9]+(\.[0-9]+)?$/) {
		val = $col
		sum += val
		inputs[idx] = val
		idx += 1
		if (val < min) {
			min = val
		}
		if (val > max) {
			max = val
		}
	}
}

END {
	if (idx > 0) {
		mean = sum / idx

		sum_of_squares = 0
		for (input in inputs) {
			sum_of_squares += (inputs[input] - mean)^2
		}
		variance = sum_of_squares / idx
		stddev = sqrt(variance)

		sum_of_logs = 0
		for (input in inputs) {
			val = inputs[input]
			if (val > 0) {
				sum_of_logs += log(val)
			}
			if (val < 0) {
				sum_of_logs += log(val)
			}
		}
		geomean = exp(sum_of_logs / idx)
		if (mean < 0) {
			geomean *= -1
		}
	} else {
		mean = 0
		stddev = 0
		geomean = 0
	}

	print "Mean: " mean
	print "Stddev: " stddev
	print "Geomean: " geomean
	print "NumInputs: " idx
	print "Range: [" min ", " max "]"
}
