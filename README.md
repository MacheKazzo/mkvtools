# mkvtools
## Overview
It contains 2 python scripts, hopefully useful for those who want to quickly extract files from the mkv or analyze the fonts needed for the subs.
The font parsing part contains a modified version of the "fontvalidator.py" script by [Myaamori-Aegisub-Scripts](https://github.com/TypesettingTools/Myaamori-Aegisub-Scripts/).
These scripts use the [MKVToolNix](https://mkvtoolnix.download/) package.
The scripts should work on UNIX, Windows, Mac OS. I only have Windows 10, so please let me know if there are any problems.

### Presets
To get started go to scripts/presets.py and you will find the "preset" class. Here you can change your defaults that mkv_extract and sub_parser will use without having to rewrite them every time.
```
class preset:
    
    #MKVToolNix application paths
    mkvprop="mkvpropedit" #call mkvpropedit (only for sub_parser)
    mkvmerg="mkvmerge" #call mkvmerge
    mkvextr="mkvextract"#call mkvextract

    def __init__(self):
        self.base_final="path of desination folder" #default mkv_extract destination folder (only for mkv_extract)
        self.base_fonts=[]#base fonts folder list (only for sub_parser)
        self.base_elements=["attachments","tracks","chapters"] #elements to extract: ["attachments","tracks","chapters"] (only for mkv_extract)
        self.base_tracks=["subtitles"]#tracks to extract: ["subtitles","audio","video"] (only for mkv_extract)
        self.base_langs=["ita","und"]#subtitles language to extract: ["ita","eng","und"<-(always better to keep it),"jap"...] (only for mkv_extract)
```

## mkv_extract
mkv_extract.py extract attachments, tracks, chapters from mkv.
If tracks are selected allows you to choose between subtitles, audio and video.
If subtitle are selected allows you to choose the language of the subtitles to extract.

Through the -h argument from the terminal it is possible to view the arguments and an example of how to use it:
![alt text](https://github.com/MacheKazzo/mkvtools/main/images/mkv_extract screen 1.png?raw=true)
## sub_parser

