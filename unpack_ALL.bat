@echo off
for %%x in (*.3ds *.app) do call unpack_CCI.bat "%%x"
for %%x in (*.cia) do call unpack_CIA "%%x"
