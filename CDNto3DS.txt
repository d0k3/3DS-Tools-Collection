Get makerom from https://github.com/Relys/Project_CTR

Usage:
	print 'Usage: CDNto3DS.py TitleID TitleKey [-redown -redec -no3ds -nocia]'
	print '-redown : redownload content'
	print '-redec  : re-attempt content decryption'
	print '-no3ds  : don\'t build 3DS file'
	print '-nocia  : don\'t build CIA file'
	
Tutorial:
 1) https://github.com/Relys/3DS_Multi_Decryptor
 2) https://gbatemp.net/threads/emunand-tool-release-and-support-thread.359239/
 3) http://mh-nexus.de/en/hxd/
 4) Use Multi Decryptor to generate fat 16 xorpad
 5) transfer over to PC
 6) Extract emunand from sd card and place it on PC
 7) Open up emunand in HxD
 8) Goto Edit-> Select Block-> Length.
 9) Set Length to 0x0B930000
 10) Press the delete key to remove the selected block (evertyhing before address 0x0B930000)
 11) Save file
 12) xor the file with the xorpad you generated. It will now be decrypted
 13) Download http://www.winimage.com/winimage.htm
 14) Open the decrypted fat 16 partition from your emunand
 15) extract and save nand/dbs/ticket.db
 16) Use https://github.com/Relys/3DS_Multi_Decryptor/blob/master/ticket-titlekey_stuff/dumpTicketKeys.py on it
 17) Transfer it over to SD card
 18) Run Multi Decryptor again and this time select Title key decryptor
 19) should generate deckeys.bin on sd card
 20) use https://github.com/Relys/3DS_Multi_Decryptor/blob/master/ticket-titlekey_stuff/printKeys.py
 21) Use https://github.com/Relys/3DS_Multi_Decryptor/tree/master/to3DS/CDNto3DS
 22) /END
