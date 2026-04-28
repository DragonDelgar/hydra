import os
import json
import sqlite3
import configparser
import pathlib
import hashlib
import time
import struct
from dataclasses import dataclass

from . import hypath
from . import hydata
from . import hysong
from . import hymisc


@dataclass
class ScanItem:
    md5: str
    title: str
    artist: str
    charter: str
    notespath: str
    rootfolder: str
    
    def __repr__(self):
        return f"ScanItem{vars(self)}"
    
    def db_values(self):
        return (self.md5, self.title, self.artist, self.charter, self.notespath, self.rootfolder)
    
    @staticmethod
    def db_cols():
        return 'md5,name,artist,charter,path,folder'
    
    @staticmethod
    def from_notes_ini_pair(f_notes, f_ini, rootfolder=None):
        with open(f_notes, 'rb') as f:
            md5 = hashlib.file_digest(f, "md5").hexdigest()
        title, artist, charter = ScanItem.get_metadata_ini(f_ini)
        return ScanItem(md5, title, artist, charter, f_notes, rootfolder)
    
    @staticmethod
    def from_sng(f_sng, rootfolder=None):
        with open(f_sng, 'rb') as f:
            md5 = hashlib.file_digest(f, "md5").hexdigest()
        title, artist, charter = ScanItem.get_metadata_sng(f_sng)
        return ScanItem(md5, title, artist, charter, f_sng, rootfolder)

    @staticmethod
    def from_db(db_row):
        return ScanItem(*db_row)

    @staticmethod
    def get_metadata_ini(f_ini):
        config = configparser.ConfigParser(
            strict=False, allow_no_value=True, interpolation=None
        )
        # utf-8 should work but try to do other encodings if it doesn't
        for codec in ['utf-8', 'utf-8-sig', 'ansi']:
            try:
                config.read(f_ini, encoding=codec)
                break
            except (configparser.MissingSectionHeaderError, UnicodeDecodeError):
                continue
       
        # Song inis have one section
        if 'Song' in config:
            metadata = config['Song']
        elif 'song' in config:
            metadata = config['song']
        else:
            raise hymisc.ChartFileError(f"Invalid ini format: {inifile}")
        
        title = metadata.get('name', "<unknown title>")
        artist = metadata.get('artist', "<unknown artist>")
        charter = metadata.get('charter', "<unknown charter>")
        
        return (title, artist, charter)
    
    @staticmethod
    def get_metadata_sng(f_sng):
        title = "<unknown title>"
        artist = "<unknown artist>"
        charter = "<unknown charter>"
        
        with open(f_sng, mode='rb') as bytes:
            METADATACOUNT_OFFSET = 34
            bytes.seek(METADATACOUNT_OFFSET, 0)
            metadata_count = struct.unpack('Q', bytes.read(8))[0]
            
            for i in range(metadata_count):
                key_len = struct.unpack('I', bytes.read(4))[0]
                key = bytes.read(key_len).decode('utf-8').casefold()
                value_len = struct.unpack('I', bytes.read(4))[0]
                value = bytes.read(value_len).decode('utf-8')
                
                match key:
                    case 'name':
                        title = value
                    case 'artist':
                        artist = value
                    case 'charter':
                        charter = value
        
        return (title, artist, charter)

def discover_charts(rootfolders, cb_progress=None):
    """Recursively searches for charts in the given root folders.
    
    Re-encountered folders will be skipped.
    
    Procedure:
    - At each folder visited, check files present.
    - Add "notes.mid" if "song.ini" is present.
    - If there was no "notes.mid", add "notes.chart" if "song.ini" is present.
    - Add all .sng files.
    
    """
    scanitems = []
    errors = []
    
    def process_folder(folder, origin_folder):
        found_mid = None
        found_chart = None
        found_ini = None
        found_sngs = []
        
        for file, fullpath in ((f, os.path.join(folder, f)) for f in os.listdir(folder)):
            if os.path.isfile(fullpath):
                if file == "notes.mid":
                    found_mid = fullpath
                elif file == "notes.chart":
                    found_chart = fullpath
                elif file == "song.ini":
                    found_ini = fullpath
                elif file.casefold().endswith(".sng"):
                    found_sngs.append(fullpath)
        
        if found_mid and found_ini:
            # Add .mid
            scanitems.append(ScanItem.from_notes_ini_pair(found_mid, found_ini, rootfolder=origin_folder))
            if cb_progress:
                cb_progress(len(scanitems))
        elif found_chart and found_ini:
            # Add .chart
            scanitems.append(ScanItem.from_notes_ini_pair(found_chart, found_ini, rootfolder=origin_folder))
            if cb_progress:
                cb_progress(len(scanitems))
        
        # Add .sng
        for f_sng in found_sngs:
            scanitems.append(ScanItem.from_sng(f_sng, rootfolder=folder))
            if cb_progress:
                cb_progress(len(scanitems))
    
    # DFS with no repeats
    unexplored = [(root, root) for root in rootfolders if os.path.isdir(root)]
    visited = set(rootfolders)
    
    while unexplored:
        dir, origin = unexplored.pop()
        
        try:
            process_folder(dir, os.path.relpath(pathlib.Path(dir).parent, origin))
                
            subpaths = [os.path.join(dir, f) for f in os.listdir(dir)]
            for subpath in (os.path.join(dir, f) for f in os.listdir(dir)):
                if os.path.isdir(subpath) and subpath not in visited:
                    visited.add(subpath)
                    unexplored.append((subpath, origin))
                
        except Exception as e:
            errors.append(e)
            continue
    
    return (scanitems, errors)
    

