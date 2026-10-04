# OpenStreetMap evidence for the proposed sample locations

Document state: 2026-10-04, public-source check completed; imported-copy and route checks remain required

## Source and limits

The agent downloaded the public [OpenStreetMap map response](https://api.openstreetmap.org/api/0.6/map?bbox=19.989,50.065,20.001,50.072) on 2026-10-04 with a project-specific User-Agent and parsed its XML locally. It contained 9156 nodes and 1470 ways. A larger request was refused with HTTP 400; the successful request used the smaller bounding box in this link. The temporary XML remains outside the repository.

This is evidence of public source geometry and tags, not evidence that the same elements are in the Geofabrik copy loaded by the project. Element timestamps below describe edits of those elements, not a source-state instant for the whole response. The sample loader must recheck the named ways and their derived states against the current imported copy, and the final demonstration must check its actual route. No synthetic mobile geometry was used.

The response also contained [Tauron Arena Kraków, way 292867512](https://www.openstreetmap.org/way/292867512), with the address Stanisława Lema 7, and [Park Lotników Polskich, relation 61707](https://www.openstreetmap.org/relation/61707). The proposed sites are on nearby paths. Their report content is fictional, independently of the real source geometry.

OpenStreetMap data are provided by OpenStreetMap contributors under the ODbL. Attribution and licence information are available on the [OpenStreetMap copyright page](https://www.openstreetmap.org/copyright). This note records the selected evidence only; it does not claim to settle the project's deferred licence questions.

## S-1: contradictory poor-surface report

- Source: [way 926589691](https://www.openstreetmap.org/way/926589691).
- Checked tags: `highway=footway`, `surface=asphalt`, `bicycle=yes`, `lit=no`, `source:bicycle=park_rules`. The returned way has no `smoothness`, `access`, `foot` or `motorroad` tag.
- Last element edit: `2023-09-29T17:25:21Z`.
- [Node 10052984321](https://www.openstreetmap.org/node/10052984321): latitude `50.0673885`, longitude `19.9946069`.
- [Node 10052984320](https://www.openstreetmap.org/node/10052984320): latitude `50.0674376`, longitude `19.9948281`.
- Proposed report point: latitude `50.06741305`, longitude `19.9947175`, the arithmetic midpoint of those two consecutive nodes. Runtime geography checks establish its actual distance to the imported network; this calculation alone is not a distance proof.

M6 of `docs/product/specification.md` makes poor surface absent for a footway with `surface=asphalt` and no `smoothness`. The proposed sample says that poor surface exists there, which supplies the M2 contradiction if that explicit absent state is also present in the imported copy and the point is associated with this stretch. Missing or changed source data must fail validation rather than move the sample to a guessed substitute.

## S-2: separate fictional stairs report

- Source geometry: [way 360933256](https://www.openstreetmap.org/way/360933256).
- Checked tags: `highway=footway`, `surface=asphalt`, `bicycle=yes`, `lit=no`, `source:bicycle=park_rules`. There is no `smoothness`, `access`, `foot` or `motorroad` tag on the returned way.
- Last element edit: `2025-05-21T19:23:40Z`.
- [Node 4516199745](https://www.openstreetmap.org/node/4516199745): latitude `50.0679184`, longitude `19.9934156`.
- [Node 4516199744](https://www.openstreetmap.org/node/4516199744): latitude `50.0676502`, longitude `19.9934334`.
- Proposed report point: latitude `50.0677843`, longitude `19.9934245`, the arithmetic midpoint of those consecutive nodes.
- Proposed fictional step count: `3`. This is sample content, not an observation from OpenStreetMap.

The point is approximately 101 m from S-1 under a local planar estimate. The lack of `highway=steps` does not contradict a report of stairs under M2. The loader must check its association with the imported pedestrian network without treating that default as an explicit absence.

## S-3: fictional rest place near the contradiction

- Proposed point: latitude `50.06737`, longitude `19.99468`.
- Location reference: the S-1 path, [way 926589691](https://www.openstreetmap.org/way/926589691).
- This location is approximately 5.5 m from S-1 under a local planar estimate. No bench or other real rest-place observation is claimed.

The loader checks that this sample is within 50 m of the S-1 reference path. That path is the proposed corridor for showing the contradiction, not an agreed complete demo route. `stage7_demo_scenario` must use a route through the corridor or arrange a reviewed location change before the first loading. The joint acceptance check measures distance to the actual planned route, not merely to the reference path.

## S-4: separate fictional poor-surface geozone

- Source geometry: [way 28837556](https://www.openstreetmap.org/way/28837556).
- Checked tags: `highway=footway`, `surface=asphalt`, `bicycle=yes`, `lit=no`, `source:bicycle=park_rules`. There is no `smoothness`, `access`, `foot` or `motorroad` tag on the returned way.
- Last element edit: `2022-10-16T23:39:38Z`.
- [Node 3117020358](https://www.openstreetmap.org/node/3117020358): latitude `50.0681075`, longitude `19.9933379`.
- [Node 1688072264](https://www.openstreetmap.org/node/1688072264): latitude `50.0681275`, longitude `19.9939376`.
- Proposed centre: latitude `50.0681175`, longitude `19.99363775`, the arithmetic midpoint of those consecutive nodes.
- Radius: `25 m`. The claimed poor surface is fictional.

Runtime checks must show that the circle intersects the imported reference way and does not cover the S-1 reference path. The geozone is separately demonstrated through the ordinary M2 and M5 rules; the explicit source surface does not introduce a new geozone exemption.

## Required checks before claiming completion

1. The current imported copy includes the three named pedestrian ways and the required explicit poor-surface absence on the S-1 way.
2. The proposed S-1 and S-2 points have the intended unique nearest pedestrian way within 15 m; no ambiguous association is silently resolved.
3. PostGIS geography distances validate S-3's proximity and S-4's intersection and separation. Local planar estimates above are orientation only.
4. The actual demo route passes through the contradiction corridor and has S-3 within 50 m. Its states and sample presentation are checked with the running backend and frontend.
5. Loading and retry preserve user contributions, the sample mark and original fictional author confirmations.
