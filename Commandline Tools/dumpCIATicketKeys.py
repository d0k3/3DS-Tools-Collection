#!/usr/bin/env python2
import sys
import os
from binascii import hexlify
import struct

def u32(s):
	i, = struct.unpack('<I', s)
	return i

def read(l):
	global pos
	file.seek(pos)
	s = file.read(l)
	pos += l
	return s

pos = 0
encKeys = []

for filename in os.listdir("."):
	if filename.endswith(".cia"):
		file = open(filename)

		heads = u32(read(0x4))
		read(0x2) # type
		read(0x2) # ver
		certs = u32(read(0x4))
		tiks = u32(read(0x4))
		tmds = u32(read(0x4))
		pos = heads + 0x20 # dunno why, but 0x20 seems to work


		pos += certs
		sigtype = hexlify(read(4))
		pos += {'00010000':0x23C, '00010001':0x13C, '00010002':0x7C, '00010003':0x23C, '00010004':0x13C, '00010005':0x7C}[sigtype]
		pos += 0x7F
		encKey = read(0x10)
		pos += 0xD
		tid = read(0x8)
		pos += 0xD
		commonKeyIndex = ord(read(1))

		print 'Encrypted title key:  ' + hexlify(encKey)
		print 'Title ID:  ' + hexlify(tid)
		print 'Common key index: %u' % commonKeyIndex
		print ''

		encKeys.append([encKey, tid, commonKeyIndex])

		pos = 0

outData = struct.pack('<IIII', len(encKeys), 0, 0, 0)
for entry in encKeys:
	outData += struct.pack('<II', entry[2], 0)
	outData += entry[1]
	outData += entry[0]

open('encTitleKeys.bin','wb').write(outData)
