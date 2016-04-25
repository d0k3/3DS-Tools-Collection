# FunkyCIA2 (FunkyCIA v2.1)
# - preinstalled game/app creation is not broken (stopped wiping the ticket id)
# - added -personal, so that CIAs can be made for your own console, = not sharable, they should only work for your 3ds, although last time I checked for some reason they still do not install...

import sys
import os
import re
import binascii
from struct import unpack, pack
import urllib2
import argparse
import string
import hashlib
import datetime
from collections import namedtuple
from collections import Counter

if not sys.version_info[:2] == (2, 7):
    print '*****\n!!!!!Warning - Only tested with Python 2.7!!!!!\n*****\n'

windoze = '9c4f88f706dedde3bc0ebb66e34963e5'
magic = binascii.a2b_hex('00010004919EBE464AD0F552CD1B72E7884910CF55A9F02E50789641D896683DC005BD0AEA87079D8AC284C675065F74C8BF37C88044409502A022980BB8AD48383F6D28A79DE39626CCB2B22A0F19E41032F094B39FF0133146DEC8F6C1A9D55CD28D9E1C47B3D11F4F5426C2C780135A2775D3CA679BC7E834F0E0FB58E68860A71330FC95791793C8FBA935A7A6908F229DEE2A0CA6B9B23B12D495A6FE19D0D72648216878605A66538DBF376899905D3445FC5C727A0E13E0E2C8971C9CFA6C60678875732A4E75523D2F562F12AABD1573BF06C94054AEFA81A71417AF9A4A066D0FFC5AD64BAB28B1FF60661F4437D49E1E0D9412EB4BCACF4CFD6A3408847982000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000526F6F742D43413030303030303033000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000158533030303030303063000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000137A0894AD505BB6C67E2E5BDD6A3BEC43D910C772E9CC290DA58588B77DCC11680BB3E29F4EABBB26E98C2601985C041BB14378E689181AAD770568E928A2B98167EE3E10D072BEEF1FA22FA2AA3E13F11E1836A92A4281EF70AAF4E462998221C6FBB9BDD017E6AC590494E9CEA9859CEB2D2A4C1766F2C33912C58F14A803E36FCCDCCCDC13FD7AE77C7A78D997E6ACC35557E0D3E9EB64B43C92F4C50D67A602DEB391B06661CD32880BD64912AF1CBCB7162A06F02565D3B0ECE4FCECDDAE8A4934DB8EE67F3017986221155D131C6C3F09AB1945C206AC70C942B36F49A1183BCD78B6E4B47C6C5CAC0F8D62F897C6953DD12F28B70C5B7DF751819A9834652625000100010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000010003704138EFBBBDA16A987DD901326D1C9459484C88A2861B91A312587AE70EF6237EC50E1032DC39DDE89A96A8E859D76A98A6E7E36A0CFE352CA893058234FF833FCB3B03811E9F0DC0D9A52F8045B4B2F9411B67A51C44B5EF8CE77BD6D56BA75734A1856DE6D4BED6D3A242C7C8791B3422375E5C779ABF072F7695EFA0F75BCB83789FC30E3FE4CC8392207840638949C7F688565F649B74D63D8D58FFADDA571E9554426B1318FC468983D4C8A5628B06B6FC5D507C13E7A18AC1511EB6D62EA5448F83501447A9AFB3ECC2903C9DD52F922AC9ACDBEF58C6021848D96E208732D3D1D9D9EA440D91621C7A99DB8843C59C1F2E2C7D9B577D512C166D6F7E1AAD4A774A37447E78FE2021E14A95D112A068ADA019F463C7A55685AABB6888B9246483D18B9C806F474918331782344A4B8531334B26303263D9D2EB4F4BB99602B352F6AE4046C69A5E7E8E4A18EF9BC0A2DED61310417012FD824CC116CFB7C4C1F7EC7177A17446CBDE96F3EDD88FCD052F0B888A45FDAF2B631354F40D16E5FA9C2C4EDA98E798D15E6046DC5363F3096B2C607A9D8DD55B1502A6AC7D3CC8D8C575998E7D796910C804C495235057E91ECD2637C9C1845151AC6B9A0490AE3EC6F47740A0DB0BA36D075956CEE7354EA3E9A4F2720B26550C7D394324BC0CB7E9317D8A8661F42191FF10B08256CE3FD25B745E5194906B4D61CB4C2E000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000526F6F7400000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001434130303030303030330000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000007BE8EF6CB279C9E2EEE121C6EAF44FF639F88F078B4B77ED9F9560B0358281B50E55AB721115A177703C7A30FE3AE9EF1C60BC1D974676B23A68CC04B198525BC968F11DE2DB50E4D9E7F071E562DAE2092233E9D363F61DD7C19FF3A4A91E8F6553D471DD7B84B9F1B8CE7335F0F5540563A1EAB83963E09BE901011F99546361287020E9CC0DAB487F140D6626A1836D27111F2068DE4772149151CF69C61BA60EF9D949A0F71F5499F2D39AD28C7005348293C431FFBD33F6BCA60DC7195EA2BCC56D200BAF6D06D09C41DB8DE9C720154CA4832B69C08C69CD3B073A0063602F462D338061A5EA6C915CD5623579C3EB64CE44EF586D14BAAA8834019B3EEBEED3790001000100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')

