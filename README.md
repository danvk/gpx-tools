# gpx-tools

Collection of scripts I've made to collect and clean data for my [hiking blog].

A few use cases:

- Figure out where I've been based on EXIF data in my photos on Google Photos,
  e.g. to discover forgotten hikes I'd done in years past.
- Use timestamps on photos to add times to GPX files that lack them.

## Quickstart

    python3 -m venv venv
    pip install requirements.txt
    ./extract.py path/to/your/photo-archive.zip

## Scripts

### Extracting location data from photos

Extract all locations and times from photos in a collection of zip archives:

    ./extract.py path/to/your/photo-archives*.zip > photos.geojson

For me, these ZIP files came either from selecting photos in Google Photos and
downloading them, or from using Google Takeout to download _all_ my photos.

If you have many years of photos, this might produce an unwieldy GeoJSON file.
To filter mine down to just the Catskills, I used [mapshaper]:

    mapshaper all-photos.geojson -join catskills.geojson calc='n = count()' -filter 'n>0' -o catskills-photos.geojson

If you want to turn a collection of photos into a GPX track (for uploading to
[gpx.studio], say), you can use `fc_to_track.py`:

    ./fc_to_track.py photos.geojson > track.gpx

### Adding times to photos

Sometimes you have a GPX file for a hike but it lacks time data. This can happen if you
start with a track from [eBird] (which only records the shape of the track) or if you
use [gpx.studio] to trace out known hiking trails.

But you typically do have time data for at least some points on your hike from photos.
The trick is to associate those photos with track points from the GPX file.

Assuming you start with `photos.geojson` and `track.gpx` and know the start/end times
for the entire hike:

    # Step 1: cluster "bursts" of photos
    ./cluster_photos.py photos.geojson > photos.clustered.geojson

    # Step 2: Associate those photos with track points, interpolating remaining times.
    ./add_times_from_photos.py track.gpx photos.clustered.geojson '2022:07:16 11:38:00' '2022:07:16 18:50:00' > track+times.gpx

If you want to attach elevation data to the track, [gpsvisualizer] has a helpful tool.

[hiking blog]: https://www.danvk.org/catskills/
[mapshaper]: https://mapshaper.org/
[ebird]: https://ebird.org/
[gpx.studio]: https://gpx.studio/
[gpsvisualizer]: https://www.gpsvisualizer.com/elevation
