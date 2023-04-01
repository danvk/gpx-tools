#!/usr/bin/env python
"""Break a GPX file up into a GeoJSON FeatureCollection of its track points."""

import sys
import json

from parsing import read_gpx

(gpx_file,) = sys.argv[1:]

trkpts = read_gpx(gpx_file)

fc = {
    'type': 'FeatureCollection',
    'features': [
        {
            'type': 'Feature',
            'properties': {
                'index': i,
            },
            'geometry': {
                'type': 'Point',
                'coordinates': (pt[0], pt[1]),
            }
        }
        for i, pt in enumerate(trkpts)
    ]
}
json.dump(fc, sys.stdout, indent=2)
