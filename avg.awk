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

	num_less_than_mean = 0
	num_less_than_sigma = 0
	num_less_than_two_sigma = 0
	num_less_than_three_sigma = 0
	for (input in inputs) {
		if (inputs[input] < mean)
			num_less_than_mean += 1
		if (inputs[input] < (mean + stddev))
			num_less_than_sigma += 1
		if (inputs[input] < (mean + (2 * stddev)))
			num_less_than_two_sigma += 1
		if (inputs[input] < (mean + (3 * stddev)))
			num_less_than_three_sigma += 1
	}

	printf("%% < %f (mean): %.2f\n", mean, 100 * (num_less_than_mean / idx))
	printf("%% < %f (1 sigma): %.2f\n", mean + stddev, 100 * (num_less_than_sigma / idx))
	printf("%% < %f (2 sigma): %.2f\n", mean + (2 * stddev), 100 * (num_less_than_two_sigma / idx))
	printf("%% < %f (3 sigma): %.2f\n", mean + (3 * stddev), 100 * (num_less_than_three_sigma / idx))
}