logfile = str(datetime.datetime.now()).replace(' ', '_').replace(':', '-') + '.txt'
usedlog = 0
def writeInLog(msg):
    global usedlog
    usedlog = 1
    f = open(logfile, "a")
    f.write(msg+"\n")
    f.close()

execname = './make_cdn_cia'
if hashlib.md5(sys.platform).hexdigest() == windoze:
    execname = 'make_cdn_cia.exe'

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
SYMBOLS = {
    'customary'     : ('B', 'KB', 'MB', 'GB', 'T', 'P', 'E', 'Z', 'Y'),
}
def bytes2human(n, format='%(value).2f %(symbol)s', symbols='customary'):
    n = int(n)
    if n < 0:
        raise ValueError("n < 0")
    symbols = SYMBOLS[symbols]
    prefix = {}
    for i, s in enumerate(symbols[1:]):
        prefix[s] = 1 << (i+1)*10
    for symbol in reversed(symbols[1:]):
        if n >= prefix[symbol]:
            value = float(n) / prefix[symbol]
            return format % locals()
    return format % dict(symbol=symbols[0], value=n)
##########


parser = argparse.ArgumentParser()
parser.add_argument('inputfile', action='store', help='The ticket.db file')
choose = parser.add_mutually_exclusive_group()
choose.add_argument('-type', nargs='+', choices=['gameapp', 'update', 'dlc', 'demo', 'dsiware', 'system', 'ALL'], dest='chosentypelist', help='The types of contents that you wish to be downloaded')
choose.add_argument('-title', nargs='+', dest='specific_titles', help='Give TitleIDs to be specifically downloaded')
parser.add_argument('-ignoretitles', nargs='+', dest='ignore_titles', help='Give TitleIDs that will be ignored.')
parser.add_argument('-outputdir', action='store', dest='output_dir', help='The custom output directory to store output in, if desired')
parser.add_argument('-nosort', action='store_false', default=True, dest='sort', help='Turn OFF sorting of the titles into folders based on their type (eshop app, update, dlc, etc).')
parser.add_argument('-nodownload', action='store_false', default=True, dest='download', help='Turn OFF content downloading - will not generate CIA files.')
parser.add_argument('-nobuild', action='store_false', default=True, dest='build', help='Turn OFF generation of CIA files, titles will be downloaded only.')
parser.add_argument('-noignore', action='store_false', default=True, dest='ignorefake', help='Using this will stop tickets that are not attached to your eshop account from being ignored')
parser.add_argument('-nopatchdlc', action='store_false', default=True, dest='patch_dlc', help='This will disable unlocking all DLC content')
parser.add_argument('-nopatchdemo', action='store_false', default=True, dest='patch_demo', help='This will disable patching the demo play limit')
parser.add_argument('-personal', action='store_false', default=True, dest='blank_ids', help='Using this flag will disable blanking the device unique IDs in the CIA. Hopefully this can be used to make PERFECT backup CIAs that ONLY work with your console.')
parser.add_argument('-preinstalled', action='store_true', default=False, dest='preinstalled', help='Using this flag with ONE Title ID will make sure the correct ticket is chosen when making a CIA from a presinstalled game/app :) (maybe not required... but it will only help).')
parser.add_argument('-retry', type=int, default=4, dest='retry_count', choices=range(0, 10), help='How many times a file download will be attempted')

parser.add_argument('-db', action='store', dest='use_ticket', help='-')
parser.add_argument('-key', action='store', dest='use_key', help='-')


arguments = parser.parse_args()

tk = 0x140
badtitle = False
dlSystem = False
dlALL = False
typelist = []
titlelist = []
ignorelist = []
error = False

