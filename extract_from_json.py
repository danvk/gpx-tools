#!/usr/bin/env python
"""Extract location/time data from the JSON metadata in a Google Photos takeout archive."""

import json
import os
import sys
import zipfile
from glob import glob


features = []

for arg in sys.argv[1:]:
    for zip_path in glob(arg):
        archive = zipfile.ZipFile(zip_path, mode='r')
        for path in archive.namelist():
            ext = os.path.splitext(path)[1].lower()
            if ext != '.json':
                continue
            with archive.open(path, mode='r') as f:
                metadata = json.load(f)
                geo = metadata.get('geoData')
                if geo and geo['latitude'] != 0.0:
                    d = metadata.get('photoTakenTime') or metadata['date']
                    features.append({
                        'type': 'Feature',
                        'properties': {
                            # 'title': metadata['title'],
                            # 'zipfile': zip_path,
                            # 'url': metadata.get('url'),
                            'date': d['formatted'],
                            # 'timestamp': d['timestamp'],
                        },
                        'geometry': {
                            'type': 'Point',
                            'coordinates': [geo['longitude'], geo['latitude']]
                        }
                    })

print(json.dumps({
    'type': 'FeatureCollection',
    'features': features
}, indent=2))
