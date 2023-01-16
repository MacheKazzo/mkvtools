import scripts.my_functions as my
from scripts.presets import preset
from os import makedirs
from os.path import isdir,basename
from textwrap import dedent
import argparse
import sys
from json import loads

preset=preset()
cmds=my.commands()

def extract(mkv):
    sup_base=mkv["path"][:-len(mkv["name"])-1]
    final_dir=preset.base_final+"/"+basename(sup_base)+"/"+mkv["name"][:-4]
    
    try:
        temp=loads(my.get_out(mkv["path"]))
    except:
        return 0
    
    try:
        makedirs(final_dir)
    except:
        pass
    
    if isdir(final_dir):
        pass
    else:
        raise Exception ("Fail to create the final directory")
    
    if "attachments" in preset.base_elements:
        my.attachmentsex(temp,mkv["path"],final_dir,preset,cmds)
    if "tracks" in preset.base_elements:
        my.tracksex(temp,mkv["path"],final_dir,preset,cmds)
    if "chapters" in preset.base_elements:
        my.chaptersex(mkv["path"],final_dir,preset,cmds)
    return 0
        

def main():
    parser=argparse.ArgumentParser(prog='mkv_extract',formatter_class=argparse.RawTextHelpFormatter,epilog=dedent("Example:mkv_extract \"mkvs folder path 1\" \"mkvs folder path 2\" \".mkv path\"... -d \"new destination folder\" -e tracks -t subtitles audio video -l und ita eng"))
    parser.add_argument("folders",nargs='+',help="File paths to extract (folders or single mkvs)\n")
    parser.add_argument("-d","--destination",help="mkv_extract destination folder. If omitted it extracts to the default path: \"{}\"\n\n".format(preset.base_final))
    parser.add_argument("-n","--name",help="Destination folder (or path) of the extracted files within the preset path.\nIf omitted, it automatically creates a folder with the name of the one containing the mkv and the mkv itself. Useless if \"-d\" used.\n\n")
    parser.add_argument("-e","--elements",nargs='+',help="Elements to extract: [\"attachments\",\"tracks\",\"chapters\"]. If omitted extract: {}\n\n".format(preset.base_elements))
    parser.add_argument("-t","--tracks",nargs='+',help="Tracks to extract if \"tracks\" in element: [\"subtitles\",\"audio\",\"video\"]. If omitted extract: {}\n\n".format(preset.base_tracks))
    parser.add_argument("-l","--langs",nargs='+',help="Subtitles language to extract if \"subtitles\" in element: [\"und\"<-(always better to keep it),\"ita\",\"eng\",\"jap\"...]. If omitted extract {} subtitles.\n".format(preset.base_langs))
    args=parser.parse_args()
    
    direc=args.folders
    if args.destination:
        preset.base_final=args.destination
    if not args.destination:
        if args.name:
            preset.base_final=preset.base_final+"/"+args.name
    if args.elements:
        preset.base_elements=args.elements
    if args.tracks:
        preset.base_tracks=args.tracks
    if args.langs:
        preset.base_langs=args.langs

    print("File Reading...")
    files=my.get_files(direc,".mkv")
    for f in files:
        extract(f)

    print("File Extraction...")
    my.run_cmds(cmds.cmd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