eshopapp = 0
dlp = 0
demo = 0
updatepatch = 0
dlc = 0
dsiware = 0
dsisysapp = 0
dsisysdata = 0
mystery = 0
system = 0
anything = 0

if (arguments.chosentypelist is arguments.specific_titles):
    print 'Please either choose one or more content types to download (-type gameapp update dlc demo dsiware system ALL)'
    print 'OR type one or more specific titles (-title TITLEID1 TITLEID2)'
    sys.exit(0)

if arguments.chosentypelist is not None:
    if 'gameapp' in arguments.chosentypelist: typelist.append('0000')
    if 'demo' in arguments.chosentypelist: typelist.append('0002')
    if 'update' in arguments.chosentypelist: typelist.append('000e')
    if 'dlc' in arguments.chosentypelist: typelist.append('008c')
    if 'dsiware' in arguments.chosentypelist: typelist.append('8004')
    if 'system' in arguments.chosentypelist: dlSystem = True
    if 'ALL' in arguments.chosentypelist: dlALL = True

if arguments.specific_titles is not None:
    for specific_title in arguments.specific_titles:
        if (len(specific_title) is 16) and all(c in string.hexdigits for c in specific_title):
            titlelist.append(specific_title.lower())
        else:
            print 'The Title ID(s) must be 16 hexadecimal characters long'
            print specific_title + ' - is not ok.'
            print ''
            badtitle = True
if badtitle: #if any title that was specified was not ok, quit
    sys.exit(0)

if arguments.ignore_titles is not None:
    for ignore_title in arguments.ignore_titles:
        if (len(ignore_title) is 16) and all(c in string.hexdigits for c in ignore_title):
            ignorelist.append(ignore_title.lower())
        else:
            print 'The Title ID(s) must be 16 hexadecimal characters long'
            print ignore_title + ' - is not ok.'
            print ''
            badtitle = True
if badtitle: #if any title that was specified was not ok, quit
    sys.exit(0)

if arguments.preinstalled:
    if arguments.specific_titles is not None:
        if len(arguments.specific_titles) > 1:
            print 'Please one give only ONE Title ID'
            sys.exit(0)
    else:
        print 'For a preinstalled game, please specify ONE title with, like \'-title TITLEID -preinstalled\', using the Title ID of your game'
        sys.exit(0)
    arguments.ignorefake = False



print '*******\nFunkyCIA2 by cearp - FunkyCIA v2.1\n*******\n'

ticketlist = []
not_eshop_tickets = []
eshop_tickets = []
completetitleids = []
Ticket = namedtuple('Ticket', ['data', 'titleid', 'consoleid', 'commonkeyindex'])

if not os.path.isfile(arguments.inputfile):
    print 'The input file does not exist.'
    sys.exit(0)

with open(arguments.inputfile, 'rb') as fh:
    ticks = fh.read()

ticketOffsets = [m.start() for m in re.finditer(b'Root-CA00000003-XS0000000c', ticks)]
ticks = bytearray(ticks)

#This check can fail on other DB files and stuff (since 'Root-CA' can appear in them, but not necessarily mean there are tickets).
#Just make sure to only pass in a ticket.db file or individual tickets (or a file with a bunch of individual ones merged).
if (len(ticketOffsets) == 0):
    print 'No tickets found. Did you input the correct file?'
    sys.exit(0)



for offs in ticketOffsets:

    commonKeyIndex = ticks[offs+0xB1]
    if ticks[offs+0x7C] != 0x1: #Try and make sure we're actually dealing with a ticket(this value is always 0x1 in a ticket).
        continue
    if commonKeyIndex > 5: #There's some master rusemen in ticket.db that get past the other checks.
        continue

    anything = anything + 1

    ticketData = bytearray(ticks[offs-0x140:offs+0x210])
    ticketlist.append(  Ticket(ticketData, binascii.hexlify(ticketData[tk+0x9C:tk+0xA4]).lower(), binascii.hexlify(ticketData[tk+0x98:tk+0x9C]), ticks[offs+0xB1]    )   )


print 'Number of Tickets                       - ' + str(len(ticketlist))
dupetitles = []
y=Counter()
for tiktik in ticketlist:
    y[tiktik.titleid] += 1
dupetitles = [i for i in y if y[i]>1]
print 'Number of Titles with Duplicates        - ' + str(len([i for i in y if y[i]>1]))
print 'Number of Unique Title Tickets          - ' + str( len (list(y) ) )

