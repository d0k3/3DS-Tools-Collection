#This script is old and shitty

import os
import errno
import sys
import urllib2
from struct import unpack, pack
from subprocess import call
from binascii import hexlify
from hashlib import sha256


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

##########From https://stackoverflow.com/questions/5783517/downloading-progress-bar-urllib2-python
def chunk_report(bytes_so_far, chunk_size, total_size):
	percent = float(bytes_so_far) / total_size
	percent = round(percent*100, 2)
	sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" % (bytes_so_far, total_size, percent))

	if bytes_so_far >= total_size:
		sys.stdout.write('\n')

def chunk_read(response, outfname, chunk_size=2*1024*1024, report_hook=None):
	fh = open(outfname,'wb')
	total_size = response.info().getheader('Content-Length').strip()
	total_size = int(total_size)
	bytes_so_far = 0
	data = []

	while 1:
		if report_hook:
			report_hook(bytes_so_far, chunk_size, total_size)

		chunk = response.read(chunk_size)
		bytes_so_far += len(chunk)

		if not chunk:
			 break

		fh.write(chunk)

	fh.close()
##########

def SystemUsage():
	print 'Usage: CDNto3DS.py TitleID TitleKey [-vers -redown -redec -no3ds -nocia]'
	print '-vers   : version of title to fetch'
	print '-redown : redownload content'
	print '-nodown : don\'t download content, just print links'
	print '-redec  : re-attempt content decryption'
	print '-no3ds  : don\'t build 3DS file'
	print '-nocia  : don\'t build CIA file'
	raise SystemExit(0)

if len(sys.argv) < 3:
	SystemUsage()

titleid = sys.argv[1]
titlekey = sys.argv[2]
forceDownload = 0
forceDecrypt = 0
make3ds = 1
makecia = 1
nohash = 0
dlversion = -1
noDownload = 0
noDownloadFile = None

for i in xrange(len(sys.argv)) :
	if sys.argv[i] == '-redown': forceDownload = 1
	elif sys.argv[i] == '-redec': forceDecrypt = 1
	elif sys.argv[i] == '-no3ds': makecia = 0
	elif sys.argv[i] == '-nocia': make3ds = 0
	elif sys.argv[i] == '-nodown': noDownload = 1
	elif sys.argv[i] == '-vers': 
		i += 1
		dlversion = sys.argv[i]
	#else : SystemUsage()
	
if len(titleid) != 16 or len(titlekey) != 32:
	print 'Invalid arguments'
	raise SystemExit(0)

baseurl = 'http://nus.cdn.c.shop.nintendowifi.net/ccs/download/' + titleid

print 'Downloading TMD...'

try:
	tmd = urllib2.urlopen(baseurl + '/tmd' + ('.' + str(dlversion), '')[dlversion == -1])
except urllib2.URLError, e:
	print 'ERROR: Bad title ID?'
	raise SystemExit(0)

tmd = tmd.read()

mkdir_p(titleid + ('_v' + str(dlversion), '')[dlversion == -1])
open(titleid + ('_v' + str(dlversion), '')[dlversion == -1] + '/tmd','wb').write(tmd)
print 'Done\n'

if tmd[:4] != '\x00\x01\x00\x04':
	print 'Unexpected signature type.'
	raise SystemExit(0)

# If not normal application, don't make 3ds
if titleid[:8] != '00040000':
	make3ds = 0

mCiaCmd = 'makerom -f cia -rsf rom.rsf -o ' + titleid + '.cia'
mRomCmd = 'makerom -f cci -rsf rom.rsf -nomodtid -o ' + titleid + '.3ds'

# Set Proper CommonKey ID
if unpack('>H', tmd[0x18e:0x190])[0] & 0x10 == 0x10 :
	mCiaCmd = mCiaCmd + ' -ckeyid 1'
else :
	mCiaCmd = mCiaCmd + ' -ckeyid 0'
	
# Set Proper Version
version = unpack('>H', tmd[0x1dc:0x1de])[0]
mCiaCmd = mCiaCmd + ' -major ' + str((version & 0xfc00) >> 10) + ' -minor ' + str((version & 0x3f0) >> 4) + ' -micro ' + str(version & 0xF)

# Set Save Size
saveSize = (unpack('<I', tmd[0x19a:0x19e])[0])/1024
mCiaCmd = mCiaCmd + ' -DSaveSize=' + str(saveSize)
mRomCmd = mRomCmd + ' -DSaveSize=' + str(saveSize)

# If DLC Set DLC flag
if titleid[:8] == '0004008c':
	mCiaCmd = mCiaCmd + ' -dlc'
	
contentCount = unpack('>H', tmd[0x206:0x208])[0]

print 'Content count: ' + str(contentCount) + '\n'

# If not normal application, don't make 3ds
if contentCount > 8 :
	make3ds = 0

# If speicifed nodown option, print links to a file.
if noDownload == 1 :
	noDownloadFile = open('CDNLinks.txt', 'a')
	noDownloadFile.write("TitleId %s\n"%(titleid))

