You're on your own for the keys ([but I've heard of this site that has a database of them...](http://lmgtfy.com/?q=http%3A%2F%2F3ds.nfshost.com)).

This script now pulls title metadata directly off the CDN by CLCert-A.

**Requires [makerom](https://github.com/profi200/Project_CTR/releases), [ctr-common-1.crt](https://mega.nz/#!Rp9CDZSY!iDopFefUj2oZERWYHm3BDbEKDhmD363YVX24TCkwp50) ([mirror](https://drive.google.com/open?id=0BzPfvjeuhqoDcnhNcjNMWlV6MFk)), and [ctr-common-1.key](https://mega.nz/#!ZxdD1DKK!eksGHKw4psuouBN1y_yeh2x3eIvXyK1IHHMfs-vTJvs) ([mirror](https://drive.google.com/open?id=0BzPfvjeuhqoDd01oNUw4N0RpNFk)) to be in the directory**   
___

This script is used with **decrypted** titlekeys from **decTitleKeys.bin**. If you need a tool that uses **encrypted** titlekeys and **encTitleKeys.bin** then use [@cearp's tool](https://gbatemp.net/threads/423025/) instead.

Advantage to **decrypted** titlekeys:
  - Titlekey can be checked if correct against encrypted CDN content to ensure it is correct

Advantage to **encrypted** titlekeys:
  - Game can be repaired/redownloaded from the eShop application

Until such time as the bootrom and its relevant keys (0x3D KeyX to be specific) have been obtained, you will have to choose between encrypted and decrypted titlekeys since we cannot encrypt/decrypt them from a PC yet.

To convert between them on a 3DS, use [Decrypt9WIP](https://github.com/d0k3/Decrypt9WIP).
___

Usage: PlaiCDN \<TitleID TitleKey\> \<Options\> for content options    
\-redown   : redownload content    
\-no3ds    : don't build 3DS file    
\-nocia    : don't build CIA file    
\-nobuild  : don't build 3DS or CIA    
\-nohash   : ignore hash checks    
\-nowait   : no crypt message/waiting for input    
\-check    : checks if title id matches key    

Usage: PlaiCDN \<TitleID\> for general options    
\-info     : to display detailed metadata    
\-seed     : generates game-specific seeddb file when using -info    

Usage: PlaiCDN \<Options\> for decTitleKeys.bin options    
\-deckey   : print keys from decTitleKeys.bin    
\-checkbin : checks titlekeys from decTitleKeys.bin    
\-checkall : check all titlekeys when using -checkbin    
\-fast     : skips name retrieval when using -checkbin, cannot be used with seed/seeddb    
\-seeddb   : generates a single seeddb.bin    

___

Examples (note this is not the correct key):    
+ `PlaiCDN.exe 000400000014F200 -info`
  + this would pull a ton of title metadata off the CDN for "Animal Crossing: Happy Home Designer"
+ `PlaiCDN.exe 000400000014F200 abb5c65ecaba9bcd29d1bfdf3f64c285`
  + this would create a .CIA and .3DS file for "Animal Crossing: Happy Home Designer"
+ `PlaiCDN.exe 000400000014F200 abb5c65ecaba9bcd29d1bfdf3f64c285 -check`
  + this would check if the key (abb5c65ecaba9bcd29d1bfdf3f64c285) for "Animal Crossing: Happy Home Designer" is correct (it's not)
+ `PlaiCDN.exe 000400000014F200 abb5c65ecaba9bcd29d1bfdf3f64c285 -redown -no3ds`
  + this would create a .CIA file after redownloading previously downloaded encrypted files for "Animal Crossing: Happy Home Designer"
+ `PlaiCDN.exe -checkbin`
  + this would check all game keys in `decTitleKeys.bin` to see if they match their titles, in addition to outputting metadata on them pulled from the CDN

___

If you are using the script itself instead of the compiled .exe, you will also need [Python 3](https://www.python.org/downloads/) to be installed, and [PyCrypto](https://pypi.python.org/pypi/pycrypto) to be installed.

If pycrypto gives you issues installing, try using [this](https://github.com/sfbahr/PyCrypto-Wheels).

The executable was created with the command `pyinstaller --onefile PlaiCDN.py`

This project is a replacement for [CDNto3DS](https://github.com/Relys/3DS_Multi_Decryptor/blob/master/to3DS/CDNto3DS/CDNto3DS.py) and includes expanded features and capabilities, including use on non windows platforms thanks to its reliance on PyCrypto instead of aescbc.

___

Example Output:

![screenshot](http://i.imgur.com/MuT7FX6.png)
