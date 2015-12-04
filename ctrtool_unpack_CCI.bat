md %1_unpacked
ctrtool --exefs=%1_unpacked/exefs.bin --romfs=%1_unpacked/romfs.bin --exheader=%1_unpacked/exheader.bin --logo=%1_unpacked/logo.bin --exefsdir=%1_unpacked/exefs --romfsdir=%1_unpacked/romfs %1
ctrtool --romfsdir=%1_unpacked/romfs %1_unpacked/romfs.bin