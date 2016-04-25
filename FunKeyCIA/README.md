# FunKeyCIA
Python tool for downloading content from CDN, uses only a title id and title key, or keyfile, to make a good cia.



## Example uses:


* Download a single game, with the title id and encrypted titlekey.

`FunKeyCIA.py -title XXXXXXXXXXXXXXXX -key ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ`


* Download a game, using the encTitleKeys.bin file in the same folder as FunKeyCIA.py.
Only the title id is needed, because the encTitleKeys.bin contains the keys.

`FunKeyCIA.py -keyfile -title XXXXXXXXXXXXXXXX`


* Download a game, using the latest encTitleKeys.bin file from 3ds.nfshost.com.
The will save the key file to the same folder as FunKeyCIA.py, overwriting any file with the same name.
Only the title id is needed because the encTitleKeys.bin contains the keys.

`FunKeyCIA.py -nfskeyfile -title XXXXXXXXXXXXXXXX`

* Give multiple title ids. Only works when using keyfiles, not when you give the key yourself.
When using keyfiles, you can download multiple things, this will get the latest keyfile from 3ds.nfshost.com and download 3 games:

`FunKeyCIA.py -nfskey -title XXXXXXXXXXXXXXXX XXXXXXXXXXXXXXXX XXXXXXXXXXXXXXXX`


* Generate tickets only
We can generate tickets only, and not download and create a CIA. Tickets will be put in the 'tickets' folder.

`FunKeyCIA.py -ticketsonly -title XXXXXXXXXXXXXXXX -key ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ`

`FunKeyCIA.py -ticketsonly -nfskeyfile XXXXXXXXXXXXXXXX`


* Generate ALL* tickets in the keyfile.
We can generate all the tickets that a keyfile has by telling it, without specifying all the title ids.
*When using '-all', system titles and game updates will be ignored.

`FunKeyCIA.py -ticketsonly -nfskeyfile -all`

