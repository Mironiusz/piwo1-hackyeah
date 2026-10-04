# Valhalla with accessibility patches

This directory builds the image of the routing engine of `plans_finished/valhalla_routing/`: the official Valhalla 3.9.0 image with two patches to its source. Without them the walking legs of a public transport route ignore every place the request asks to avoid, and the accessibility of a stop is honoured only when the pedestrian costing is `type: wheelchair`, which also switches on the own wheelchair rules of Valhalla. Both break the rules of a walking route of M2 in `docs/product/specification.md`.

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

## Publishing the image

`.github/workflows/valhalla-image.yml` builds this directory on a GitHub-hosted runner with `CONCURRENCY=4` and publishes the image to the GitHub container registry, so a server pulls the image instead of building it. The workflow runs only when a person starts it: it has no other trigger, and nothing deploys or pulls the image on its own. The workflow file has no comments, by the no line comments rule, so its decisions are described here.

### Running the workflow

On GitHub open Actions, choose `Valhalla image` and press Run workflow, or start it with the GitHub CLI:

```bash
gh workflow run valhalla-image.yml -f patch_rev=1
```

GitHub offers a manually started workflow only once its file is on the default branch, `main`. A run builds `valhalla/` of the branch it is started on, chosen in Use workflow from or with `--ref <branch>`, and that branch needs the workflow file too.

The two inputs:

- `patch_rev`, 1 by default, is the revision of the patch set. A person raises it whenever a `.patch` file or the `Dockerfile` changes. The tag also carries the version of Valhalla, so a new version can start again at 1.
- `overwrite` is off by default. Without it, the run stops before building when the version tag already exists in the registry, so a tag that a server pinned never changes under it. With it, the run replaces that tag.

Runs never overlap: a run started while another is in progress waits for it, so two runs cannot both find a tag free and publish it twice. A run pushes with the token GitHub gives every run, `GITHUB_TOKEN`, allowed to write packages, so publishing needs no personal token.

### What a run publishes

The image is `ghcr.io/<owner>/valhalla-a11y`, where `<owner>` is the owner of this repository on GitHub in lower case. It gets two tags:

- `<version>-a11y.<patch_rev>`, for example `3.9.0-a11y.1`, is the tag a server pins.
- `sha-<commit>`, with the full hash of the commit the run built, traces an image back to its source.

There is no `latest` tag, so a server always names an exact tag. The summary of a run shows the full name to pull. The version is read from the `--branch` of the `git clone` in the `Dockerfile`, and the run fails unless it finds exactly one version there. An upgrade of Valhalla changes it there together with both `FROM` lines and the description label. The image is built for `linux/amd64`, the platform of the runner.

After the push, the run checks on the pushed image that `valhalla_service`, `valhalla_build_tiles` and `valhalla_convert_transit` each print that version for `--version`.

The spike built the image from scratch in 11 min 33 s with 4 compile jobs, and a standard GitHub-hosted runner of a public repository has 4 cores, so a run from scratch should take roughly 15 to 25 minutes with the push and the smoke test; no run has been timed on GitHub yet. Buildx keeps its layers in the GitHub Actions cache, so a run whose patches and build steps have not changed since a cached run reuses the compiled binaries. A run is stopped after 120 minutes.

### When to run it

Only after a change of a `.patch` file or of the `Dockerfile`, an upgrade of Valhalla included. Refreshing the OpenStreetMap or GTFS data and rebuilding the tiles use the tools of the image a server already has and need no new image.

### Pulling the image on a server

A person pulls the exact tag on the server:

```bash
docker pull ghcr.io/<owner>/valhalla-a11y:3.9.0-a11y.1
```

A public package is pulled without logging in. For a private package, a person logs in once on the server with a personal access token (classic) that has the `read:packages` scope, typed at the password prompt so that it stays out of the shell history:

```bash
docker login ghcr.io -u <github-user>
```

The token stays on that server and never enters the repository. Whether the package is public or private is set on its page on GitHub, under Package settings. Nothing pulls or switches the image on its own: a server uses a new tag only after a person pulls it and points the routing service at it.

