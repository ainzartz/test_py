import os
import sys

fp = open("1")
dic = {}
for line in fp:
	cols = line.split("Send ConnID")
	#if len(cols) != 2:
	#	print line
	a = cols[1].replace('\n', '')
	a = a[1:]

	a = a.replace('[', '').replace('\'', '').replace(']', '').replace(',', '')
	b = a.split(' ')

	for b1 in b:
		dic[b1] = 1
fp.close()

print len(dic)

