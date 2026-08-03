import os
import sys
import json
import configparser

import hydra.hypath as hypath
import hydra.hyutil as hyutil
import hydra.hydata as hydata

if __name__ == "__main__":
    
    outfile_name = "runfolder_output.json"
    
    os.makedirs(os.sep.join(['..','output']), exist_ok=True)
    outfile = os.sep.join(['..','output', outfile_name])
    
    book = {}
    
    charts_root = sys.argv[1]
    
    if not isinstance(charts_root, list):
        charts_root = [charts_root]
    
    charts = hyutil.discover_charts(charts_root)[0]
    
    print(f"\nFound {len(charts)} charts in '{charts_root}'.\n")
    
    records_count = 0
    for scanitem in charts:
    # for chartfile, inifile, dirname, _subfolder in charts:
        #print(f"{scanitem.notespath}")
        
        # hyhash, name, artist, charter, path, folder = hyutil.get_rowvalues(
            # chartfile, inifile, dirname, charts_root
        # )
        
        if scanitem.md5 not in book:
            book[scanitem.md5] = {
                'ref_name': scanitem.title,
                'ref_artist': scanitem.artist,
                'ref_charter': scanitem.charter,
                
                'records': {},
            }
        
        try:
            record = hyutil.analyze_chart_file(
                scanitem.notespath, 
                'Expert', True, True,
                'scores', 0,
            )
        except Exception:
            continue
        
        book[scanitem.md5]['records']['Expert Pro Drums, 2x Bass'] = record
        records_count += 1
    
    with open(outfile, mode='w', encoding='utf-8') as output_json:
        json.dump(book, output_json, default=hydata.json_save, separators=(',', ':'))
    
    print(f"\nFinished saving {records_count} records to {outfile_name}")
