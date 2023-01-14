
class preset:
    
    #MKVToolNix application paths
    mkvprop="mkvpropedit" #call mkvpropedit (only for font_parser)
    mkvmerg="mkvmerge" #call mkvmerge
    mkvextr="mkvextract"#call mkvextract

    def __init__(self):
        self.base_final="path of desination folder" #default mkv_extract destination folder (only for mkv_extract)
        self.base_fonts=[]#base fonts folder list (only for font_parser)
        self.base_elements=["attachments","tracks","chapters"] #elements to extract: ["attachments","tracks","chapters"] (only for mkv_extract)
        self.base_tracks=["subtitles"]#tracks to extract: ["subtitles","audio","video"] (only for mkv_extract)
        self.base_langs=["ita","und"]#subtitles language to extract: ["ita","eng","und"<-(always better to keep it),"jap"...] (only for mkv_extract)


file_ext={#it is already complete
    #sub
    "S_HDMV/TEXTST":"",
    "S_TEXT/SSA":".ssa",
    "S_SSA":".ssa",
    "S_TEXT/ASS":".ass",
    "S_ASS":".ass",
    "S_TEXT/UTF8":".srt",
    "S_TEXT/ASCII":".srt",
    "S_HDMV/PGS":".sup",
    "S_KATE":".ogg",
    "S_TEXT/USF":".usf",
    "S_TEXT/WEBVTT":".vtt",
    "S_VOBSUB":".sub",
    #audio
    "A_FLAC":".flac",
    "A_DTS":".dts",
    "A_AC3":".ac3",
    "A_EAC3":".ac3",
    "A_AAC/MPEG2/*":".aac",
    "A_AAC/MPEG4/*":".aac",
    "A_AAC":".aac",
    "A_ALAC":".alac",
    "A_OPUS":".opus",
    "A_MPEG/L2":".mp2",
    "A_MPEG/L3":".mp3",
    "A_PCM/INT/LIT":".wav",
    "A_PCM/INT/BIG":".wav",
    "A_REAL/*":".ra",
    "A_TRUEHD":".thd",
    "A_MLP":".mlp",
    "A_TTA1":".tta",
    "A_VORBIS":".ogg",
    "A_WAVPACK4":".wv",
    #video
    "V_MPEG4/ISO/HEVC":".hevc",
    "V_MPEG4/ISO/AVC":".avc",
    "V_MPEG1":".mpg",
    "V_MPEG2":".mpg",
    "V_MS/VFW/FOURCC":".avi",
    "V_REAL/*":".rm",
    "V_THEORA":".ogg",
    "V_VP8":".ivf",
    "V_VP9":".ivf"
}
