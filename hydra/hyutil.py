import os
import json
import sqlite3
import configparser
import pathlib
import hashlib
import time

from . import hypath
from . import hydata
from . import hysong
from . import hymisc

    
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