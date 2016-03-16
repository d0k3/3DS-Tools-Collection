import struct,os,sys
from binascii import hexlify

def GetIDandSEED(filename):
    tids = []
    seeds = []
    with open(filename,'rb') as savefile:
        savedata = savefile.read()
        while savedata.find('SEEDDB')>=0:
            SBoffset = savedata.find('SEEDDB')
            tidoffset = (struct.unpack('<I',savedata[SBoffset+24:SBoffset+28])[0] - 1) * 4096 + SBoffset - 52 + 4096
            seedoffset = tidoffset + 16000
            titlecount = struct.unpack('<I',savedata[tidoffset-4092:tidoffset-4088])[0]
            try:
                for i in range(titlecount):
                    tid = savedata[tidoffset:tidoffset+8]
                    seed = savedata[seedoffset:seedoffset+16]
                    if not tid in tids:
                        tids.append(tid)
                        seeds.append(seed)
                        print 'TitleID: ' + hexlify(reverseByteArray(tid)),' SEED: ' + hexlify(seed)
                    tidoffset += 8
                    seedoffset += 16
            except:
                print 'No SEED found in this partition.'
            finally:
                savedata = savedata[seedoffset:]
    return tids,seeds

def reverseByteArray(bytearr):
    outarr = ''
    for i in range(0, bytearr.__len__())[::-1]:
        outarr += bytearr[i]
    return outarr

if __name__ == '__main__':
    tids = []
    seeds = []
    if len(sys.argv)<2:
        print 'Usage: seeddb_gen.py file(s)'
        sys.exit()
    
    if '-h'in sys.argv or '-help' in sys.argv:
        print 'Usage: seeddb_gen.py file(s)\n'
        print "SEEDDB is stored in 'nand:\\data<console-unique>\\sysdata\\0001000f\\'"
        print 'Decyrpt NAND FAT16 partition and dump these files for this script.'
        sys.exit()
    
    for filename in sys.argv[1:]:
        titleid,seed = GetIDandSEED(filename)
        tids += titleid
        seeds += seed
    
    if len(tids)<1:
        print 'No SEED found.'
        sys.exit()

    outpath = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'seeddb.bin')
    with open(outpath,'wb') as seeddb:
        print '\nGenerating seeddb.bin ...'
        seeddb.write(struct.pack('<I',len(tids)))
        seeddb.write('\x00'*12)
        for i in range(len(tids)):
            seeddb.write(tids[i]+seeds[i]+('\x00'*8))
    print 'done!'
