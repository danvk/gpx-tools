#!/usr/bin/env python3
"""Convert a FeatureCollection (of photos, say) to a GPX track."""

import fileinput
import json
from xml.sax.saxutils import escape
from datetime import datetime, timezone


def zuluize_date(date: str) -> str:
    naive = datetime.strptime(date, "%Y:%m:%d %H:%M:%S")
    local = naive.astimezone()
    utc = local.astimezone(timezone.utc)
    return utc.strftime('%Y-%m-%dT%H:%M:%SZ')


def main():
    contents = '\n'.join(fileinput.input())
    infile = fileinput.filename()

    fc = json.loads(contents)
    points = [
        (f['properties']['date'], *f['geometry']['coordinates'])
        for f in fc['features']
    ]
    points.sort()
    by_date = {}
    for point in points:
        date = point[0][:10].replace(':', '-')
        by_date.setdefault(date, [])
        by_date[date].append(point)

    for date, points in by_date.items():
        with open(f'{date}.gpx', 'w') as out:
            out.write(
    f'''<?xml version="1.0"?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.1" creator="AllTrails.com" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
<metadata>
</metadata>
<trk>
    <name>{escape(infile)} - {date}</name>
    <src>Photos</src>
    <trkseg>
    ''')
            for (t, lng, lat) in points:
                out.write(f'''     <trkpt lat="{lat}" lon="{lng}">
                <time>{zuluize_date(t)}</time>
            </trkpt>
                ''')
            out.write('''</trkseg>
        </trk>
        </gpx>
                ''')

if __name__ == '__main__':
    main()