def analyze_chart_file(
    filepath,
    m_difficulty, m_pro, m_bass2x,
    d_mode, d_value,
    ms_filter=None,
    cb_parsecomplete=None, cb_pathsprogress=None,
    export_tempomap=False
):
    """Entry point for analyzing a chart file.
    
    Accepts .mid, .chart, and .sng.
    
    """
    if filepath.casefold().endswith(".mid"):
        load_songpath = hysong.load_songpath_mid
    elif filepath.casefold().endswith(".chart"):
        load_songpath = hysong.load_songpath_chart
    elif filepath.casefold().endswith(".sng"):
        load_songpath = hysong.load_songpath_sng
    else:
        raise hymisc.ChartFileError(f"Unexpected chart filetype: {filepath}")
    
    song = load_songpath(filepath, m_difficulty, m_pro, m_bass2x)
    
    if cb_parsecomplete:
        cb_parsecomplete()
        
    return _analyze(song, m_difficulty, m_pro, m_bass2x, d_mode, d_value, ms_filter, cb_pathsprogress, export_tempomap)


def analyze_chart_bytes_mid(
    chartbytes,
    m_difficulty, m_pro, m_bass2x,
    d_mode, d_value,
    ms_filter=None,
    cb_parsecomplete=None, cb_pathsprogress=None,
    export_tempomap=False
):
    """Entry point for analyzing a chart from the bytes of a .mid file.
    
    Use this with an SNG that has already been decoded for its .mid file.
    Otherwise, use analyze_chart_file.
    
    """
    song = hysong.load_songbytes_mid(chartbytes, m_difficulty, m_pro, m_bass2x)
    
    if cb_parsecomplete:
        cb_parsecomplete()
    
    return _analyze(song, m_difficulty, m_pro, m_bass2x, d_mode, d_value, ms_filter, cb_pathsprogress, export_tempomap)

def analyze_chart_bytes_chart(
    chartbytes,
    m_difficulty, m_pro, m_bass2x,
    d_mode, d_value,
    ms_filter=None,
    cb_parsecomplete=None, cb_pathsprogress=None,
    export_tempomap=False
):
    """Entry point for analyzing a chart from the bytes of a .chart file.
    
    Use this with an SNG that has already been decoded for its .chart file.
    Otherwise, use analyze_chart_file.
    
    """
    song = hysong.load_songbytes_chart(chartbytes, m_difficulty, m_pro, m_bass2x)
    
    if cb_parsecomplete:
        cb_parsecomplete()
    
    return _analyze(song, m_difficulty, m_pro, m_bass2x, d_mode, d_value, ms_filter, cb_pathsprogress, export_tempomap)
    
def _analyze(
    song,
    m_difficulty, m_pro, m_bass2x,
    d_mode, d_value,
    ms_filter=None,
    cb_pathsprogress=None,
    export_tempomap=False
):
    """Uses hydra to produce a pathing result for one song with the given settings.
    
    Use analyze_chart_bytes_mid, analyze_chart_bytes_chart, or analyze_chart_file
    to get the song input for this function.
    
    """
    # Use song object to make a score graph
    graph = hypath.ScoreGraph(song)
    
    # Use score graph to run the paths
    pather = hypath.GraphPather()
    pather.read(graph, d_mode, d_value, ms_filter, cb_pathsprogress)
    
    if export_tempomap:
        tempo_map = {
            'res': song.tick_resolution,
            'tpm': {t: v for t,v in song.tpm_changes.items()},
            'bpm': {t: v for t,v in song.bpm_changes.items()}
        }
        return (pather.record, tempo_map)

    return pather.record

def count_chart_chords(filepath):
    # Parse chart file and make a song object
    if filepath.endswith(".mid"):
        parser = hysong.MidiParser()
    elif filepath.endswith(".chart"):
        parser = hysong.ChartParser()
    else:
        raise hymisc.ChartFileError(f"Unexpected chart filetype: {filepath}")
    
    parser.parsefile(filepath, 'Expert', True, True)
    
    counts = {}
    for ts in parser.song._sequence:
        if ts.chord in counts:
            counts[ts.chord] += 1
        else:
            counts[ts.chord] = 1
    
    return counts