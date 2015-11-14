#!/usr/bin/env python2
# This script is awful, but it 'works for me'(TM)

import sys
import os
import re
import binascii
import struct

# encTitleKeys.bin format
#
#  4 bytes  Number of entries
# 12 bytes  Reserved
#
# entry(32 bytes in size):
#   4 bytes  Common key index(0-5)
#   4 bytes  Reserved
#   8 bytes  Title Id
#  16 bytes  Encrypted title key

if len(sys.argv) < 2:
    print 'Usage: dump_ticket_keys.py ticket.db'
    print 'Instead of ticket.db, you can also pass in an individual ticket'
    print 'or many tickets merged together'
    sys.exit(0)

if not os.path.isfile(sys.argv[1]):
    print "Input file '%s' doesn't exist." % sys.argv[1]
    raise SystemExit(0)

with open(sys.argv[1], 'rb') as fh:
    ticks = fh.read()

ticketOffsets = [m.start() for m in re.finditer(b'Root-CA00000003-XS0000000c', ticks)]

ticks = bytearray(ticks)

# This check can fail on other DB files, etc (since 'Root-CA'
# can appear in them, but not necessarily mean there are tickets).
# Just make sure to only pass in a ticket.db file or individual
# tickets (or a file with a bunch of individual ones merged).
if len(ticketOffsets) == 0:
    print 'No tickets found. Did you input the correct file?'
    sys.exit(0)

encKeys = []

for offs in ticketOffsets:
    encKey = ticks[offs+0x7F:offs+0x8F]
    tId = ticks[offs+0x9C:offs+0xA4]
    commonKeyIndex = ticks[offs+0xB1]
    
    if [encKey, tId, commonKeyIndex] in encKeys:
        continue
    if ticks[offs+0x7C] != 0x1:  # This value is always 0x1 in a ticket.
        continue
    if commonKeyIndex > 5:
        continue

    # if commonKeyIndex != 0:  # Uncomment these two lines to grab just eShop ticket info.
    #     continue

    print 'Encrypted title key:  ' + binascii.hexlify(encKey)
    print 'Title ID:  ' + binascii.hexlify(tId)
    print 'Common key index: %u' % commonKeyIndex
    print ''

    encKeys.append([encKey, tId, commonKeyIndex])

outData = struct.pack('<IIII', len(encKeys), 0, 0, 0)
for entry in encKeys:
    outData += struct.pack('<II', entry[2], 0)
    outData += entry[1]
    outData += entry[0]

open('encTitleKeys.bin', 'wb').write(outData)