# Download Contents
fSize = 16*1024
for i in xrange(contentCount):
	cOffs = 0xB04+(0x30*i)
	cID = format(unpack('>I', tmd[cOffs:cOffs+4])[0], '08x')
	cIDX = format(unpack('>H', tmd[cOffs+4:cOffs+6])[0], '04x')
	
	# If not normal application, don't make 3ds
	if unpack('>H', tmd[cOffs+4:cOffs+6])[0] >= 8 :
		make3ds = 0

	cOffs = 0xB04+(0x30*i)
	cID = format(unpack('>I', tmd[cOffs:cOffs+4])[0], '08x')
	cIDX = format(unpack('>H', tmd[cOffs+4:cOffs+6])[0], '04x')
	cSIZE = format(unpack('>Q', tmd[cOffs+8:cOffs+16])[0], 'd')
	cHASH = format(unpack('>32s', tmd[cOffs+16:cOffs+48])[0])
	if unpack('>H', tmd[cOffs+4:cOffs+6])[0] >= 8 :
		make3ds = 0
	
	print 'Content ID:    ' + cID
	print 'Content Index: ' + cIDX
	print 'Content Size:  ' + cSIZE
	print 'Content Hash:  ' + hexlify(cHASH)

	outfname = titleid + ('_v' + str(dlversion), '')[dlversion == -1] + '/' + cID
	if os.path.exists(outfname) == 0 or forceDownload == 1 or os.path.getsize(outfname) != unpack('>Q', tmd[cOffs+8:cOffs+16])[0]:
		if noDownload == 0:
			response = urllib2.urlopen(baseurl + '/' + cID)
			chunk_read(response, outfname, report_hook=chunk_report)
			
			#If we redownloaded the content, then decrypting it is implied.
			call(["aescbc", outfname, outfname + '.dec', titlekey, cIDX + '0000000000000000000000000000'])
		else :
			print("Content Link:  %s\n Target File:  %s\n\n" % (baseurl + '/' + cID, outfname))
			noDownloadFile.write("%s:%s\n"%(outfname,baseurl+'/'+cID))
			continue
	elif os.path.exists(outfname + '.dec') == 0 or forceDecrypt == 1 or os.path.getsize(outfname + '.dec') != unpack('>Q', tmd[cOffs+8:cOffs+16])[0]:
		call(["aescbc", outfname, outfname + '.dec', titlekey, cIDX + '0000000000000000000000000000'])

	with open(outfname + '.dec','rb') as fh:
		fh.seek(0, os.SEEK_END)
		fhSize = fh.tell()
		if fh.tell() != unpack('>Q', tmd[cOffs+8:cOffs+16])[0]:
			print 'Title size mismatch.  Download likely incomplete'
			print 'Downloaded: ' + format(fh.tell(), 'd')
			raise SystemExit(0)
		fh.seek(0)
		hash = sha256()
		
		while fh.tell() != fhSize:
			hash.update(fh.read(0x1000000))
			print 'checking hash: ' + format(float(fh.tell()*100)/fhSize,'.1f') + '% done\r',
			
		sha256file = hash.hexdigest()
		if sha256file != hexlify(cHASH):
			print 'hash mismatched, Decryption likely failed, wrong key?'
			print 'got hash: ' + sha256file
			raise SystemExit(0)
		fh.seek(0x100)
		if fh.read(4) != 'NCCH':
			makecia = 0
			make3ds = 0
			fh.seek(0x60)
			if fh.read(4) != 'WfA\0':
				print 'Not NCCH, nor DSiWare, file likely corrupted'
				raise SystemExit(0)
			else:
				print 'Not an NCCH container, likely DSiWare'
		fh.seek(0, os.SEEK_END)
		fSize += fh.tell()
		
	print '\n'
	mCiaCmd = mCiaCmd + ' -i ' + outfname + '.dec' + ':0x' + cIDX + ':0x' + cID
	mRomCmd = mRomCmd + ' -i ' + outfname + '.dec' + ':0x' + cIDX + ':0x' + cID

if noDownload == 1 :
	noDownloadFile.close()
	print "URL links appended to CDNLinks.txt"
	raise SystemExit(0)

# Create RSF File
romrsf = 'Option:\n  MediaFootPadding: true\n  EnableCrypt: false\nSystemControlInfo:\n  SaveDataSize: $(SaveSize)K'
with open('rom.rsf', 'wb') as fh:
	fh.write(romrsf)
	
if makecia == 1:
	print '\nBuilding ' + titleid + '.cia...'
	#print mCiaCmd
	os.system(mCiaCmd)

if make3ds == 1:
	print '\nBuilding ' + titleid + '.3ds...'
	#print mRomCmd
	os.system(mRomCmd)
	
os.remove('rom.rsf')

if not os.path.isfile(titleid + '.cia') and makecia == 1:
	print "Something went wrong."
	raise SystemExit(0)

if not os.path.isfile(titleid + '.3ds') and make3ds == 1:
	print "Something went wrong."
	raise SystemExit(0)
	
print 'Done!'
