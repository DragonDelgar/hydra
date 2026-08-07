import os
import sys
import json
import configparser

import hydra.hypath as hypath
import hydra.hyutil as hyutil
import hydra.hydata as hydata


def _generate_test(record, scanitem, i):
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
                'scores', 10,
            )
        except Exception:
            continue
        
        book[scanitem.md5]['records']['Expert Pro Drums, 2x Bass'] = record
        
        #_generate_test(record, scanitem, records_count)
        
        records_count += 1
    
    with open(outfile, mode='w', encoding='utf-8') as output_json:
        json.dump(book, output_json, default=hydata.json_save, separators=(',', ':'))
    
    print(f"\nFinished saving {records_count} records to {outfile_name}")
