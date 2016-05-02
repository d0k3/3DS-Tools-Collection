@echo off
for %%x in (*.3ds *.app) do call ctrtool_unpack_CCI.bat "%%x"
for %%x in (*.cia) do call ctrtool_unpack_CIA "%%x"
pause
