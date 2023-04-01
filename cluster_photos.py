#!/usr/bin/env python
"""Cluster bursts of photos that are close together in time and space."""

import json
import sys

from parsing import date_to_secs, secs_to_zulu

(photos_geojson,) = sys.argv[1:]
photos_fc = json.load(open(photos_geojson))

photos = [
    (date_to_secs(f['properties']['date']), *f['geometry']['coordinates'])
    for f in photos_fc['features']
]
photos.sort()

TIME_GAP = 2.5*60

# Cluster photo bursts
clusters = []
for photo in photos:
    if not clusters:
        clusters.append([photo])
        continue

    last = clusters[-1][-1]
    dt = photo[0] - last[0]
    if dt > TIME_GAP:
        clusters.append([photo])
    else:
        clusters[-1].append(photo)


def average(nums):
    total = 0
    n = 0
    for num in nums:
        n += 1
        total += num
    return total / n


# Reduce clusters to a single photo
features = []
for cluster in clusters:
    t = average(t for t, x, y in cluster)
    x = average(x for t, x, y in cluster)
    y = average(y for t, x, y in cluster)

    features.append({
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [x, y],
        },
        'properties': {
            'date': secs_to_zulu(int(t)),
            'num_photos': len(cluster),
        },
    })

json.dump({'type': 'FeatureCollection', 'features': features}, sys.stdout, indent=2)
