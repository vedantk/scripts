BEGIN {
	numFuncs = 0
	numUnoutlinedFuncsWithBrk = 0
	numFuncsWithAssertRtn = 0
	numFuncsWithOSLog = 0
	funcHasBrk = 0
	funcHasAssertRtn = 0
	funcHasOSLog = 0
	isOutlined = 0
	numOutlinedFuncs = 0
	outlinedBytes = 0
	funcName = ""
}

/:$/ {
	if ($0 ~ /^[-+_].*\.cold.[0-9]+:$/) {
		print $0
		isOutlined = 1
		numOutlinedFuncs += 1
	} else {
		isOutlined = 0
	}

	funcName = $0

	numFuncs += 1
	funcHasBrk = 0
	funcHasAssertRtn = 0
	funcHasOSLog = 0
}

/^0000/ {
	bytesInFunc += 4
	if (isOutlined == 1) {
		outlinedBytes += 4
		if ($0 ~ /abort|assert|brk|os_log/) {
			print $0
			print ""
		}
	}
}

/brk/ {
	if (funcHasBrk == 0) {
		if (isOutlined == 0) {
			numUnoutlinedFuncsWithBrk += 1
		}
		funcHasBrk = 1
	}
}

/assert_rtn/ {
	if (funcHasAssertRtn == 0 && isOutlined) {
		numFuncsWithAssertRtn += 1
		funcHasAssertRtn = 1
	}
}

/os_log/ {
	if (funcHasOSLog == 0 && isOutlined == 1) {
		numFuncsWithOSLog += 1
		funcHasOSLog = 1
	}
}

END {
	print "numFuncs:" numFuncs
	print "numUnoutlinedFuncsWithBrk:" numUnoutlinedFuncsWithBrk
	print "numOutlinedFuncs:" numOutlinedFuncs
	print "outlinedBytes:" outlinedBytes
	print "numFuncsWithAssertRtn:" numFuncsWithAssertRtn
	print "numFuncsWithOSLog:" numFuncsWithOSLog
}
