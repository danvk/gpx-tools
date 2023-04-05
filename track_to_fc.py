#!/usr/bin/env python
"""Break a GPX file up into a GeoJSON FeatureCollection of its track points."""

import sys
import json

from parsing import read_gpx

(gpx_file,) = sys.argv[1:]

(_, trkpts) = read_gpx(gpx_file)

fc = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'properties': {
                'index': i,
                'ele': pt.ele,
                'time': pt.time,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': (pt.lng, pt.lat),
            }
        }
        for i, pt in enumerate(trkpts)
    ]
}
json.dump(fc, sys.stdout, indent=2)
