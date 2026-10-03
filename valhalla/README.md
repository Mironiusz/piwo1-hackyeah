# Valhalla with accessibility patches

This directory builds the image of the routing engine of `plans/valhalla_routing/`: the official Valhalla 3.9.0 image with two patches to its source. Without them the walking legs of a public transport route ignore every place the request asks to avoid, and the accessibility of a stop is honoured only when the pedestrian costing is `type: wheelchair`, which also switches on the own wheelchair rules of Valhalla. Both break the rules of a walking route of M2 in `docs/product/specification.md`.

## The patches

| Patch                         | Files                                                                                               | What it changes                                                                                                                                                                                                                                                                                                                                                               |
| ----------------------------- | --------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `multimodal-exclusions.patch` | `src/loki/worker.cc`                                                                                | loki attached the excluded edges of `exclude_locations` and `exclude_polygons` only to the costing of the request, for example `multimodal`, while the walking legs are computed with the costing built from `pedestrian`. The excluded edges now go to every costing in `kCostingTypeMapping` of the request costing, which also covers `bikeshare` and `auto_pedestrian`.   |
| `stop-accessibility.patch`    | `src/thor/multimodal_transit.cc`, `src/mjolnir/convert_transit.cc`, `src/mjolnir/transitbuilder.cc` | With `transit.wheelchair=true` nobody boards, alights or transfers at a platform whose GTFS `wheelchair_boarding` is not 1; riding through it on the same vehicle stays allowed. `transitbuilder` keeps the wheelchair bit of the stop on the transit node instead of resetting it, and `convert_transit` no longer marks every stop of an inaccessible trip as inaccessible. |

The patches change the C++ code of Valhalla and follow its style, including its line comments marked `PATCH(<name>)`, so that they can be offered upstream unchanged. The no line comments rule of `docs/standards/standard_code_quality.md` applies to the code of this project, not to these diffs.

## Building the image

From the repository root:

```bash
docker build -t valhalla-patched:3.9.0-a11y valhalla/
```

The build clones the `3.9.0` tag, applies both patches and rebuilds only `valhalla_service`, `valhalla_convert_transit` and `valhalla_build_tiles`. They replace the stock binaries in the official runtime image, which also provides the `prime_server` headers the build needs; every other tool of the image stays stock. The build argument `CONCURRENCY`, 4 by default, sets the number of compile jobs.

## Building tiles with the image

- Road tiles built with the stock 3.9.0 tools work with the patched service unchanged.
- Transit tiles must be converted with the patched `valhalla_convert_transit` and built with the patched `valhalla_build_tiles`, because the patched `transitbuilder` keeps the accessibility of a stop on its transit node. Transit tiles from the stock tools lose it.

## Behaviour of the patched engine

- A public transport request with `transit.wheelchair=true` and the pedestrian costing `type: foot` honours the excluded places on its walking legs, skips inaccessible trips and never boards, alights or transfers at an inaccessible stop.
- With `transit.wheelchair=false` routes are identical to the stock engine.
- Walking routes without public transport are unchanged by the patches.

## Evidence and status

- Measured in the Valhalla spike of 2026-10-03, run outside the repository (`plans/valhalla_routing/VALHALLA_ROUTING_PRD.md`, section Risks and notes). The patches in this directory are byte for byte the ones measured there, and the Dockerfile is the one the spike built and smoke-tested, without its header comment.
- On 2026-10-03 the upstream `master` branch had the same unpatched code, so nothing could be taken from upstream instead.
- The upstream pull requests are not opened yet. Until both changes are accepted upstream, the project owns this build and re-applies and re-tests the patches on every upgrade of Valhalla.
- A build from scratch took 11 min 33 s in the spike and produced an image of 659 MB, against 638 MB of the official image.
