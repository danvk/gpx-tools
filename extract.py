#!/usr/bin/env python
"""Find photos with geocodes in a ZIP file and output them in a FeatureCollection."""

import json
import os
import sys
import zipfile
from glob import glob

import exifread


TAGS_OF_NOTE = [
    'GPS GPSLatitude',
    'GPS GPSLongitude',
    'EXIF DateTimeOriginal',
]

EXTS = {'.jpg', '.heic', '.jpeg'}


def extract_exif(f):
    tags = exifread.process_file(f, details=False)
    gps = exifread.utils.get_gps_coords(tags)
    out = {}
    if gps:
        out['lngLat'] = (gps[1], gps[0])
    out['date'] = str(tags.get('EXIF DateTimeOriginal'))
    return out


features = []

for arg in sys.argv[1:]:
    for zip_path in glob(arg):
        archive = zipfile.ZipFile(zip_path, mode='r')
        for path in archive.namelist():
            ext = os.path.splitext(path)[1].lower()
            if ext in EXTS:
                with archive.open(path, mode='r') as f:
                    exif = extract_exif(f)
                    if 'lngLat' in exif:
                        features.append({
                            'type': 'Feature',
                            'properties': {
                                'file': path,
                                'zipfile': zip_path,
                                'date': exif['date']
                            },
                            'geometry': {
                                'type': 'Point',
                                'coordinates': exif['lngLat']
                            }
                        })
                    else:
                        sys.stderr.write(f'Skipping {path} since it lacks lat/lng\n')

print(json.dumps({
    'type': 'FeatureCollection',
    'features': sorted(features, key=lambda f: f['properties']['date'])
}, indent=2))
