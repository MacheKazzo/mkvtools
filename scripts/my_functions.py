from os.path import isdir,isfile,basename
from os import listdir
from subprocess import run,getoutput,Popen,PIPE
from scripts.presets import preset,file_ext
import collections
import itertools
import logging
import re
import ass
from fontTools.ttLib import ttFont
from fontTools.misc import encodingTools
import json


class commands:
    def __init__(self):
        self.cmd=[""]
        self.i=0
        self.j=0
    def merge(self,comm):
        if len(self.cmd[self.i])>6500:
            self.cmd.append("")
            self.i+=1
            self.j=0
        if self.j>0:
            self.cmd[self.i]+=" && "
        self.j+=1
        self.cmd[self.i]+=comm


def searchext(track_type):
    if track_type in file_ext:
        return file_ext[track_type]
    return ""


def run_cmds(cmds):
    for cmd in cmds:
        run(cmd,shell=True)
    return 0


def get_out(mkv_path):
    with Popen(preset.mkvmerg+" -J \""+mkv_path+"\"",stdout=PIPE, stderr=PIPE) as p:
        output,errors=p.communicate()
    temp=output.decode('utf-8')
    return temp


def tracksex(temp,mkv_path,final_direc,preset,cmds=None):
    final_direc+="/tracks/"
    tracks=[]
    for t in temp["tracks"]:
        if t["type"] in preset.base_tracks:
            if t["type"]=="subtitles" and ("all" in preset.base_langs or t["properties"]["language"] in preset.base_langs):
                track_path=final_direc+"sub "+t["properties"]["language"]+"-ID"+str(t["id"])+searchext(t["properties"]["codec_id"])
            else:
                track_path=final_direc+t["type"]+"-ID"+str(t["id"])+searchext(t["properties"]["codec_id"])
            if not cmds==None:
                cmds.merge(preset.mkvextr+" \""+mkv_path+"\" tracks "+str(t["id"])+":\""+track_path+"\"")
            tracks.append({"type":t["type"],"codec":t["properties"]["codec_id"],"id":str(t["id"]),"path":track_path})
    return tracks


def attachmentsex(temp,mkv_path,final_direc,preset,cmds=None):
    final_direc+="/attachments/"
    attachments=[]
    for a in temp["attachments"]:
        attach_path=final_direc+a["file_name"]
        if not cmds==None:
            cmds.merge(preset.mkvextr+" \""+mkv_path+"\" attachments "+str(a["id"])+":\""+attach_path+"\"")
        attachments.append({"name":a["file_name"],"id":str(a["id"]),"type":a["content_type"],"path":attach_path})
    return attachments
        

def chaptersex(mkv_path,final_direc,preset,cmds=None):
    chap_path=final_direc+"/chapters.xml"
    if not cmds==None:
        cmds.merge(preset.mkvextr+" \""+mkv_path+"\" chapters \""+chap_path+"\"")
    chapters={"name":"chapters.xml","path":chap_path}
    return chapters


def search_files(direc,exts=None):
    if not isinstance(direc,(str)):
        raise Exception("direc need to be a str variable")
    if not isdir(direc):
        raise Exception(direc+" is not a valid directory")
    if exts==None:
        files=[{"name":f,"path":direc+"/"+f} for f in listdir(direc) if isfile(direc+"/"+f)]
    elif isinstance(exts,(str,tuple)):
        files=[{"name":f,"path":direc+"/"+f} for f in listdir(direc) if f.lower().endswith(exts) and isfile(direc+"/"+f)]
    elif isinstance(exts,(list)):
        files=[{"name":f,"path":direc+"/"+f} for f in listdir(direc) for e in exts if f.lower().endswith(e) and isfile(direc+"/"+f)]
    else:
        raise Exception("exts need to be a str, list, tuple variable or None. If None take all files in the directory.")
    return files

def get_files(direc,exts):
    files=[]
    for d in direc:
        if isdir(d):
            files.extend(search_files(d,exts))
        elif isfile(d) and d.lower().endswith(exts):
            files.append({"name":basename(d),"path":d})
    return files

#fontvalidator____________________________________________________________________

logging.basicConfig(format="%(name)s: %(message)s")

TAG_PATTERN = re.compile(r"\\\s*([^(\\]+)(?<!\s)\s*(?:\(\s*([^)]+)(?<!\s)\s*)?")
INT_PATTERN = re.compile(r"^[+-]?\d+")
LINE_PATTERN = re.compile(r"(?:\{(?P<tags>[^}]*)\}?)?(?P<text>[^{]*)")
TEXT_WHITESPACE_PATTERN = re.compile(r"\\[nNh]")

State = collections.namedtuple("State", ["font", "italic", "weight", "drawing"])

def parse_int(s):
    if match := INT_PATTERN.match(s):
        return int(match.group(0))
    else:
        return 0

def strip_fontname(s):
    if s.startswith('@'):
        return s[1:]
    else:
        return s

