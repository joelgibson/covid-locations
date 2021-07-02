import difflib
import glob
import itertools
import datetime

from common import read_casefile

casefiles = sorted(glob.glob('casefiles/*'))
retired = set()
for casefile1, casefile2 in zip(casefiles, casefiles[1:]):
    cases1, cases2 = [sorted(read_casefile(casefile)) for casefile in [casefile1, casefile2]]
    matcher = difflib.SequenceMatcher(a=cases1, b=cases2)

    date = datetime.date(*[int(x) for x in casefile2.split('/')[1].split('T')[0].split('-')])
    retirements = [
        case
        for op, i1, i2, _, _ in matcher.get_opcodes()
        for case in cases1[i1:i2]
        if op == 'delete'
        and (date - case.date).days >= 12
    ]

    if not retirements:
        print(f"# No cases retired {casefile1} {casefile2}")
    else:
        print(f"# {len(retirements)} cases retired {casefile1} {casefile2}")
        for case in retirements:
            print(case)

    print()