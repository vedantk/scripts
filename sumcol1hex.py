import fileinput

total = 0
for line in fileinput.input():
    col1 = line.split()[0]
    val = int(col1, base=16)
    print('{0} -> {1}'.format(col1, val))
    total += val

print(total)