def parse_tags(s, state, line_style, styles):
    for match in TAG_PATTERN.finditer(s):
        value, paren = match.groups()

        def get_tag(name, *exclude):
            if value.startswith(name) and not any(value.startswith(ex) for ex in exclude):
                args = []
                if paren is not None:
                    args.append(paren)
                if len(stripped := value[len(name):].lstrip()) > 0:
                    args.append(stripped)
                return args
            else:
                return None


        if (args := get_tag("fn")) is not None:
            if len(args) == 0:
                font = line_style.font
            else:
                font = strip_fontname(args[0])
            state = state._replace(font=font)
        elif (args := get_tag("b", "blur", "be", "bord")) is not None:
            weight = None if len(args) == 0 else parse_int(args[0])
            if weight is None:
                transformed = None
            elif weight == 0:
                transformed = 400
            elif weight in (1, -1):
                transformed = 700
            elif 100 <= weight <= 900:
                transformed = weight
            else:
                transformed = None

            state = state._replace(weight=transformed or line_style.weight)
        elif (args := get_tag("i", "iclip")) is not None:
            slant = None if len(args) == 0 else parse_int(args[0])
            state = state._replace(italic=slant == 1 if slant in (0, 1) else line_style.italic)
        elif (args := get_tag("p", "pos", "pbo")) is not None:
            scale = 0 if len(args) == 0 else parse_int(args[0])
            state = state._replace(drawing=scale != 0)
        elif (args := get_tag("r")) is not None:
            if len(args) == 0:
                style = line_style
            else:
                if (style := styles.get(args[0])) is None:
                    print(rf"Warning: \r argument {args[0]} does not exist; defaulting to line style")
                    style = line_style
            state = state._replace(font=style.font, italic=style.italic, weight=style.weight)
        elif (args := get_tag("t")) is not None:
            if len(args) > 0:
                state = parse_tags(args[0], state, line_style, styles)

    return state

def parse_text(text):
    return TEXT_WHITESPACE_PATTERN.sub(' ', text)

def parse_line(line, line_style, styles):
    state = line_style
    for tags, text in LINE_PATTERN.findall(line):
        if len(tags) > 0:
            state = parse_tags(tags, state, line_style, styles)
        if len(text) > 0:
            yield state, parse_text(text)


class Font:
    def __init__(self, fontfile, font_number=0):
        self.fontfile = fontfile
        self.font = ttFont.TTFont(fontfile, fontNumber=font_number)
        self.num_fonts = getattr(self.font.reader, "numFonts", 1)
        self.postscript = self.font.has_key("CFF ")
        self.glyphs = self.font.getGlyphSet()

        os2 = self.font["OS/2"]
        self.weight = os2.usWeightClass
        self.italic = os2.fsSelection & 0b1 > 0
        self.slant = self.italic * 110
        self.width = 100

        self.names = [name for name in self.font["name"].names
                      if name.platformID == 3 and name.platEncID in (0, 1)]
        self.family_names = [name.string.decode('utf_16_be')
                             for name in self.names if name.nameID == 1]
        self.full_names = [name.string.decode('utf_16_be')
                           for name in self.names if name.nameID == 4]
        self.postscript_name = ''
        for name in self.font["name"].names:
            if name.nameID == 6 and (encoding := encodingTools.getEncoding(
                    name.platformID, name.platEncID, name.langID)) is not None:
                self.postscript_name = name.string.decode(encoding).strip()

                # these are the two recommended formats, prioritize them
                if (name.platformID, name.platEncID, name.langID) in \
                        [(1, 0, 0), (3, 1, 0x409)]:
                    break

        exact_names = [self.postscript_name] if (self.postscript and self.postscript_name) else self.full_names
        self.exact_names = [name for name in exact_names
                            if all(name.lower() != family.lower() for family in self.family_names)]

        mac_italic = self.font["head"].macStyle & 0b10 > 0
        if mac_italic != self.italic:
            print(f"warning: different italic values in macStyle and fsSelection for font {self.postscript_name}")

        # fail early if glyph tables can't be accessed
        self.missing_glyphs('')

    def missing_glyphs(self, text):
        if (uniTable := self.font.getBestCmap()):
            return [c for c in text
                    if ord(c) not in uniTable]
        elif (symbolTable := self.font["cmap"].getcmap(3, 0)):
            macTable = self.font["cmap"].getcmap(1, 0)
            encoding = encodingTools.getEncoding(1, 0, macTable.language) if macTable else 'mac_roman'
            missing = []
            for c in text:
                try:
                    if (c.encode(encoding)[0] + 0xf000) not in symbolTable.cmap:
                        missing.append(c)
                except UnicodeEncodeError:
                    missing.append(c)
            return missing
        else:
            print(f"warning: could not read glyphs for font {self}")

    def __repr__(self):
        return f"{self.postscript_name}(italic={self.italic}, weight={self.weight})"



