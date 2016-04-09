#!/usr/bin/env python2
import sys
import os
from binascii import hexlify, unhexlify
import struct

encKeys = []

with open('keys.txt') as fh:
	for line in fh:

		lineArray = line.strip().split(' ')
		print lineArray

		tid = lineArray[0]
		encKey = lineArray[1]

		commonKeyIndex = 0000
		encKeys.append([unhexlify(encKey), unhexlify(tid), commonKeyIndex])

outData = struct.pack('<IIII', len(encKeys), 0, 0, 0)
for entry in encKeys:
	outData += struct.pack('<II', entry[2], 0)
	outData += entry[1]
	outData += entry[0]

open('decTitleKeys.bin','wb').write(outData)
