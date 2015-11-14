@echo off
set NAME="REINAND CFW"
set LONG_DESC="ReiNAND CFW via Brahma2"
set AUTHOR="Reisyukaku"
set ICON="icon.png"
set OUTPUT="reinand.smdh"
smdhtool --create %NAME% %LONG_DESC% %AUTHOR% %ICON% %OUTPUT%