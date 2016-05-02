#!/usr/bin/env python3
#script is a replacement for https://github.com/Relys/3DS_Multi_Decryptor/blob/master/to3DS/CDNto3DS/CDNto3DS.py
#requires PyCrypto to be installed ("python3 -m ensurepip" then "pip3 install PyCrypto")
#requires makerom (https://github.com/profi200/Project_CTR/releases)
#this is a Python 3 script

from xml.dom import minidom
from subprocess import DEVNULL, STDOUT, call, check_call
from struct import pack, unpack
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from hashlib import sha256
from imp import reload
import platform
import os
import struct
import errno
import shlex
import ssl
import sys
import urllib.request, urllib.error, urllib.parse

##########From http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
def pmkdir(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

##########From http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
def which(program):
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

##########Based on https://stackoverflow.com/questions/5783517/downloading-progress-bar-urllib2-python
def report_chunk(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    sys.stdout.write('\rDownloaded and decrypted %d of %d bytes (%0.2f%%)' % (bytes_so_far, total_size, percent))
    sys.stdout.flush()
    if bytes_so_far >= total_size:
        print('')

# download in 0x200000 byte chunks, decrypt the chunk with IVs described below, then write the decrypted chunk to disk (half the file size of decrypting separately!)
def read_chunk(response, f_out, intitle_key, first_iv, chunk_size=0x200000, report_hook=None):
    file_handler = open(f_out,'wb')
    total_size = int(response.getheader('Content-Length'))
    total_size = int(total_size)
    bytes_so_far = 0
    data = []
    first_read_chunk = 0
    while 1:
        if report_hook:
            report_hook(bytes_so_far, chunk_size, total_size)
        chunk = response.read(chunk_size)
        bytes_so_far += len(chunk)
        if not chunk:
             break
        # IV of first chunk should be the Content ID + 28 0s like with the entire file, but each subsequent chunk should be the last 16 bytes of the previous still ciphered chunk
        if first_read_chunk == 0:
            decryptor = AES.new(intitle_key, AES.MODE_CBC, unhexlify(first_iv))
            first_read_chunk = 1
        else:
            decryptor = AES.new(intitle_key, AES.MODE_CBC, prev_chunk[(0x200000 - 16):0x200000])
        dec_chunk = decryptor.decrypt(chunk)
        prev_chunk = chunk
        file_handler.write(dec_chunk)
    file_handler.close()

def system_usage():
    print('Usage: PlaiCDN <TitleID TitleKey> <Options> for content options')
    print('-redown   : redownload content')
    print('-no3ds    : don\'t build 3DS file')
    print('-nocia    : don\'t build CIA file')
    print('-nobuild  : don\'t build 3DS or CIA')
    print('-nohash   : ignore hash checks')
    print('-nowait   : no crypt message/waiting for input')
    print('-check    : checks if title id matches key')
    print('')
    print('Usage: PlaiCDN <TitleID> for general options')
    print('-info     : to display detailed metadata')
    print('-seed     : generates game-specific seeddb file when using -info')
    print('')
    print('Usage: PlaiCDN <Options> for decTitleKeys.bin options')
    print('-deckey   : print keys from decTitleKeys.bin')
    print('-checkbin : checks titlekeys from decTitleKeys.bin')
    print('-checkall : check all titlekeys when using -checkbin')
    print('-fast     : skips name retrieval when using -checkbin, cannot be used with seed/seeddb')
    print('-seeddb   : generates a single seeddb.bin')
    raise SystemExit(0)

def getTitleInfo(title_id):
    tid_high = ((hexlify(title_id)).decode()).upper()[:8]
    tid_index = ['00040010', '0004001B', '000400DB', '0004009B',
                 '00040030', '00040130', '00040138', '00040001',
                 '00048005', '0004800F', '00040002', '0004008C']
    res_index = ['-System Application-', '-System Data Archive-', '-System Data Archive-', '-System Data Archive-',
                 '-System Applet-', '-System Module-', '-System Firmware-', '-Download Play Title-',
                 '-TWL System Application-', '-TWL System Data Archive-', '-Game Demo-', '-Addon DLC-']
    if fast == 1 and gen_seed != 1:
        tid_index.extend(['00040000', '0004000E'])
        res_index.extend(['-eShop Content-', '-eShop Content Update-'])
    if tid_high in tid_index:
        return(res_index[tid_index.index(tid_high)], '---', '-------', '------', '', '---', '---')
        title_name_stripped, region, product_code, publisher, crypto_seed, curr_version, title_size

    # create new SSL context to load decrypted CLCert-A off directory, key and cert are in PEM format
    # see https://github.com/SciresM/ccrypt
    ctr_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    ctr_context.load_cert_chain('ctr-common-1.crt', keyfile='ctr-common-1.key')

    # ninja handles handles actions that require authentication, in addition to converting title ID to internal the CDN content ID
    ninja_url = 'https://ninja.ctr.shop.nintendo.net/ninja/ws/titles/id_pair'
    ec_url = 'https://ninja.ctr.shop.nintendo.net/ninja/ws/'

    # use GET request with parameter "title_id[]=mytitle_id" with SSL context to retrieve XML response
    try:
        shop_request = urllib.request.Request(ninja_url + '?title_id[]=' + (hexlify(title_id)).decode())
        shop_request.get_method = lambda: 'GET'
        response = urllib.request.urlopen(shop_request, context=ctr_context)
        xml_response = minidom.parseString((response.read()).decode('UTF-8', 'replace'))
    except urllib.error.URLError as e:
        raise

    # set ns_uid (the internal content ID) to field from XML
    ns_uid = xml_response.getElementsByTagName('ns_uid')[0].childNodes[0].data

    # samurai handles metadata actions, including getting a title's info
    # URL regions are by country instead of geographical regions... for some reason
    samurai_url = 'https://samurai.ctr.shop.nintendo.net/samurai/ws/'
    region_array = ['JP', 'HK', 'TW', 'KR', 'DE', 'FR', 'ES', 'NL', 'IT', 'US', 'GB']
    eur_array = ['GB', 'DE', 'FR', 'ES', 'NL', 'IT']
    region = ''

    # try loop to figure out which region the title is from; there is no easy way to do this other than try them all
    for country_code in region_array:
        try:
            title_request = urllib.request.Request(samurai_url + country_code + '/title/' + ns_uid)
            titleResponse = urllib.request.urlopen(title_request, context=ctr_context)
            ec_request = urllib.request.Request(ec_url + country_code + '/title/' + ns_uid + '/ec_info')
            ec_response = urllib.request.urlopen(ec_request, context=ctr_context)
        except urllib.error.URLError as e:
            pass
        else:
            if ('JP') in country_code:
                region = region + 'JPN'
            if ('US') in country_code:
                region = region + 'USA'
            if ('TW') in country_code:
                region = region + 'TWN'
            if ('HK') in country_code:
                region = region + 'HKG'
            if ('KR') in country_code:
                region = region + 'KOR'
            if country_code in eur_array and 'EUR' not in region:
                region = region + 'EUR'
    if region == '':
        raise
    if len(region) > 3:
        region = 'ALL'

    # get info from the returned XMs from the URL
    xml_response = minidom.parseString((titleResponse.read()).decode('UTF-8'))
    title_name = xml_response.getElementsByTagName('name')[0].childNodes[0].data
    title_name_stripped = title_name.replace('\n', ' ')
    publisher = xml_response.getElementsByTagName('name')[2].childNodes[0].data
    product_code = xml_response.getElementsByTagName('product_code')[0].childNodes[0].data

    xml_response = minidom.parseString((ec_response.read()).decode('UTF-8'))
    curr_version = xml_response.getElementsByTagName('title_version')[0].childNodes[0].data
    title_size = '{:.5}'.format(int(xml_response.getElementsByTagName('content_size')[0].childNodes[0].data) / 1000000)

    try:
        crypto_seed = xml_response.getElementsByTagName('external_seed')[0].childNodes[0].data
    except:
        crypto_seed = ''

    # some windows unicode character bullshit
    if 'Windows' in platform.system():
        title_name_stripped = ''.join([i if ord(i) < 128 else ' ' for i in title_name_stripped])
        publisher = ''.join([i if ord(i) < 128 else ' ' for i in publisher])

    return(title_name_stripped, region, product_code, publisher, crypto_seed, curr_version, title_size)

#=========================================================================================================
# Seeddb implementation
class crypto_handler:
    def __init__(self):
        self.crypto_db = {}
    def add_seed(self, title_id, title_key):
        self.crypto_db.update({title_id: title_key})
    def gen_seeddb(self):
        if self.crypto_db:
            if '-seeddb' in sys.argv:
                self.write_seed()
            else:
                for title_id in self.crypto_db:
                    self.write_seed(title_id)
    def write_seed(self, title_id=None):
        # Providing title_id makes a title specific seeddb
        if title_id:
            pmkdir(title_id)
            s_out = title_id+'/seeddb.bin'
            seed_db = {title_id: self.crypto_db[title_id]}
        else:
            s_out = 'seeddb.bin'
            seed_db = self.crypto_db
        with open(s_out, 'wb') as seeddb_handler:
            seed_count = hex(len(seed_db)).split('x')[1].zfill(32)
            seed_count = "".join(reversed([seed_count[i:i+2] for i in range(0, len(seed_count), 2)]))
            seeddb_handler.write(unhexlify(seed_count))
            for title_id in seed_db:
                # Title_id is reversed in seeddb.bin
                seed_title = "".join(reversed([title_id[i:i+2] for i in range(0, len(title_id), 2)]))
                seed_crypto = seed_db[title_id]
                seed_padding = "".zfill(16)
                seed = unhexlify(seed_title+seed_crypto+seed_padding)
                seeddb_handler.write(seed)
            seeddb_handler.close()
gen_seed = 0
fast = 0
for i in range(len(sys.argv)):
    if sys.argv[i] in ['-seed', '-seeddb']: gen_seed = 1
    elif sys.argv[i] == '-fast': fast = 1
crypto_db = crypto_handler()
#=========================================================================================================

#from https://github.com/Relys/3DS_Multi_Decryptor/blob/master/ticket-title_key_stuff/printKeys.py
for i in range(len(sys.argv)):
    if sys.argv[i] == '-deckey':
        with open('decTitleKeys.bin', 'rb') as file_handler:
            n_entries = os.fstat(file_handler.fileno()).st_size / 32
            file_handler.seek(16, os.SEEK_SET)
            for i in range(int(n_entries)):
                file_handler.seek(8, os.SEEK_CUR)
                title_id = file_handler.read(8)
                decrypted_title_key = file_handler.read(16)
                print('%s: %s' % ((hexlify(title_id)).decode(), (hexlify(decrypted_title_key)).decode()))
        raise SystemExit(0)

for i in range(len(sys.argv)):
    if sys.argv[i] == '-info':
        title_id = sys.argv[1]
        if len(title_id) != 16:
            print('Invalid arguments')
            raise SystemExit(0)

        if (not os.path.isfile('ctr-common-1.crt')) or (not os.path.isfile('ctr-common-1.crt')):
                print('\nCould not find certificate files, all secure connections will fail!\n')

        base_url = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/' + title_id
        # download tmd_var and set to object
        try:
            tmd_var = urllib.request.urlopen(base_url + '/tmd')
        except urllib.error.URLError as e:
            print('Could not retrieve tmd; received error: ' + str(e))
            continue
        tmd_var = tmd_var.read()

        content_count = unpack('>H', tmd_var[0x206:0x208])[0]
        for i in range(content_count):
            c_offs = 0xB04+(0x30*i)
            c_id = format(unpack('>I', tmd_var[c_offs:c_offs+4])[0], '08x')
            c_idx = format(unpack('>H', tmd_var[c_offs+4:c_offs+6])[0], '04x')
            c_size = format(unpack('>Q', tmd_var[c_offs+8:c_offs+16])[0], 'd')
            c_hash = tmd_var[c_offs+16:c_offs+48]
            # If content count above 8 (not a normal application), don't make 3ds
            if unpack('>H', tmd_var[c_offs+4:c_offs+6])[0] >= 8:
                make_3ds = 0
            print('')
            print('Content ID:    ' + c_id)
            print('Content Index: ' + c_idx)
            print('Content Size:  ' + c_size)
            print('Content Hash:  ' + (hexlify(c_hash)).decode())
        try:
            ret_title_name_stripped, ret_region, ret_product_code, ret_publisher, ret_crypto_seed, ret_curr_version, ret_title_size = getTitleInfo((unhexlify(title_id)))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            print('\nCould not retrieve CDN data!\n')
            ret_region = '---'
            ret_title_name_stripped = '---Unknown---'
            ret_product_code = '------'
            ret_publisher = '------'
            ret_crypto_seed = ''
            ret_curr_version = '---'
            ret_title_size = '---'

        print('\n~\n')

        print('Title Name: ' + ret_title_name_stripped)
        print('Region: ' + ret_region)
        print('Product Code: ' + ret_product_code)
        print('Publisher: ' + ret_publisher)
        print('Current Version: ' + ret_curr_version)
        if ret_title_size == '---':
            print('Title Size: ' + ret_title_size)
        else:
            print('Title Size: ' + ret_title_size + 'mb')
        if ret_crypto_seed != '':
            print('9.6 Crypto Seed: ' + ret_crypto_seed)
            # Add crypto seed to crypto database
            crypto_db.add_seed(title_id, ret_crypto_seed)
        # Generate seeddb.bin from crypto seed database
        if gen_seed == 1:
            crypto_db.gen_seeddb()
        print('')
        raise SystemExit(0)

for i in range(len(sys.argv)):
    if sys.argv[i] == '-checkbin':
        if (not os.path.isfile('ctr-common-1.crt')) or (not os.path.isfile('ctr-common-1.crt')):
            print('\nCould not find certificate files, all secure connections will fail!')
        check_all = 0
        for i in range(len(sys.argv)):
            if sys.argv[i] == '-checkall': check_all = 1
        with open('decTitleKeys.bin', 'rb') as file_handler:
            n_entries = os.fstat(file_handler.fileno()).st_size / 32
            file_handler.seek(16, os.SEEK_SET)
            final_output = []
            print('')
            # format: Title Name (left aligned) gets 40 characters, Title ID (Right aligned) gets 16, Titlekey (Right aligned) gets 32, and Region (Right aligned) gets 3
            # anything longer is truncated, anything shorter is padded
            print("{0:<40} {1:>16} {2:>32} {3:>3}".format('Name', 'Title ID', 'Titlekey', 'Region'))
            print("-"*100)
            for i in range(int(n_entries)):
                file_handler.seek(8, os.SEEK_CUR)
                title_id = file_handler.read(8)
                decrypted_title_key = file_handler.read(16)
                # regular CDN URL for downloads off the CDN
                base_url = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/' + (hexlify(title_id)).decode()
                tid_high = ((hexlify(title_id)).decode()).upper()[:8]
                if check_all == 0 and (tid_high not in ['00040000', '0004000E', '0004008C']):
                    continue
                # download tmd_var and set to object
                try:
                    tmd_var = urllib.request.urlopen(base_url + '/tmd')
                except urllib.error.URLError as e:
                    continue
                tmd_var = tmd_var.read()
                # try to get info from the CDN, if it fails then set title and region to unknown
                try:
                    ret_title_name_stripped, ret_region, ret_product_code, ret_publisher, ret_crypto_seed, ret_curr_version, ret_title_size = getTitleInfo(title_id)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    print('\nCould not retrieve CDN data!\n')
                    ret_region = '---'
                    ret_title_name_stripped = '---Unknown---'
                    ret_product_code = '------'
                    ret_publisher = '------'
                    ret_crypto_seed = ''
                    ret_curr_version = '---'
                    ret_title_size = '---'

                content_count = unpack('>H', tmd_var[0x206:0x208])[0]
                for i in range(content_count):
                    c_offs = 0xB04+(0x30*i)
                    c_idx = format(unpack('>H', tmd_var[c_offs+4:c_offs+6])[0], '04x')
                    c_id = format(unpack('>I', tmd_var[c_offs:c_offs+4])[0], '08x')
                    # use range requests to download bytes 0 through 271, needed 272 instead of 260 because AES-128-CBC encrypts in chunks of 128 bits
                    try:
                        check_req = urllib.request.Request('%s/%s'%(base_url, c_id))
                        check_req.headers['Range'] = 'bytes=%s-%s' % (0, 271)
                        check_temp = urllib.request.urlopen(check_req)
                    except urllib.error.URLError as e:
                        continue
                # set IV to offset 0xf0 length 0x10 of ciphertext; thanks to yellows8 for the offset
                check_temp_perm = check_temp.read()
                check_iv = check_temp_perm[0xf0:0x100]
                decryptor = AES.new(decrypted_title_key, AES.MODE_CBC, check_iv)
                # check for magic ('NCCH') at offset 0x100 length 0x104 of the decrypted content
                check_temp_out = decryptor.decrypt(check_temp_perm)[0x100:0x104]

                if 'NCCH' not in check_temp_out.decode('UTF-8', 'ignore'):
                    decryptor = AES.new(decrypted_title_key, AES.MODE_CBC, unhexlify(c_idx + '0000000000000000000000000000'))
                    dsi_check_temp_out = decryptor.decrypt(check_temp_perm)[0x60:0x64]

                if 'NCCH' in check_temp_out.decode('UTF-8', 'ignore') or 'WfA' in dsi_check_temp_out.decode('UTF-8', 'ignore'):
                    # format: Title Name (left aligned) gets 40 characters, Title ID (Right aligned) gets 16, Titlekey (Right aligned) gets 32, and Region (Right aligned) gets 3
                    # anything longer is truncated, anything shorter is padded
                    print("{0:<40.40} {1:>16} {2:>32} {3:>3}".format(ret_title_name_stripped, (hexlify(title_id).decode()).strip(), ((hexlify(decrypted_title_key)).decode()).strip(), ret_region))
                    # Add crypto seed to crypto database
                    if ret_crypto_seed != '':
                        crypto_db.add_seed((hexlify(title_id).decode()).strip(), ret_crypto_seed)
            # Generate seeddb.bin from crypto seed database
            if gen_seed == 1:
                crypto_db.gen_seeddb()
            raise SystemExit(0)

#if args for deckeys or checkbin weren't used above, remaining functions require 3 args minimum
if len(sys.argv) < 3:
    system_usage()

# default values
title_id = sys.argv[1]
title_key = sys.argv[2]
force_download = 0
make_3ds = 1
make_cia = 1
check_key = 0
no_hash = 0
no_wait = 0
check_temp_out = None
nocert = 0
first_pass = 1

# check args
for i in range(len(sys.argv)):
    if sys.argv[i] == '-redown': force_download = 1
    elif sys.argv[i] == '-no3ds': make_3ds = 0
    elif sys.argv[i] == '-nocia': make_cia = 0
    elif sys.argv[i] == '-check': check_key = 1
    elif sys.argv[i] == '-nowait': no_wait = 1
    elif sys.argv[i] == '-nohash': no_hash = no_wait = 1
    elif sys.argv[i] == '-nobuild':
        make_cia = 0
        make_3ds = 0
        no_wait = 1

if (len(title_key) != 32 and not os.path.isfile('decTitleKeys.bin')) or len(title_id) != 16:
    print('Invalid arguments')
    raise SystemExit(0)

# pull title key from decTitleKeys.bin if available
if len(title_key) != 32 and os.path.isfile('decTitleKeys.bin'):
    decrypted_keys = {}
    with open('decTitleKeys.bin', 'rb') as file_handler:
        n_entries = os.fstat(file_handler.fileno()).st_size / 32
        file_handler.seek(16, os.SEEK_SET)
        for i in range(int(n_entries)):
            file_handler.seek(8, os.SEEK_CUR)
            tmp_title_id = file_handler.read(8)
            decrypted_title_key = file_handler.read(16)
            decrypted_keys.update({(hexlify(tmp_title_id)).decode() : (hexlify(decrypted_title_key)).decode()})
    try:
        title_key = decrypted_keys[title_id]
    except:
        print('Title key not available in decTitleKeys.bin')
        raise SystemExit(0)

# set CDN default URL
base_url = 'http://ccs.cdn.c.shop.nintendowifi.net/ccs/download/' + title_id

# download tmd and set to 'tmd_var' object
try:
    tmd_var = urllib.request.urlopen(base_url + '/tmd')
except urllib.error.URLError as e:
    print('ERROR: Bad title ID?')
    raise SystemExit(0)
tmd_var = tmd_var.read()

#create folder
if check_key == 0:
    pmkdir(title_id)

# https://www.3dbrew.org/wiki/Title_metadata#Signature_Data
if bytes('\x00\x01\x00\x04', 'UTF-8') not in tmd_var[:4]:
    print('Unexpected signature type.')
    raise SystemExit(0)

# If not normal application, don't make 3ds
if title_id[:8] != '00040000':
    make_3ds = 0

# Check OS, path, and current dir to set makerom location
if 'Windows' in platform.system():
    if os.path.isfile('makerom.exe'):
        makerom_command = 'makerom.exe'
    else:
        makerom_command = which('makerom.exe')
else:
    if os.path.isfile('makerom'):
        makerom_command = './makerom'
    else:
        makerom_command = which('makerom')
if makerom_command == None:
    print('Could not find makerom!')
    raise SystemExit(0)

# Set proper common key ID
if unpack('>H', tmd_var[0x18e:0x190])[0] & 0x10 == 0x10:
    ckeyid = 1
else:
    ckeyid = 0

# Set Proper Version
title_version = unpack('>H', tmd_var[0x1dc:0x1de])[0]

# Set Save Size
save_size = (unpack('<I', tmd_var[0x19a:0x19e])[0])/1024

# If DLC Set DLC flag
dlcflag = ''
if '0004008c' in title_id:
    dlcflag = '-dlc'
content_count = unpack('>H', tmd_var[0x206:0x208])[0]

# If content count above 8 (not a normal application), don't make 3ds
if content_count > 8:
    make_3ds = 0
command_c_id = []

# Download Contents
fSize = 16384
for i in range(content_count):
    c_offs = 0xB04+(0x30*i)
    c_id = format(unpack('>I', tmd_var[c_offs:c_offs+4])[0], '08x')
    c_idx = format(unpack('>H', tmd_var[c_offs+4:c_offs+6])[0], '04x')
    c_size = format(unpack('>Q', tmd_var[c_offs+8:c_offs+16])[0], 'd')
    c_hash = tmd_var[c_offs+16:c_offs+48]
    # If content count above 8 (not a normal application), don't make 3ds
    if unpack('>H', tmd_var[c_offs+4:c_offs+6])[0] >= 8:
        make_3ds = 0
    # set output location to a folder named for title id and contentid.dec as the file
    f_out = title_id + '/' + c_id + '.dec'
    if first_pass == 1:
        if (not os.path.isfile('ctr-common-1.crt')) or (not os.path.isfile('ctr-common-1.crt')):
            print('\nCould not find certificate files, all secure connections will fail!')
            nocert = 1
        print('\nDownloading and decrypting the first 272 bytes of ' + c_id + ' for key check...\n')
        # use range requests to download bytes 0 through 271, needed 272 instead of 260 because AES-128-CBC encrypts in chunks of 128 bits
        try:
            check_req = urllib.request.Request('%s/%s'%(base_url, c_id))
            check_req.headers['Range'] = 'bytes=%s-%s' % (0, 271)
            check_temp = urllib.request.urlopen(check_req)
        except urllib.error.URLError as e:
            print('ERROR: Possibly wrong container?\n')
            raise SystemExit(0)

        print('Fetching title metadata for ' + title_id + '\n')
        try:
            ret_title_name_stripped, ret_region, ret_product_code, ret_publisher, ret_crypto_seed, ret_curr_version, ret_title_size = getTitleInfo((unhexlify(title_id)))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            print('\nCould not retrieve CDN data!\n')
            ret_region = '---'
            ret_title_name_stripped = '---Unknown---'
            ret_product_code = '------'
            ret_publisher = '------'
            ret_crypto_seed = ''
            ret_curr_version = '---'
            ret_title_size = '---'
        # set IV to offset 0xf0 length 0x10 of ciphertext; thanks to yellows8 for the offset
        check_temp_perm = check_temp.read()
        decryptor = AES.new(unhexlify(title_key), AES.MODE_CBC, check_temp_perm[0xf0:0x100])
        # check for magic ('NCCH') at offset 0x100 length 0x104 of the decrypted content
        check_temp_out = decryptor.decrypt(check_temp_perm)[0x100:0x104]
        print('Title Name: ' + ret_title_name_stripped)
        print('Region: ' + ret_region)
        print('Product Code: ' + ret_product_code)
        print('Publisher: ' + ret_publisher)
        print('Current Version: ' + ret_curr_version)
        print('Title Size: ' + ret_title_size + 'mb')
        if gen_seed == 1:
            print('')
            if ret_crypto_seed != '':
                print('9.6 Crypto Seed: ' + ret_crypto_seed)
                # Add crypto seed to crypto database
                crypto_db.add_seed(title_id, ret_crypto_seed)
                crypto_db.gen_seeddb()
                raise SystemExit(0)
            if ret_crypto_seed == '':
                print('Title ' + title_id + ' does not have a 9.6 crypto seed')
                raise SystemExit(0)

        print('')
        if 'NCCH' not in check_temp_out.decode('UTF-8', 'ignore'):
            decryptor = AES.new(unhexlify(title_key), AES.MODE_CBC, unhexlify(c_idx + '0000000000000000000000000000'))
            dsi_check_temp_out = decryptor.decrypt(check_temp_perm)[0x60:0x64]
        if 'NCCH' not in check_temp_out.decode('UTF-8', 'ignore') and 'WfA' not in dsi_check_temp_out.decode('UTF-8', 'ignore'):
            print('\nERROR: Decryption failed; invalid titlekey?')
            raise SystemExit(0)
        print('\nTitlekey successfully verified to match title ID ' + title_id + '...\n')
        if check_key == 1:
            raise SystemExit(0)

    print('Content ID:    ' + c_id)
    print('Content Index: ' + c_idx)
    print('Content Size:  ' + c_size)
    print('Content Hash:  ' + (hexlify(c_hash)).decode())

    # if the content location does not exist, redown is set, or the size is incorrect redownload
    if os.path.exists(f_out) == 0 or force_download == 1 or os.path.getsize(f_out) != unpack('>Q', tmd_var[c_offs+8:c_offs+16])[0]:
        response = urllib.request.urlopen(base_url + '/' + c_id)
        read_chunk(response, f_out, unhexlify(title_key), c_idx + '0000000000000000000000000000', report_hook=report_chunk)
    # check hash and NCCH of downloaded content
    with open(f_out,'rb') as file_handler:
        file_handler.seek(0, os.SEEK_END)
        file_handlerSize = file_handler.tell()
        if file_handler.tell() != unpack('>Q', tmd_var[c_offs+8:c_offs+16])[0]:
            print('Title size mismatch.  Download likely incomplete')
            print('Downloaded: ' + format(file_handler.tell(), 'd'))
            raise SystemExit(0)
        if no_hash == 0:
            file_handler.seek(0)
            hash = sha256()
            while file_handler.tell() != file_handlerSize:
                hash.update(file_handler.read(0x1000000))
                print('Checking Hash: ' + format(float(file_handler.tell()*100)/file_handlerSize,'.1f') + '% done\r', end=' ')
            sha256file = hash.hexdigest()
            if sha256file != (hexlify(c_hash)).decode():
                print('hash mismatched, Decryption likely failed, wrong key or file modified?')
                print('got hash: ' + sha256file)
                raise SystemExit(0)
            print('Hash verified successfully.')
        file_handler.seek(0x100)
        if (file_handler.read(4)).decode('UTF-8', 'ignore') != 'NCCH':
            make_cia = 0
            make_3ds = 0
            file_handler.seek(0x60)
            if 'WfA' not in file_handler.read(4).decode():
                print('Not NCCH, nor DSiWare, file likely corrupted')
                raise SystemExit(0)
            else:
                print('Not an NCCH container, likely DSiWare')
        file_handler.seek(0, os.SEEK_END)
        fSize += file_handler.tell()
    print('')
    command_c_id = command_c_id + ['-i', f_out + ':0x' + c_idx + ':0x' + c_id]
    first_pass = 0

if ret_crypto_seed == '' and nocert == 1 and no_wait == 0:
    print('')
    print('Could not check for 9.6 crypto seed automatically due to secure connection failure!')
    print('')
    print('If this is a 9.6+ game, then it will fail to load once installed unless the system')
    print('connects to the eShop at least once after install to update seeddb, or you place')
    print('the cert files in the current directory and rerun this script for manual decryption.')
    print('')
    input('Press Enter to continue...')

if ret_crypto_seed != '' and no_wait == 0:
    print('')
    print('This is a 9.6+ eShop game which uses seed encryption.')
    print('')
    print('The NCCH on 9.6+ eShop games is seed encrypted and cannot be used')
    print('without seed decryption on a 3DS. To fix this you should copy')
    print('all .dec files and the generated seeddb.bin in the Title ID folder')
    print('to \'/D9Game/\' on your SD card, then use the following option in Decrypt9:')
    print('')
    print('\'Game Decryptor Options\' > \'NCCH/NCSD Decryptor\'')
    print('')
    print('Once you have decrypted the files, copy the .dec files from')
    print('\'/D9Game/\' back into the Title ID folder, overwriting them.')
    print('')
    print('NOTE: The generated .3ds files will not work with Gateway')
    print('')
    input('Press Enter once you have done this...')

# create the RSF File
rom_rsf = 'Option:\n  MediaFootPadding: true\n  EnableCrypt: false\nSystemControlInfo:\n  SaveDataSize: $(SaveSize)K'
with open('rom.rsf', 'wb') as file_handler:
    file_handler.write(rom_rsf.encode())

# set makerom command with subproces, removing '' if dlcflag isn't set (otherwise makerom breaks)
dotcia_command_array = ([makerom_command, '-f', 'cia', '-rsf', 'rom.rsf', '-o', title_id + '.cia', '-ckeyid', str(ckeyid), '-major', str((title_version & 0xfc00) >> 10), '-minor', str((title_version & 0x3f0) >> 4), '-micro', str(title_version & 0xF), '-DSaveSize=' + str(save_size), str(dlcflag)] + command_c_id)
dot3ds_command_array = ([makerom_command, '-f', 'cci', '-rsf', 'rom.rsf', '-nomodtid', '-o', title_id + '.3ds', '-ckeyid', str(ckeyid), '-major', str((title_version & 0xfc00) >> 10), '-minor', str((title_version & 0x3f0) >> 4), '-micro', str(title_version & 0xF), '-DSaveSize=' + str(save_size), str(dlcflag)] + command_c_id)

if '' in dotcia_command_array:
    dotcia_command_array.remove('')
if '' in dot3ds_command_array:
    dot3ds_command_array.remove('')

if make_cia == 1:
    print('\nBuilding ' + title_id + '.cia...')
    call(dotcia_command_array, stdout=DEVNULL, stderr=STDOUT)

if make_3ds == 1:
    print('\nBuilding ' + title_id + '.3ds...')
    call(dot3ds_command_array, stdout=DEVNULL, stderr=STDOUT)

if os.path.isfile('rom.rsf'):
    os.remove('rom.rsf')

if make_cia == 1 and not os.path.isfile(title_id + '.cia'):
    print('Something went wrong.')
    raise SystemExit(0)

if make_3ds == 1 and not os.path.isfile(title_id + '.3ds'):
    print('Something went wrong.')
    raise SystemExit(0)

print('Done!')
