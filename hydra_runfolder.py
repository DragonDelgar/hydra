import os
import sys
import json
import csv

import hydra.hypath as hypath
import hydra.hyutil as hyutil
import hydra.hydata as hydata


def _generate_test(record, scanitem, i):
    """
        Analyzes each input chart and uses the resulting pathlist to create
        a test where the expected result is that pathlist.
    
        To do: Some sort of sys.argv setup for this?
    """
    print(f"    def test_{i}(self): # {scanitem.artist} - {scanitem.title}")
    print(f"        self._test_pathlist(\"{scanitem.notespath.replace('\\', '\\\\')}\", 10, {{")
    scoretiers = {}
    for p in record.all_paths():
        if p.totalscore() not in scoretiers:
            scoretiers[p.totalscore()] = []
        scoretiers[p.totalscore()].append(p.pathstring())
        
    for k in scoretiers.keys():
        print(f"                {k} : [\"{"\", \"".join(scoretiers[k])}\"],")
    print("            })\n")
    

def book_from_folder(rootfolder, score_depth):
    if not isinstance(rootfolder, list):
        rootfolder = [rootfolder]
    
    book = {}
    print(f"\nDiscovering charts...")
    scanitems, errors = hyutil.discover_charts(rootfolder)
    print(f"\nFound {len(scanitems)} charts in '{rootfolder}'.\n")
    if errors:
        print("Error(s) occurred:")
        for error in errors:
            print(f"\t{error}")
        print("\n", end='')
    
    miscinfo = {}
    
    print(f"Analyzing charts...", end='')
    for scanitem in scanitems:
        if scanitem.md5 not in book:
            print(".", end='', flush=True)
            try:
                record, tempomap = hyutil.analyze_chart_file(
                    scanitem.notespath, 
                    'Expert', True, True,
                    'scores', score_depth,
                    export_tempomap=True,
                )
            
                book[scanitem.md5] = {
                    'ref_name': scanitem.title,
                    'ref_artist': scanitem.artist,
                    'ref_charter': scanitem.charter,
                    
                    'tempomap': tempomap,
                    
                    'records': {'Expert Pro Drums, 2x Bass': record},
                }
                
                tierstr = "???"
                for folder in reversed(scanitem.notespath.split(os.sep)[:-1]):
                    if folder.startswith('Tier'):
                        tierstr = folder
                        break
                        
                miscinfo[scanitem.md5] = {
                    'tier': tierstr,
                }
            except Exception as e:
                print(f"\nAn error occurred while trying to process {scanitem.notespath}: {e}")
    print("\nDone.")
    
    return book, miscinfo

def output_csv(book, filename_csv):
    print("\nOutputting csv...")
    with open(filename_csv, 'w', newline='', encoding="utf-8") as file_csv:
        csvwriter = csv.writer(file_csv)
        csvwriter.writerow(["Title", "Artist", "Charter", "md5", "Index", "Score", "Path", "Avg. Mult", "Ghost kicks", "Accent kicks"])
        for md5 in book.keys():
            record = book[md5]['records']['Expert Pro Drums, 2x Bass']
            for i,path in enumerate(record.all_paths()):
                csvwriter.writerow([
                    book[md5]['ref_name'],
                    book[md5]['ref_artist'],
                    book[md5]['ref_charter'],
                    md5,
                    i,
                    path.totalscore(),
                    path.pathstring_verbose(),
                    path.avg_mult(),
                    record.songfeatures['Ghost kicks'] if 'Ghost kicks' in record.songfeatures else 0,
                    record.songfeatures['Accent kicks'] if 'Accent kicks' in record.songfeatures else 0,
                ])
    print(f"Done. ({filename_csv})")


def output_csv_tourney(book, miscinfo, filename_csv):
    print("\nOutputting csv...")
    with open(filename_csv, 'w', newline='', encoding="utf-8") as file_csv:
        csvwriter = csv.writer(file_csv)
        csvwriter.writerow(["Tier", "Title", "Artist", "Path Label", "Score", "Mult Squeezes", "Activations"])
        for md5 in reversed(book.keys()):
            record = book[md5]['records']['Expert Pro Drums, 2x Bass']
            optimal_score = record.best_path().totalscore()
            for i,path in enumerate(record.all_paths()):
                p_score = path.totalscore()
                pstr = path.pathstring_verbose().split('|')
                csvwriter.writerow([
                    miscinfo[md5]['tier'],
                    book[md5]['ref_name'],
                    book[md5]['ref_artist'],
                    "Optimal" if p_score == optimal_score else "Alternate",
                    path.totalscore(),
                    "None." if pstr[0].startswith('(') else pstr[0].strip(),
                    "None." if pstr[1].startswith(' (') else pstr[1].strip(),
                ])
    print(f"Done. ({filename_csv})")


if __name__ == "__main__":
    # Output files
    filename = "runfolder_output"
    os.makedirs(os.sep.join(['..','output']), exist_ok=True)
    filename_json = os.sep.join(['..','output', filename+'.json'])
    filename_csv = os.sep.join(['..','output', filename+'.csv'])
    
    try:
        rootfolder = sys.argv[1]
    except:
        print(f"Missing first argument: root chart folder.")
        
    try:
        score_depth = int(sys.argv[2])
    except:
        score_depth = 4
        
    book, miscinfo = book_from_folder(rootfolder, score_depth)
    
    print("\nOutputting json...")
    with open(filename_json, mode='w', encoding='utf-8') as file_json:
        json.dump(book, file_json, default=hydata.json_save, separators=(',', ':'))
    print(f"Done. ({filename_json})")
    
    output_csv(book, filename_csv)
