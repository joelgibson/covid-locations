
import dataclasses
import datetime
import functools
import json
import re
from typing import List, Tuple

def extract_dates(string: str) -> List[datetime.date]:
    """Of course this is funky because we're dealing with weird data. Don't look too hard."""
    months = ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']
    monthmatch = '|'.join(months)
    dates = []
    for day, month in re.findall(r'([0-9]{1,2}).*?(' + monthmatch + ')', string.lower()):
        monthnum = months.index(month) + 1
        dates += [datetime.date(2021, monthnum, int(day))]
    
    return dates

def extract_times(string: str) -> List[Tuple[int, int]]:
    pairs = []
    for hour, minute, ampm in re.findall(r'([0-9]{1,2})(?::([0-9]{1,2}))?(am|pm)', string.lower()):
        hours = int(hour)
        if ampm == 'pm' and hours != 12:
            hours += 11
        
        minutes = 0 if not minute else int(minute)
        pairs += [(hours, minutes)]
    
    return pairs


@dataclasses.dataclass
class Case:
    Venue: str
    Address: str
    Suburb: str
    Time: str
    Date: str
    Lon: str
    Lat: str

    @functools.cached_property
    def tag(self) -> Tuple[str]:
        return tuple(sorted(set([
            *self.Venue.strip().lower().split(),
            *self.Address.strip().lower().split(),
            *self.Suburb.strip().lower().split(),
            *self.Date.strip().lower().split(),
        ])))
    
    @functools.cached_property
    def date(self):
        """Find the first date in the Date field, or some date far in the future if no valid dates were found."""
        dates = extract_dates(self.Date)
        if not dates:
            return datetime.date(2100, 1, 1)
        
        return dates[0]
    
    @functools.cached_property
    def start_time(self):
        """Find the first instant referenced here."""
        date = extract_dates(self.Date)[0]
        if self.Time == 'All day':
            return datetime.datetime(date.year, date.month, date.day, 0, 0)
        
        hours, minutes = extract_times(self.Time)[0]
        return datetime.datetime(date.year, date.month, date.day, hours, minutes)
    
    @functools.cached_property
    def end_time(self):
        """Find the last instant referenced here."""
        date = extract_dates(self.Date)[-1]
        if self.Time == 'All day':
            return datetime.datetime(date.year, date.month, date.day, 0, 0) + datetime.timedelta(days=1)
        hours, minutes = extract_times(self.Time)[-1]
        return datetime.datetime(date.year, date.month, date.day, hours, minutes)


    def __hash__(self):
        return hash(str(self))
    
    def __lt__(self, other):
        return (self.date, self.Venue, str(self)) < (other.date, other.Venue, str(other))
    
    def differences(self, other) -> int:
        return sum(1 for field in Case.__dataclass_fields__ if getattr(self, field) != getattr(other, field) )


def parse_datetime(json_filename: str) -> str:
    """
    >>> parse_datetime('covid-case-locations-20210630-200.json')
    '2021-06-30T02:00'
    """
    _, date, time = json_filename[:-5].rsplit('-', maxsplit=2)
    date = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
    time = f"{int(time[:-2]):02d}:{time[-2:]}"
    return date + 'T' + time


def read_case_json(json_file):
    with open(json_file, 'rb') as f:
        data = json.load(f)
    
    return [
        Case(**{field: entry[field] for field in Case.__dataclass_fields__})
        for entry in data['data']['monitor']
    ]


def read_casefile(casefile) -> List[Case]:
    if casefile == '-empty-':
        return []
    
    with open(casefile, 'r') as f:
        return [
            eval(line.strip(), {'Case': Case}, {}) for line in f
            if line.strip() != ''
            and not line.strip().startswith('#')
        ]