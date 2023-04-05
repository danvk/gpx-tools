"""Utility code for parsing GPX files and dates/times."""

from typing import List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass
import xml.dom.minidom


@dataclass
class TrackPoint:
    lat: float
    lng: float
    ele: Optional[float] = None
    time: Optional[str] = None


def get_text(root):
    rc = []
    for node in root.childNodes:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)


def read_gpx(gpx_file: str) -> tuple[List[tuple[float, float]], List[TrackPoint]]:
    """Read a list of (lng, lat) pairs from a GPX file."""
    root = xml.dom.minidom.parse(open(gpx_file))
    trksegs = root.getElementsByTagName('trkseg')
    assert len(trksegs) == 1
    trkseg = trksegs[0]

    trkpts = trkseg.getElementsByTagName('trkpt')
    assert len(trkpts) > 0

    pairs = []
    pts = []
    for trkpt in trkpts:
        lat = float(trkpt.getAttribute('lat'))
        lng = float(trkpt.getAttribute('lon'))
        ele = None
        ele_el = trkpt.getElementsByTagName('ele')
        if len(ele_el) > 0:
            ele = float(get_text(ele_el[0]))
        time = None
        time_el = trkpt.getElementsByTagName('time')
        if len(time_el) > 0:
            time = get_text(time_el[0])
        pairs.append((lng, lat))
        pts.append(TrackPoint(lat=lat, lng=lng, ele=ele, time=time))

    return pairs, pts


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
