#script is modified from https://github.com/Relys/3DS_Multi_Decryptor/blob/master/to3DS/CDNto3DS/CDNto3DS.py
#requires PyCrypto to be installed (pip install PyCrypto)
#requires makerom (https://github.com/profi200/Project_CTR/releases)

import os
import struct
import errno
import sys
import urllib2
from struct import unpack, pack
from subprocess import call
from binascii import hexlify, unhexlify
from hashlib import sha256
from Crypto.Cipher import AES


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
    print("Downloaded %d of %d bytes (%0.2f%%)" % (bytes_so_far, total_size, percent))

    if bytes_so_far >= total_size:
        print('\n')

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
    print 'Usage: CDNto3DS.py <TitleID TitleKey [-redown -redec -no3ds -nocia] or [-check]> or [-deckey] or [-checkbin]'
    print '-deckey   : print keys from decTitleKeys.bin'
    print '-check    : checks if title id matches key'
    print '-checkbin : checks titlekeys from decTitleKeys.bin'
    print '-redown   : redownload content'
    print '-nodown   : don\'t download content, just print links'
    print '-redec    : re-attempt content decryption'
    print '-no3ds    : don\'t build 3DS file'
    print '-nocia    : don\'t build CIA file'
    raise SystemExit(0)

#adapted from http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto
def decrypt_file(in_key, in_filename, out_filename, in_iv, chunksize=24*1024):
    with open(in_filename, 'rb') as infile:
        iv = unhexlify(in_iv)
        key = unhexlify(in_key)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

#from https://github.com/Relys/3DS_Multi_Decryptor/blob/master/ticket-titlekey_stuff/printKeys.py
for i in xrange(len(sys.argv)) :
    if sys.argv[i] == '-deckey':
        with open('decTitleKeys.bin', 'rb') as fh:
            nEntries = os.fstat(fh.fileno()).st_size / 32
            fh.seek(16, os.SEEK_SET)
            for i in xrange(nEntries):
                fh.seek(8, os.SEEK_CUR)
                titleId = fh.read(8)
                decryptedTitleKey = fh.read(16)
                print '%s: %s' % (hexlify(titleId), hexlify(decryptedTitleKey))
        raise SystemExit(0)

for i in xrange(len(sys.argv)) :
    if sys.argv[i] == '-checkbin':
        tmdFail = 0
        with open('decTitleKeys.bin', 'rb') as fh:
            nEntries = os.fstat(fh.fileno()).st_size / 32
            fh.seek(16, os.SEEK_SET)
            print "This option checks 00040000 (game) titles only\n"
            for i in xrange(nEntries):
                fh.seek(8, os.SEEK_CUR)
                titleId = fh.read(8)
                decryptedTitleKey = fh.read(16)

                baseurl = 'http://nus.cdn.c.shop.nintendowifi.net/ccs/download/' + hexlify(titleId)
                try:
                    tmd = urllib2.urlopen(baseurl + '/tmd')
                except urllib2.URLError, e:
                    print 'ERROR: Could not retrieve TMD, bad title ID?'
                    tmdFail = 1

                if tmdFail == 0 and titleId[:8] == '00040000':
                    tmd = tmd.read()

                    cOffs = 0xB04+(0x30*i)
                    cID = format(unpack('>I', tmd[cOffs:cOffs+4])[0], '08x')
                    cIDX = format(unpack('>H', tmd[cOffs+4:cOffs+6])[0], '04x')
                    cSIZE = format(unpack('>Q', tmd[cOffs+8:cOffs+16])[0], 'd')
                    cHASH = format(unpack('>32s', tmd[cOffs+16:cOffs+48])[0])
                    # use range requests to download bytes 0 through 271, needed because AES-128-CBC encrypts in chunks of 128 bits
                    print hexlify(titleId)
                    print 'Content ID:    ' + cID
                    print 'Content Index: ' + cIDX
                    print 'Content Size:  ' + cSIZE
                    print 'Content Hash:  ' + hexlify(cHASH)

                    try:
                        checkReq = urllib2.Request("%s/%s"%(baseurl, cID))
                        checkReq.headers['Range'] = 'bytes=%s-%s' % (0, 271)
                        checkTemp = urllib2.urlopen(checkReq)
                    except urllib2.URLError, e:
                        print 'ERROR: Could not retrieve content, bad title ID?'

                    # set IV to offset 0xf0 length 0x10 of ciphertext; thanks to yellows8 for the offset
                    checkTempPerm = checkTemp.read()
                    checkIv = checkTempPerm[0xf0:0x100]
                    decryptor = AES.new(decryptedTitleKey, AES.MODE_CBC, checkIv)

                    # check for magic ("NCCH") at offset 0x100 length 0x104 of the decrypted content
                    checkTempOut = decryptor.decrypt(checkTempPerm)[0x100:0x104]

                    if 'NCCH' not in checkTempOut:
                        print 'ERROR: Titlekey ' + decryptedTitleKey + ' does not match title ID ' + titleId

                    print 'Title ID ' + hexlify(titleId) + ' successfully verified to match titlekey ' + hexlify(decryptedTitleKey)
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
checkKey = 0
checkTempOut = None

