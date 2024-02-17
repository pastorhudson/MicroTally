echo off
esptool --chip esp32s2 --port COM7 erase_flash
echo "Waiting for S2 to restart before writing MicroTally"
echo off
timeout /T 10 /NOBREAK
esptool --chip esp32s2 --port COM7 write_flash -z 0x0 MicroTally.bin