"""
Generate "casefiles" (a sorted file with one case per line) from the raw JSON data.
"""

import pathlib
import glob
from common import read_case_json, parse_datetime

for src_name in glob.glob('json/*.json'):
    dst_name = pathlib.Path('casefiles', parse_datetime(src_name))
    if dst_name.exists():
        continue

    cases = sorted(read_case_json(src_name))
    with open(dst_name, 'w') as f:
        for case in cases:
            print(repr(case), file=f)
    
    print(f"Wrote {dst_name} from source data {src_name}")
