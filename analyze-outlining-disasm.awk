BEGIN {
	numFuncs = 0
	numOutlinedFuncsWithBrk = 0
	numFuncsWithAssertRtn = 0
	numFuncsWithOSLog = 0
	funcHasBrk = 0
	funcHasAssertRtn = 0
	funcHasOSLog = 0
	isOutlined = 0
	numOutlinedFuncs = 0
	outlinedBytes = 0
	funcName = ""
	totalBytes = 0
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
	totalBytes += 4
	if (isOutlined == 1) {
		outlinedBytes += 4
		# print $0
		if ($0 ~ /Unwind_Resume|abort|assert|brk|os_log/) {
			print $0
			print ""
		}
	}
}

/brk/ {
	if (funcHasBrk == 0) {
		if (isOutlined == 1) {
			numOutlinedFuncsWithBrk += 1
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
	print "numOutlinedFuncsWithBrk:" numOutlinedFuncsWithBrk
	print "numOutlinedFuncs:" numOutlinedFuncs
	print "numFuncsWithAssertRtn:" numFuncsWithAssertRtn
	print "numFuncsWithOSLog:" numFuncsWithOSLog
	print "totalBytes:" totalBytes
	print "outlinedBytes:" outlinedBytes
	print "outlined:" outlinedBytes/(1.0*totalBytes)
}
