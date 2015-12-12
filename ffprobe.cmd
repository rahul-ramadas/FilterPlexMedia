@echo off

ffprobe.exe -v quiet -print_format json -show_format -show_streams %*
