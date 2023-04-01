"""Utility code for parsing GPX files and dates/times."""

import re
from typing import List
from datetime import datetime, timezone


def read_gpx(gpx_file: str) -> List[tuple[float, float]]:
    """Read a list of (lng, lat) pairs from a GPX file."""
    xml_text = open(gpx_file).read()
    m = re.search(r'<trkseg>(.*)</trkseg>', xml_text, flags=re.S)
    assert m
    trkpts_txt = m.group(1)
    trkpts1 = [
        (float(m.group(1)), float(m.group(2)))
        for m in re.finditer(r'<trkpt lon="([-0-9.]+)" lat="([-0-9.]+)">', trkpts_txt)
    ]
    trkpts2 = [
        (float(m.group(2)), float(m.group(1)))
        for m in re.finditer(r'<trkpt lat="([-0-9.]+)" lon="([-0-9.]+)">', trkpts_txt)
    ]
    trkpts = trkpts1 + trkpts2
    return trkpts


def secs_to_zulu(secs: int) -> str:
    utc = datetime.fromtimestamp(secs, tz=timezone.utc)
    return utc.strftime('%Y-%m-%dT%H:%M:%SZ')


def date_to_secs(date: str) -> int:
    """Convert a local EXIF or ISO 8601 date to a unix timestamp."""
    if date.endswith('Z'):
        utc = datetime.strptime(date[:-1] + '+0000', '%Y-%m-%dT%H:%M:%S%z')
        return utc.timestamp()
    naive = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
    local = naive.astimezone()
    utc = local.astimezone(timezone.utc)
    return utc.timestamp()