class FontCollection:
    def __init__(self, fontfiles):
        self.fonts = []
        self.fonts_info=[]
        for name, f in fontfiles:
            try:
                font = Font(f)
                familyn=font.family_names
                fulln=font.full_names
                self.fonts.append(font)
                if font.num_fonts > 1:
                    for i in range(1, font.num_fonts):
                        font=Font(f, font_number=i)
                        self.fonts.append(font)
                        familyn.extend(font.family_names)
                        fulln.extend(font.full_names)
                self.fonts_info.append({"name": name,"family": familyn,"full": fulln,"path": f})
            except Exception as e:
                print(f"Error reading {name}: {e}")

        self.cache = {}
        self.by_full = {name.lower(): font
                        for font in self.fonts
                        for name in font.exact_names}
        self.by_family = {name.lower(): [font for (_, font) in fonts]
                          for name, fonts in itertools.groupby(
                              sorted([(family, font)
                                      for font in self.fonts
                                      for family in font.family_names],
                                     key=lambda x: x[0]),
                              key=lambda x: x[0])}

    def similarity(self, state, font):
        return abs(state.weight - font.weight) + abs(state.italic * 100 - font.slant)

    def _match(self, state):
        if (exact := self.by_full.get(state.font)):
            return exact, True
        elif (family := self.by_family.get(state.font)):
            return min(family, key=lambda font: self.similarity(state, font)), False
        else:
            return None, False

    def match(self, state):
        s = state._replace(font=state.font.lower(), drawing=False)
        try:
            return self.cache[s]
        except KeyError:
            font = self._match(s)
            self.cache[s] = font
            return font



def validate_fonts(doc, fonts, warn_on_exact):
    report = {
        "missing_font": collections.defaultdict(set),
        "missing_glyphs": collections.defaultdict(set),
        "missing_glyphs_lines": collections.defaultdict(set),
        "faux_bold": collections.defaultdict(set),
        "faux_italic": collections.defaultdict(set),
        "mismatch_bold": collections.defaultdict(set),
        "mismatch_italic": collections.defaultdict(set)
    }
    styles = {style.name: State(strip_fontname(style.fontname), style.italic, 700 if style.bold else 400, False)
              for style in doc.styles}
    for i, line in enumerate(doc.events):
        if isinstance(line, ass.Comment):
            continue
        nline = i + 1

        try:
            style = styles[line.style]
        except KeyError:
            print(f"Warning: Unknown style {line.style} on line {nline}; assuming default style")
            style = State("Arial", False, 400, False)
            
        for state, text in parse_line(line.text, style, styles):
            font, exact_match = fonts.match(state)
            if font is None:
                report["missing_font"][state.font].add(nline)
                continue

            if state.weight >= font.weight + 150 and warn_on_exact:
                report["faux_bold"][state.font, state.weight, font.weight].add(nline)

            if state.weight <= font.weight - 150 and not exact_match and warn_on_exact:
                report["mismatch_bold"][state.font, state.weight, font.weight].add(nline)

            if state.italic and not font.italic and warn_on_exact:
                report["faux_italic"][state.font].add(nline)

            if not state.italic and font.italic and not exact_match and warn_on_exact:
                report["mismatch_italic"][state.font].add(nline)

            if not state.drawing and warn_on_exact:
                missing = font.missing_glyphs(text)
                report["missing_glyphs"][state.font].update(missing)
                if len(missing) > 0:
                    report["missing_glyphs_lines"][state.font].add(nline)

    def format_lines(lines, limit=10):
        sorted_lines = sorted(lines)
        if len(sorted_lines) > limit:
            sorted_lines = sorted_lines[:limit]
            sorted_lines.append("[...]")
        return ' '.join(map(str, sorted_lines))
    missing_fonts=[]
    for font, lines in sorted(report["missing_font"].items(), key=lambda x: x[0]):
        missing_fonts.append(font)
        if warn_on_exact:
            print(f"- Could not find font {font} on line(s): {format_lines(lines)}")

    for (font, reqweight, realweight), lines in sorted(report["faux_bold"].items(), key=lambda x: x[0]):
        
        print(f"- Faux bold used for font {font} (requested weight {reqweight}, got {realweight}) " \
              f"on line(s): {format_lines(lines)}")

    for font, lines in sorted(report["faux_italic"].items(), key=lambda x: x[0]):
        
        print(f"- Faux italic used for font {font} on line(s): {format_lines(lines)}")

    for (font, reqweight, realweight), lines in sorted(report["mismatch_bold"].items(), key=lambda x: x[0]):
        
        print(f"- Requested weight {reqweight} but got {realweight} for font {font} " \
              f"on line(s): {format_lines(lines)}")

    for font, lines in sorted(report["mismatch_italic"].items(), key=lambda x: x[0]):
        
        print(f"- Requested non-italic but got italic for font {font} on line(s): " + \
              format_lines(lines))

    for font, lines in sorted(report["missing_glyphs_lines"].items(), key=lambda x: x[0]):
        
        missing = ' '.join(f'{g}(U+{ord(g):04X})' for g in sorted(report['missing_glyphs'][font]))
        print(f"- Font {font} is missing glyphs {missing} " \
              f"on line(s): {format_lines(lines)}")

    return missing_fonts


def font_onsubs(direc,font_list,warnings=False):
    with open(direc, 'r', encoding='utf_8_sig') as f:
        subtitles = [(basename(direc), ass.parse(f))]
    fonts = FontCollection(font_list)
    for name, doc in subtitles:
        missing_fonts=validate_fonts(doc,fonts,warnings)
    return missing_fonts