systik = 0
for tiktik in ticketlist:
    typecheck = tiktik.titleid[4:8]
    if (int(typecheck,16) & 0x10):
        systik += 1
    elif (typecheck == '8005'):
        systik += 1
    elif (typecheck == '800f'):
        systik += 1
print 'Number of System Tickets (ignored)      - ' + str(systik)


#does not look at system titles
for tiktik in ticketlist:
    if (tiktik.commonkeyindex == 0):
        if arguments.ignorefake: 
            if (tiktik.consoleid == '00000000'):
                not_eshop_tickets.append(tiktik)
            else:
                eshop_tickets.append(tiktik)
        else:
            eshop_tickets.append(tiktik)

if(arguments.ignorefake):

    print ''
    print 'Number of eShop Tickets                 - ' + str(len(eshop_tickets))

    dupetitles = []
    y=Counter()
    for tiktik in eshop_tickets:
        y[tiktik.titleid] += 1
    dupetitles = [i for i in y if y[i]>1]
    print 'Number of eShop Titles with Duplicates  - ' + str(len([i for i in y if y[i]>1]))
    print 'Number of Unique eShop Titles           - ' + str( len (list(y) ) )

    print 'Number of (non system) Tickets NOT from your eShop (ignored)     - ' + str(len(not_eshop_tickets))
    print '^^ can be installed CIAs, preinstalled games/apps etc... things not from YOUR eshop'
    print '^^ if you want to dump your preinstalled game, you need to use -preinstalled'

print ''

