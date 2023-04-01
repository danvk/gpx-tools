#!/usr/bin/env python3
"""Convert "Zulu" times in a stream to local times."""

import re
import fileinput
from datetime import datetime, timezone


PAT = re.compile(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ')
ISO_FMT = '%Y-%m-%dT%H:%M:%SZ'

def unzulu_line(line: str) -> str:
    m = PAT.search(line)
    if not m:
        return line
    dt_str = m.group(0)
    dt = datetime.strptime(dt_str, ISO_FMT).replace(tzinfo=timezone.utc)
    local = dt.astimezone()
    local_str = local.ctime()
    return line.replace(dt_str, local_str)


if __name__ == '__main__':
    for line in fileinput.input():
        print(unzulu_line(line), end='')
