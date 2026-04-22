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
    notespath: str
    rootfolder: str
    title: str
    artist: str
    charter: str
    
    def __repr__(self):
        return f"ScanItem{vars(self)}"
    
    def from_mid_ini(f_mid, f_ini):
        
    
    def from_chart_ini(f_chart, f_ini):
        
    
    def from_sng(f_sng):
        with open(f_sng, mode='rb') as bytes:
            
            item = ScanItem(f_sng, None, None, None, None)
            
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
                        item.title = value
                    case 'artist':
                        item.artist = value
                    case 'charter':
                        item.charter = value
           
            return item
    
def discover_charts_new(rootfolders, cb_progress=None):
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
    
    def process_folder(folder):
        print(f"Processing {folder}...")
        
        found_mid = None
        found_chart = None
        found_ini = None
        found_sngs = []
        fullpaths = (os.path.join(folder, f) for f in os.listdir(folder))
        for file in (os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(f)):
            # gather up files by type
            if file == "notes.mid":
                found_mid = os.path.join(folder, f)
            elif file == "notes.chart":
                found_chart = os.path.join(folder, f)
            elif file == "song.ini":
                found_ini = os.path.join(folder, f)
            elif file.casefold().endswith(".sng"):
                found_sngs.append(os.path.join(folder, f))
        
        if found_mid and found_ini:
            # Add .mid
            print(f".mid found: {found_mid}/{found_ini}")
            mid_item = ScanItem.from_mid_ini(found_mid, found_ini)
            mid_item.rootfolder = folder
            scanitems.append(mid_item)
            if cb_progress:
                cb_progress(len(scanitems))
        elif found_chart and found_ini:
            # Add .chart
            print(f".chart found: {found_chart}/{found_ini}")
            chart_item = ScanItem.from_chart_ini(found_chart, found_ini)
            chart_item.rootfolder = folder
            scanitems.append(chart_item)
            if cb_progress:
                cb_progress(len(scanitems))
        
        # Add .sng
        for f_sng in found_sngs:
            print(f"SNG found: {f_sng}")
            sng_item = ScanItem.from_sng(f_sng)
            sng_item.rootfolder = folder
            scanitems.append(sng_item)
            if cb_progress:
                cb_progress(len(scanitems))
    
    # DFS
    unexplored = [(root, root) for root in rootfolders if os.path.isdir(root)]
    visited = set(rootfolders)
    
    while unexplored:
        dir, origin = unexplored.pop()
        
        #try:
        process_folder(dir)
            
        subpaths = [os.path.join(dir, f) for f in os.listdir(dir)]
        for subpath in (os.path.join(dir, f) for f in os.listdir(dir)):
            if os.path.isdir(subpath) and subpath not in visited:
                visited.add(subpath)
                unexplored.append((subpath, origin))
            
        # except Exception as e:
            # errors.append(e)
            # continue
    
    return (scanitems, errors)
    
def discover_charts(rootfolders, cb_progress=None):
    """Returns a list of tuples (chartfile, inifile, chartfolder, subfolders)
    and a list of encountered errors.
    
    Recursively searches for charts in the given root folders.
    """
    try:
        # (current search path, original root folder)
        unexplored = [(root, root) for root in rootfolders]
    except FileNotFoundError as e:
        return ([], [e])
    
    # Fill out chart files found in a given folder, not necessarily in order
    found_by_dirname = {}
    errors = []
    visited = set()
    while unexplored:
        f, origin = unexplored.pop()
        
        if os.path.isfile(f):
            dir, base = os.path.split(f)
            
            if base in ["notes.mid", "notes.chart"]:
                i = 0
            elif base == "song.ini":
                i = 1
            else:
                continue
                
            if dir not in found_by_dirname:
                found_by_dirname[dir] = [
                    None, None,
                    dir, os.path.relpath(pathlib.Path(dir).parent, origin)
                ]
            found_by_dirname[dir][i] = f
        
            if cb_progress:
                cb_progress(len(found_by_dirname))
        else:
            # Handle a folder - add subfolders to the search
            try:
                subnames = os.listdir(f)
            except Exception as e:
                errors.append(e)
                continue
                
            for subname in subnames:
                subpath = os.sep.join([f, subname])
                if subpath not in visited:
                    visited.add(subpath)
                    unexplored.append((subpath, origin))
    
    return (
        [tuple(info) for info in found_by_dirname.values() if all(info)],
        errors
    )


def get_folder_chart(folder):
    """Non-recursive lookup for a chart file in the given folder."""
    for f in os.listdir(folder):
        filepath = os.path.join(folder, f)
        if os.path.isfile(filepath):
            if f in ["notes.mid", "notes.chart"]:
                return filepath
    return None

def get_rowvalues(chartfile, inifile, path, subfolders):
    config = configparser.ConfigParser(
        strict=False, allow_no_value=True, interpolation=None
    )
    # utf-8 should work but try to do other encodings if it doesn't
    for codec in ['utf-8', 'utf-8-sig', 'ansi']:
        try:
            config.read(inifile, encoding=codec)
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
    
    # Hash the chart file
    with open(chartfile, 'rb') as f:
        hyhash = hashlib.file_digest(f, "md5").hexdigest()
    
    # Grab our desired metadata
    try:
        name = metadata['name']
    except KeyError:
        name = "<unknown name>"
        
    try:
        artist = metadata['artist']
    except KeyError:
        artist = "<unknown artist>"
        
    try:
        charter = metadata['charter']
    except KeyError:
        charter = "<unknown charter>"

    return (hyhash, name, artist, charter, path, subfolders)

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