print 'Going through the list...\n'
#reverse because newest ticket is at the bottom (maybe not a 100% fact?) (not really needed anyway  i think)
for tiktik in reversed(eshop_tickets):

    titleid = tiktik.titleid
    typecheck = titleid[4:8]

    if (typecheck in typelist) or (dlSystem and tiktik.commonkeyindex) or dlALL or (titleid in titlelist):

        if titleid in completetitleids:
            continue

        if titleid in ignorelist:
            print 'You are ignoring this title...'
            continue

        if (binascii.hexlify(tiktik.data[0x00:0x04]) != '00010004'):
            print '***\nTitle ID: ' + titleid
            print 'Bad Ticket Found... ignoring'
            print 'There should be a good ticket later, no problem\n***\n'
            continue

        if arguments.preinstalled:
            if (tiktik.consoleid == '00000000'):
                print 'Looks like we found the preinstalled game!\n'
            else:
                continue


        if (typecheck == '0000'):
            titletype = 'eShopApp'
            eshopapp = eshopapp + 1
        elif (typecheck == '0001'):
            titletype = 'DownloadPlayChild'
            dlp = dlp +1
        elif (typecheck == '0002'):
            titletype = 'Demo'
            demo = demo +1
            if(arguments.patch_demo):
                tiktik.data[tk+0x124:tk+0x164] = binascii.a2b_hex('00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        elif (typecheck == '000e'):
            titletype = 'UpdatePatch'
            updatepatch = updatepatch + 1
        elif (typecheck == '008c'):
            titletype = 'DLC'
            dlc = dlc + 1
            if(arguments.patch_dlc):
                tiktik.data[tk+0x164:tk+0x210] = binascii.a2b_hex('00010014000000ac000000140001001400000000000000280000000100000084000000840003000000000000ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        elif (typecheck == '8004'):
            titletype = 'DSiWare'
            dsiware = dsiware + 1
        #system apps
        elif (int(typecheck,16) & 0x10):
            titletype = 'System'
            system = system + 1
        elif (typecheck == '8005'):
            titletype = 'DSiSystemApp'
            dsisysapp = dsisysapp + 1
        elif (typecheck == '800f'):
            titletype = 'DSiSystemDataArchives'
            dsisysdata = dsisysdata + 1
        else:
            titletype = 'OtherContent---Mystery'
            print '??? No Idea what this is, probably cannot make a CIA. - ' + titleid
            print 'Skipping title...'
            mystery = mystery + 1
            continue

        if(arguments.blank_ids):
            tiktik.data[tk+0x98:tk+0x9C] = binascii.a2b_hex('00000000')
            tiktik.data[tk+0xDC:tk+0xE0] = binascii.a2b_hex('00000000')

        if(arguments.output_dir is not None):
            if(arguments.sort):
                rawdir = os.path.join(arguments.output_dir, 'raw', titletype, titleid)
                ciadir = os.path.join(arguments.output_dir, 'cia', titletype, titleid)
            else:
                rawdir = os.path.join(arguments.output_dir, 'raw', titleid)
                ciadir = os.path.join(arguments.output_dir, 'cia', titleid)
        else:
            if(arguments.sort):
                rawdir = os.path.join('raw', titletype, titleid)
                ciadir = os.path.join('cia', titletype, titleid)
            else:
                rawdir = os.path.join('raw', titleid)
                ciadir = os.path.join('cia', titleid)

        if not os.path.exists(rawdir):
            os.makedirs(os.path.join(rawdir))
        open(os.path.join(rawdir, 'cetk'),'wb').write(tiktik.data+magic)

        completetitleids.append(titleid)


        #download stuff
        if(arguments.download):
            print 'Downloading TMD...'

            if error:
                error = False

            baseurl = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/' + titleid

            for attempt in range(arguments.retry_count+1):
                try:
                    if(attempt > 0):
                        print '*Attempt ' + str(attempt+1) + ' of ' + str(arguments.retry_count+1)
                    tmd = urllib2.urlopen(baseurl + '/tmd')
                except urllib2.URLError, e:
                    print 'Could not download TMD...'
                    error = True
                    continue
                error = False
                print 'Downloaded TMD OK!'
                break
            
            if error:
                print 'ERROR: Could not download TMD. Skipping title...\n'
                writeInLog('Trouble downloading tmd:  ' + baseurl + '/tmd')
                writeInLog('CIA not created:  ' + titleid)

            if not error:

                print ''

                tmd = tmd.read()
                open(os.path.join(rawdir) + '/tmd','wb').write(tmd)

                #download stuff
                print 'Downloading Contents...'

                contentCount = int(binascii.hexlify(tmd[tk+0x9E:tk+0xA0]),16)
                for i in xrange(contentCount):
                    print i
                    if not error:
                        cOffs = 0xB04+(0x30*i)
                        cID = binascii.hexlify(tmd[cOffs:cOffs+0x04])
                        print 'Downloading ' + str(i+1) + ' of ' + str(contentCount) + '. This file is ' + bytes2human(int(binascii.hexlify(tmd[cOffs+0x08:cOffs+0x10]),16))
                        outfname = os.path.join(rawdir, cID)
                        
                        for attempt in range(arguments.retry_count+1):
                            try:
                                if(attempt > 0):
                                    print 'Attempt ' + str(attempt+1) + ' of ' + str(arguments.retry_count+1)
                                response = urllib2.urlopen(baseurl + '/' + cID)
                                chunk_read(response, outfname, report_hook=chunk_report)
                                if (int(os.path.getsize(outfname)) != int(binascii.hexlify(tmd[cOffs+0x08:cOffs+0x10]),16) ):
                                    print 'Content download not correct size\n'
                                    continue
                            except urllib2.URLError, e:
                                print 'Could not download content file...\n'
                                error = True
                                continue
                            error = False
                            break
                        
                        if error:
                            print 'ERROR: Could not download content file... Skipping title'
                            writeInLog('Could not download content file:  ' + baseurl + '/' + cID)
                            writeInLog('CIA not created:  ' + titleid)
                        
                        print ''
                

                if not error:
                    print 'Title download complete\n'

                    #cia generation
                    if(arguments.build):
                        if not os.path.exists(ciadir):
                            os.makedirs(ciadir)
                        makecommand = ' ' + os.path.join(rawdir) + ' ' + os.path.join(ciadir, titleid) + '.cia'
                        os.system(execname + makecommand)
                        if(os.path.isfile(os.path.join(ciadir, titleid) + '.cia')):
                            print 'CIA created ok!'
                        else:
                            print 'CIA not created...'
                            writeInLog('CIA not created:  ' + titleid)
                        print ''
                        print ''




print 'eShop Apps            -  ' + str(eshopapp)
print 'Download Play Child   -  ' + str(dlp)
print 'Demo                  -  ' + str(demo)
print 'Update Patches        -  ' + str(updatepatch)
print 'DLC                   -  ' + str(dlc)
print 'System                -  ' + str(system)
print 'DSiWare               -  ' + str(dsiware)
print 'DSi System Apps       -  ' + str(dsisysapp)
print 'DSi System Data       -  ' + str(dsisysdata)
print 'Mystery Content       -  ' + str(mystery)
total = eshopapp + demo + dlp + updatepatch + dlc + system + dsiware + dsisysapp + dsisysdata + mystery
print '\nAll tickets/titles found in file (might contain duplicates) - ' + str(anything) +  '. You selected ' + str(total) + ' of them'

if(usedlog):
    print '\n\n***\n' + '*** ' + ' A log file was created - errors/problems are listed in there.\n' + '***'
