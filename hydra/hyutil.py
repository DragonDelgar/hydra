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

def analyze_chart(
    filepath,
    m_difficulty, m_pro, m_bass2x,
    d_mode, d_value,
    cb_parsecomplete=None, cb_pathsprogress=None
):
    """The full process to go from chart file to hydata.
    
    It's more or less a chain: Chart --> Song --> Graph --> Record.
    
    """
    # Parse chart file and make a song object
    if filepath.endswith(".mid"):
        parser = hysong.MidiParser()
    elif filepath.endswith(".chart"):
        parser = hysong.ChartParser()
    else:
        raise hymisc.ChartFileError(f"Unexpected chart filetype: {filepath}")
    
    parser.parsefile(filepath, m_difficulty, m_pro, m_bass2x)
    
    if cb_parsecomplete:
        cb_parsecomplete()
    
    # Use song object to make a score graph
    graph = hypath.ScoreGraph(parser.song)
    
    # Use score graph to run the paths
    pather = hypath.GraphPather()
    pather.read(graph, d_mode, d_value, cb_pathsprogress)

    return pather.record
