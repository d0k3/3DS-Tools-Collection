#!/usr/bin/env python2
import struct
import os
import sys
from binascii import hexlify

if len(sys.argv) < 2:
    print "Usage: print_ticket_keys.py decTitleKeys.bin"
    sys.exit(0)

if not os.path.isfile(sys.argv[1]):
    print "Input file '%s' doesn't exist." % sys.argv[1]
    raise SystemExit(0)

with open(sys.argv[1], 'rb') as fh:
    nEntries = struct.unpack('<I', fh.read(4))[0]
    fh.seek(12, os.SEEK_CUR)
    
    for i in xrange(nEntries):
        fh.seek(8, os.SEEK_CUR)
        titleId = fh.read(8)
        decryptedTitleKey = fh.read(16)
        print '%s: %s' % (hexlify(titleId), hexlify(decryptedTitleKey))