## Starting the service

The image starts the routing service by itself: its command is `python3 /opt/enableme/start_routing_service.py /data`, so a container needs only the volume of the routing data mounted read-only at `/data` and the port 8002 (D-6 and D-10 of `plans_finished/backend_architecture/BACKEND_ARCHITECTURE_PLAN.md`).

`start_routing_service.py` runs with the Python 3.12 of the image and takes the directory of the routing data as its one argument, so it reads no environment entry. It waits until `current` exists in that directory, reading it again every 5 seconds and starting nothing meanwhile, and stops with a non-zero code when `current` does not name a copy or the copy has no `valhalla_tiles.tar`. Otherwise it takes the defaults that `valhalla_build_config` prints, merges `valhalla_overrides.json`, sets `mjolnir.tile_extract` to the absolute path of `copies/<name>/valhalla_tiles.tar`, writes the result to `/opt/enableme/valhalla_service.json` and replaces itself with `valhalla_service` with that file and one thread. The path stays fixed for the life of the container, so `tileset_last_modified` of `GET /status` names the copy the service loaded; a new copy is served after the container restarts.

`valhalla_overrides.json` holds only the keys the project sets. The `mjolnir` keys act only when the tiles are built, and the import sets the same three keys itself in `build_osm_valhalla_config` of `service/osm_routing_preparation.py`, so a change of one of them is made in both places (`plans_finished/route_planning/ROUTE_PLANNING_REVIEW.md`, the run of D-20):

| Key                                            | Value   | Why                                                                                            |
| ---------------------------------------------- | ------- | ---------------------------------------------------------------------------------------------- |
| `service_limits.max_exclude_locations`         | 5000    | A walking route excludes every avoided barrier of its corridor; the default is 50.             |
| `service_limits.max_exclude_polygons_length`   | 1000000 | The geozones of a corridor travel as polygons; the default is 10000.                           |
| `service_limits.max_exclude_polygons_vertices` | 50000   | Each geozone is a polygon of 32 vertices; the default is 100.                                  |
| `mjolnir.include_platforms`                    | `true`  | Platforms stay in the walking network.                                                         |
| `mjolnir.keep_osm_node_ids`                    | `true`  | A traced edge names its OpenStreetMap nodes, which tie the route to the stretches of the copy. |
| `mjolnir.keep_all_osm_node_ids`                | `true`  | Every node keeps its identity, not only the ones Valhalla would keep by itself.                |

The script names the directory and the tile archive in its own lines and never a request; the output of `valhalla_service` is left as it is. The names `current`, `copies` and `valhalla_tiles.tar` repeat those of `data/routing_data.py`, because the image holds no other code of the repository.

## Building tiles with the image

- Road tiles built with the stock 3.9.0 tools work with the patched service unchanged.
- Transit tiles must be converted with the patched `valhalla_convert_transit` and built with the patched `valhalla_build_tiles`, because the patched `transitbuilder` keeps the accessibility of a stop on its transit node. Transit tiles from the stock tools lose it.

## Behaviour of the patched engine

- A public transport request with `transit.wheelchair=true` and the pedestrian costing `type: foot` honours the excluded places on its walking legs, skips inaccessible trips and never boards, alights or transfers at an inaccessible stop.
- With `transit.wheelchair=false` routes are identical to the stock engine.
- Walking routes without public transport are unchanged by the patches.

## Evidence and status

- Measured in the Valhalla spike of 2026-10-03, run outside the repository (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PRD.md`, section Risks and notes). The patches in this directory are byte for byte the ones measured there, and the Dockerfile is the one the spike built and smoke-tested, without its header comment.
- On 2026-10-03 the upstream `master` branch had the same unpatched code, so nothing could be taken from upstream instead.
- The upstream pull requests are not opened yet. Until both changes are accepted upstream, the project owns this build and re-applies and re-tests the patches on every upgrade of Valhalla.
- A build from scratch took 11 min 33 s in the spike and produced an image of 659 MB, against 638 MB of the official image.
