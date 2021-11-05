On Windows:
via WSL clone https://github.com/Filosoft/vabamorf Provided any difficulties, look up the issues.
1) go to dct/sh and compile the dictionaries with ./nullist-uus-sonastik.sh
2) then move dictionaries (et.dct, et3.dct) to apps/cmdline/project/unix
3) clone the text corpora to the folder. you can move it directly from Windows by command explorer.exe . (or from File explorer, just type \\wsl$)
4) tag the corpora with commands prepared in print('./etana analyze -in ../../../../' + fnameIn
              + ' -out ../../../../' + fnameIn[:-5] + '-analyzed.json')