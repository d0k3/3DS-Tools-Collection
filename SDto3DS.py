#This script is old and shitty

import os
import sys
from struct import unpack, pack
from binascii import hexlify

#Ugly code ahead


if len(sys.argv) < 3:
	print 'Usage: SDto3DS.py tmd cardType'
	print "Place decrypted .tmd and .app files in the folder with this .py"
	print "\ncardType: valid options are 'card1' and 'card2'"
	raise SystemExit(0)

if not os.path.isfile(sys.argv[1]):
	print "Input file doesn't exist."
	raise SystemExit(0)

tmd = open(sys.argv[1],'rb').read()
titleid = hexlify(tmd[0x18C:0x194])

cardType = sys.argv[2].lower()
if cardType not in ['', 'card1', 'card2']:
	print 'Invalid cardType.'
	raise SystemExit(0)
cardType = ['', 'card1', 'card2'].index(cardType)

eShopContent = ['00040000', '00040002']
if titleid[:8] not in eShopContent:
	print 'This only works with eShop content.'
	raise SystemExit(0)

if tmd[:4] != '\x00\x01\x00\x04':
	print 'Unexpected signature type.'
	raise SystemExit(0)

contentCount = unpack('>H', tmd[0x206:0x208])[0]

if contentCount > 8:
	print 'Content count too high.'
	raise SystemExit(0)

print 'Content count: ' + str(contentCount) + '\n'

indextypes = [' (Main Content)', ' (Manual)', '(Download Play container)', '', '', '', '', '']

mRomCmd = 'makerom -f cci -rsf rom.rsf -o ' + titleid + '.3ds -nomodtid'

fSize = 16*1024

for i in xrange(contentCount):
	cOffs = 0xB04+(0x30*i)
	cID = unpack('>I', tmd[cOffs:cOffs+4])[0]
	cIDX = unpack('>H', tmd[cOffs+4:cOffs+6])[0]
	print 'Content ID:    ' + str(cID).zfill(8)
	print 'Content Index: ' + str(cIDX).zfill(8) + indextypes[cIDX]

	if not os.path.isfile(str(cID).zfill(8) + '.app'):
		print str(cID).zfill(8) + ".app doesn't exist"
		raise SystemExit(0)

	with open(str(cID).zfill(8) + '.app','rb') as fh:
		fh.seek(0x100)
		if fh.read(4) != 'NCCH':
			print str(cID).zfill(8) + ".app wasn't properly decrypted?"
			raise SystemExit(0)
		fh.seek(0, os.SEEK_END)
		fSize += fh.tell()

	print '\n'
	mRomCmd = mRomCmd + ' -content ' + str(cID).zfill(8) + '.app' + ':' + str(cIDX)


romrsf = ''

romrsf1 = 'CardInfo:\n  MediaSize               : '
romrsf2 = '\n  MediaType               : '
romrsf3 = '\n  CardDevice              : '
romrsf4 = '\n\nSystemControlInfo:\n  SaveDataSize: 512KB\n'

mediaSizes = ['128MB', '256MB', '512MB', '1GB', '2GB', '4GB', '8GB']
romSizes = [128*1024*1024, 256*1024*1024, 512*1024*1024, 1*1024*1024*1024, 2*1024*1024*1024, 4*1024*1024*1024, 8*1024*1024*1024]
sizeIDX = min(range(len(romSizes)), key=lambda i: abs(romSizes[i]-fSize))
if romSizes[sizeIDX] < fSize:
	sizeIDX += 1

if cardType == 1: #Card1
	romrsf = romrsf1 + mediaSizes[sizeIDX] + romrsf2 + 'Card1' + romrsf3 + 'NorFlash' + romrsf4
else: #Card2
	romrsf = romrsf1 + mediaSizes[sizeIDX] + romrsf2 + 'Card2' + romrsf3 + 'None'

with open('rom.rsf', 'wb') as fh:
	fh.write(romrsf)

print 'Building ' + titleid + '.3ds...\n'

os.system(mRomCmd)

if not os.path.isfile(titleid + '.3ds'):
	print "Something went wrong."
	raise SystemExit(0)


#This should be done with makerom in the RSF
with open(titleid + '.3ds', 'ab+') as fh: #File padding
	fh.seek(0, os.SEEK_END)
	paddingLeft = (romSizes[sizeIDX])-fh.tell()
	while paddingLeft > 0:
		if paddingLeft < 0x400000:
			padSize = paddingLeft
		else:
			padSize = 0x400000
		fh.write('\xFF'*padSize)
		paddingLeft -= 0x400000


print 'Done!'
