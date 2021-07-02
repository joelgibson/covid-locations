import sys
from common import read_casefile
import json
import dataclasses

cases = set.union(*[
    set(read_casefile(arg)) for arg in sys.argv[1:]
])

print(json.dumps([
    {**dataclasses.asdict(case), 'startTime': case.start_time, 'endTime': case.end_time}
    for case in sorted(cases, key=lambda case: (case.Venue, case.start_time))
], default=lambda x: str(x).replace(' ', 'T'), indent=1))
