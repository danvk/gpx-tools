#!/usr/bin/env python
"""Associate times from photos to a GPX track using OR Tools."""

import math
import json
import re
import sys
import itertools
import pyproj
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info

from parsing import date_to_secs, read_gpx, secs_to_zulu
from util import dist, is_ascending

(gpx_file, photos_file, start_time, end_time) = sys.argv[1:]

trkpts, pts = read_gpx(gpx_file)
photos_fc = json.load(open(photos_file))

if len(start_time) == 8 and len(end_time) == 8:
    # Add a date from the first photo
    date = photos_fc['features'][0]['properties']['date'][:10]
    assert date.startswith('20')
    date = date.replace('-', ':')
    sys.stderr.write(f'Assuming date is "{date}"\n')
    start_time = date + ' ' + start_time
    end_time = date + ' ' + end_time

start_secs = date_to_secs(start_time)
end_secs = date_to_secs(end_time)


photos = [
    (secs, *f['geometry']['coordinates'])
    for f in photos_fc['features']
    if start_secs <= (secs := date_to_secs(f['properties']['date'])) <= end_secs
]
photos.sort()

sys.stderr.write(f'Num photos: {len(photos)}\n')
sys.stderr.write(f'Num track points: {len(trkpts)}\n')

x = photos[0][1]
y = photos[0][2]
utm_crs_list = query_utm_crs_info(
    datum_name="WGS 84",
    area_of_interest=AreaOfInterest(
        west_lon_degree=x,
        south_lat_degree=y,
        east_lon_degree=x,
        north_lat_degree=y,
    ),
)
utm_crs = CRS.from_epsg(utm_crs_list[0].code)
sys.stderr.write(f'Using CRS {utm_crs}\n')

p = pyproj.Proj(utm_crs, preserve_units=True)
trk_xy = [p(*pt) for pt in trkpts]
photo_xy = [p(*pt[1:]) for pt in photos]

# Come up with tentative times for track points assuming a 1m/s pace. (2.2mph)
trk_dxy = []
d = 0
for i, xy in enumerate(trk_xy):
    if i > 0:
        d += dist(xy, trk_xy[i-1])
    trk_dxy.append((d, *xy))


# Come up with possible photo -> trkpt associations.
# The points must be within 100m of one another, and only the closest
# point within a 100m stretch of hiking is worth considering.
photo_candidates = []
for i, pxy in enumerate(photo_xy):
    candidates = []
    for j, (td, *txy), in enumerate(trk_dxy):
        d = dist(pxy, txy)
        if d > 50:
            continue
        if not candidates:
            candidates.append((j, td, d))
            continue
        last = candidates[-1]
        if td - last[1] < 100:
            if d < last[2]:
                candidates[-1] = (j, td, d)
        else:
            candidates.append((j, td, d))
    sys.stderr.write(f'Candidates for photo {i} ({len(candidates)}): {candidates}\n')
    photo_candidates.append(candidates)

nc = math.prod(len(c) for c in photo_candidates)
sys.stderr.write(f'Will consider {nc} possible mappings.\n')


def mapping_score(choices):
    # Reject (return math.inf) if the solution is infeasible.
    if not is_ascending(idx for idx, _td, _d in choices):
        return math.inf

    # TODO: reject if this implies an implausible hiking speed

    # Score is sum of distances
    score = sum(
        choice[2]
        for i, choice in enumerate(choices)
    )
    return score

best_score = math.inf
best_choices = None
num_feasible = 0
for choices in itertools.product(*photo_candidates):
    score = mapping_score(choices)
    if score == math.inf:
        continue

    num_feasible += 1
    sys.stderr.write(f'{score}: {choices}\n')
    if score < best_score:
        best_score = score
        best_choices = choices

sys.stderr.write(f'Num feasible solutions: {num_feasible}\n')
indices = [idx for idx, _td, _d in best_choices]
sys.stderr.write(f'Best choice: {best_score}\n')
sys.stderr.write(f'{best_choices}\n')
sys.stderr.write(f'{indices}\n')

# Attach photo times to track points
for i, trkpt_idx in enumerate(indices):
    trkpts[trkpt_idx] = (*trkpts[trkpt_idx], photos[i][0])


# Plug in start time, end time and photo times; interpolate remaining.
assert 0 not in indices
assert (len(trkpts) - 1) not in indices
trkpts[0] = (*trkpts[0], start_secs)
trkpts[-1] = (*trkpts[-1], end_secs)
indices = [0, *indices, len(trkpts) - 1]
sys.stderr.write(f'{indices}\n')

# Fill in the blanks with interpolation
for ai, bi in zip(indices[:-1], indices[1:]):
    sys.stderr.write(f'{ai}, {bi} {trkpts[ai]} {trkpts[bi]}\n')
    t0 = trkpts[ai][2]
    t1 = trkpts[bi][2]
    distances = [0]
    for i in range(ai, bi):
        d = dist(trkpts[i][:2], trkpts[i+1][:2])
        distances.append(distances[-1] + d)
    for i in range(ai+1, bi):
        pct = distances[i - ai] / distances[-1]
        t = t0 + (t1 - t0) * pct
        trkpts[i] = (*trkpts[i], t)

new_trkpts = []
for i, pt in enumerate(trkpts):
    pt_meta = pts[i]
    lng, lat, time = pt
    txt = f'<trkpt lon="{lng}" lat="{lat}">'
    if len(pt) > 2:
        txt += '<time>' + secs_to_zulu(time) + '</time>'
    if pt_meta.ele:
        txt += f'<ele>{pt_meta.ele}</ele>'
    txt += '</trkpt>'
    new_trkpts.append(txt)
new_trkpts_txt = '\n'.join(new_trkpts)

xml_text = open(gpx_file).read()
new_xml_text = re.sub(r'<trkseg>.*</trkseg>', f'<trkseg>\n{new_trkpts_txt}\n</trkseg>', xml_text, flags=re.S)
print(new_xml_text)