for i in xrange(len(sys.argv)) :
    if sys.argv[i] == '-redown': forceDownload = 1
    elif sys.argv[i] == '-redec': forceDecrypt = 1
    elif sys.argv[i] == '-no3ds': make3ds = 0
    elif sys.argv[i] == '-nocia': makecia = 0
    elif sys.argv[i] == '-nodown': noDownload = 1
    elif sys.argv[i] == '-check': checkKey = 1

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

if checkKey != 1:
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

    if checkKey == 1:
        print '\nDownloading and decrypting the first 272 bytes of ' + cID + ' for key check'
        # use range requests to download bytes 0 through 271, needed because AES-128-CBC encrypts in chunks of 128 bits
        try:
            checkReq = urllib2.Request("%s/%s"%(baseurl, cID))
            checkReq.headers['Range'] = 'bytes=%s-%s' % (0, 271)
            checkTemp = urllib2.urlopen(checkReq)
        except urllib2.URLError, e:
            print 'ERROR: Bad title ID?'
            raise SystemExit(0)

        # set IV to offset 0xf0 length 0x10 of ciphertext; thanks to yellows8 for the offset
        checkTempPerm = checkTemp.read()
        decryptor = AES.new(unhexlify(titlekey), AES.MODE_CBC, checkTempPerm[0xf0:0x100])

        # check for magic ("NCCH") at offset 0x100 length 0x104 of the decrypted content
        checkTempOut = decryptor.decrypt(checkTempPerm)[0x100:0x104]

        if 'NCCH' not in checkTempOut:
            print '\nERROR: Got \"' + checkTempOut + "\"; expected \"NCCH\" - Invalid Titlekey"
            raise SystemExit(0)

        print 'Titlekey successfully verified to match title ID ' + titleid
        raise SystemExit(0)

    if os.path.exists(outfname) == 0 or forceDownload == 1 or os.path.getsize(outfname) != unpack('>Q', tmd[cOffs+8:cOffs+16])[0]:
        if noDownload == 0:
            response = urllib2.urlopen(baseurl + '/' + cID)
            chunk_read(response, outfname, report_hook=chunk_report)

            #If we redownloaded the content, then decrypting it is implied.
            decrypt_file(titlekey, outfname, outfname + ".dec", cIDX + "0000000000000000000000000000")

        else :
            print("Content Link:  %s\n Target File:  %s\n\n" % (baseurl + '/' + cID, outfname))
            noDownloadFile.write("%s:%s\n"%(outfname,baseurl+'/'+cID))
            continue
    elif os.path.exists(outfname + '.dec') == 0 or forceDecrypt == 1 or os.path.getsize(outfname + '.dec') != unpack('>Q', tmd[cOffs+8:cOffs+16])[0]:
        decrypt_file(titlekey, outfname, outfname + ".dec", cIDX + "0000000000000000000000000000")

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
            print 'hash mismatched, Decryption likely failed, wrong key or file modified?'
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

print("\n")
print("The NCCH on eShop games is encrypted and cannot be used")
print("without decryption on a 3DS. To fix this you should copy")
print("all .dec files in the Title ID folder to \"/D9Game/\"")
print("on your SD card, then use the following option in Decrypt9:")
print("\n")
print("\"Game Decryptor Options\" > \"NCCH/NCSD Decryptor\"")
print("\n")
print("Once you have decrypted the files, copy the .dec files from")
print("\"/D9Game/\" back into the Title ID folder, overwriting them.")
print("\n")
raw_input("Press Enter once you have done this...")

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
