# Show the entries which make up the top (most-frequent) N% of all
# entries.
#
# The input is `sort -k1 -rn`'d output from `uniq -c`. The "N"
# variable is defined as the percentage.

BEGIN {
	if (N < 0 || N > 100) {
		print "Bad percentage."
		exit(1)
	}

	idx = 0
	total = 0
}

{
	total += $1
	counts[idx] = $1
	entries[idx] = $2
	idx += 1
}

END {
	final_idx = idx
	count = 0
	thresh = N * total / 100.0
	percentile_entries = 0

	for (idx = 0; idx < final_idx; idx += 1) {
		if (count < thresh) {
			# print "Page: " entries[idx] ", Count: " counts[idx]
			count += counts[idx]
			percentile_entries += 1
		}
	}

	# print "Total: " total
	# print "Thresh: " thresh
	# print "Top percentage: " N
	print "Entries in top " N "%: " percentile_entries
}
