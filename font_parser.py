import scripts.my_functions as my
from tempfile import TemporaryDirectory
from scripts.presets import preset
from os.path import basename,isdir,isfile
from os import listdir
from textwrap import dedent
from subprocess import run
import argparse
import sys

preset=preset()
preset.tracks=["subtitles"]


def sub_main(direc,tmp_dir,fontfolder_list,is_mkv=False,not_remove=False):
    sub_direc=direc
    if is_mkv:
        temp=my.get_temp(direc)
        cmds=my.commands()
        attachments=my.attachmentsex(temp,direc,tmp_dir,preset,cmds)
        tracks=my.tracksex(temp,direc,tmp_dir,preset,cmds)
        sub_direc=tracks[0]["path"]
        my.run_cmds(cmds.cmd)
        
        #missing fonts
        attach_list=[]
        for a in attachments:
            attach_list.append([a["name"],a["path"]])
        missing_fonts=my.font_onsubs(sub_direc,attach_list,False)
        if not missing_fonts:
            print("No missing fonts.")
        else:
            print("Missing fonts:")
            print(missing_fonts)
        
    #sub used fonts
    fontsub_list=my.font_onsubs(sub_direc,[],False)
    if not is_mkv:
        print("Sub used fonts:")
        print(fontsub_list)
        missing_fonts=fontsub_list
        
    if is_mkv and not not_remove:
        #deleting unused and duplicate fonts
        fontmkv_rawlist=my.FontCollection(attach_list).fonts_info
        fontmkv_list=[]
        removefont_list=[]
        existing_dicts=set()
        #duplicates
        for f in fontmkv_rawlist:
            font=tuple(f['full'])
            if (font) not in existing_dicts:
                existing_dicts.add((font))
                fontmkv_list.append(f)
            else:
                removefont_list.append(f)
        #unused
        for font in fontmkv_list:
            if not any(f in fontsub_list for f in font["family"]):
                removefont_list.append(font)
        #deleting
        if removefont_list:
            print("\nDeleting mkv unused fonts:")
            removefont_names=[f["name"] for f in removefont_list]
            print(removefont_names)
            for a in reversed(attachments):
                if a['name'] in removefont_names:
                    run(preset.mkvprop+" \""+direc+"\" --delete-attachment "+a["id"],shell=True)
              
    #searching and adding missing fonts found
    addfont_name=[]
    addfont_path=[]
    mime_list=[]
    for font in fontfolder_list:
        if any(f in missing_fonts for f in font["family"]):
            if font["name"].lower().endswith((".ttf",".ttc")):
                addfont_name.append(font["name"])
                addfont_path.append(font["path"])
                mime_list.append("\" --attachment-mime-type application/x-truetype-font --add-attachment \"")
            elif font["name"].lower().endswith(".otf"):
                addfont_name.append(font["name"])
                addfont_path.append(font["path"])
                mime_list.append("\" --attachment-mime-type application/vnd.ms-opentype --add-attachment \"")
    check_list=[]
    if missing_fonts and addfont_name:
        print("\nMissing fonts found:")
        print(addfont_name)
        check_list=[[n,p] for [n,p] in zip(addfont_name,addfont_path)]
        
    if is_mkv:
        if missing_fonts and addfont_name:
            print("\nAdding missing fonts found:")
            for font["path"],mime in zip(addfont_path,mime_list):
                run(preset.mkvprop+" \""+direc+mime+font["path"]+"\"",shell=True)
    
        #final check
        print("\nFinal check:")
        cmds=my.commands()
        temp=my.get_temp(direc)
        attachments=my.attachmentsex(temp,direc,tmp_dir,preset,cmds)
        my.run_cmds(cmds.cmd)
        check_list=[[a["name"],a["path"]] for a in attachments]
    print("\nWarnings:")
    my.font_onsubs(sub_direc,check_list,True)

    return 0


def main():
    parser=argparse.ArgumentParser(prog='font_parser',formatter_class=argparse.RawTextHelpFormatter,epilog=dedent("Example:font_parser \"Folder path 1\" \".ass path\" \".mkv path\"... -f \"font folder path 1\" \".ttf path\"... -l und ita eng"))
    parser.add_argument("files",nargs='+',help="File paths to parsing (folders or single mkv,ass,ssa)\n")
    parser.add_argument("-f","--fonts",nargs='+',help="Font folders or single ttc,ttf,otf\n\n")
    parser.add_argument("-nbf",action='store_false',help="Not use preset font paths: {}\n\n".format(preset.base_fonts))
    parser.add_argument("-n",action='store_true',help="Not remove unused or duplicate fonts.\n\n")
    parser.add_argument("-l","--langs",nargs='+',help="Subtitles language to extract if \"subtitles\" in element: [\"und\"<-(always better to keep it),\"ita\",\"eng\",\"jap\"...]. If omitted extract {} subtitles.\n".format(preset.base_langs))
    args=parser.parse_args()
    direc=args.files
    fontpath_list=[]
    if args.nbf:
        fontpath_list.extend(preset.base_fonts)
    if args.fonts:
        fontpath_list.extend(args.fonts)
    if args.langs:
        preset.base_langs=args.langs
   
    files=my.get_files(direc,(".mkv",".ass",".saa"))

    #fonts in fontpath_list (folders)
    fonts=my.get_files(fontpath_list,(".ttf",".ttc",".otf"))
    fontfolder_rawlist=my.FontCollection([(f["name"],f["path"]) for f in fonts]).fonts_info
    existing_dicts=set()
    fontfolder_list=[]
    for f in fontfolder_rawlist:
        font=tuple(f['full'])
        if (font) not in existing_dicts:
            existing_dicts.add((font))
            fontfolder_list.append(f)
    
    for f in files:
        print("\nAnalyzing: "+f["name"])
        if f["path"].lower().endswith(".mkv"):
            with TemporaryDirectory() as tmp_dir:
                sub_main(f["path"],tmp_dir,fontfolder_list,is_mkv=True,not_remove=args.n)
        else:
            sub_main(f["path"],"",fontfolder_list,not_remove=args.n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
