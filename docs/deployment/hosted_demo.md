# Hosted demo deployment

Document state: 2026-10-04

## What this document covers

These are the steps for standing up the hosted demo of the MVP on the demo server, restarting it after a fix and checking it before its link goes into the submission. The steps are run by the owner of the server. The owner of the repository deletes the demo and all its data on 4 October 2026, after the results are announced. This document has no instructions for the deletion.

No address, host, login or secret of the server is written here or anywhere else in the repository (`docs/standards/standard_config.md`). What the agent may do on the server is in `CLAUDE.md`, section Target environment.

The configuration is the Compose project `enableme` of `deploy/compose.yaml`, written by `plans/deployment_config/`. Every command below runs from the repository root.

## Before the first start

The server needs Docker Engine 27 or newer with the Compose plugin 2.29 or newer. The port of the public link, the value of `DEMO_HTTP_PORT` in the environment file, has to be open to the internet; only the proxy publishes a port. The server also needs outgoing HTTPS: the backend asks the public Nominatim instance for every address search (`plans_finished/address_search/ADDRESS_SEARCH_PLAN.md` D-13), and the loading step fetches the copies named in Loading the data. Both are settings of the host, made by its owner.

If the database of the demo was started earlier on its own with `db/compose.deploy.yaml`, stop it first; the project `enableme` keeps its data in volumes of its own and does not take that database over:

```bash
docker compose --env-file .env.demo -f db/compose.deploy.yaml down
```

## Getting the repository

Put on the server the version of the repository the team chose to deploy.

## Environment file

The demo reads its settings and secrets from one environment file. The file lives only on the server and is never committed. It is `.env.demo` in the repository root, which git ignores, and holds every entry of the templates `.env.example` and `.env.local.example`. The meaning of each entry is in `docs/standards/standard_config.md`, section Environment entries. Every command reads it with `--env-file .env.demo`, and the backend and the one-off loading container read it as their environment.

The configuration sets twelve entries itself, because they are paths and addresses inside its containers, so their values in `.env.demo` are not read and may stay empty: `APP_ENVIRONMENT`, `API_BIND_HOST`, `API_PORT`, `DB_HOST`, `DB_PORT`, `ROUTING_SERVICE_URL`, `ROUTING_DATA_DIR`, `VALHALLA_TOOL_DIR`, `VALHALLA_CONFIG_TEMPLATE`, `IMPORT_WORKSPACE_ROOT`, `TILE_ARCHIVE_DIR` and `TILE_ARCHIVE_SOURCE`. `DB_HOST_PORT` is used only on a developer machine. `API_TRUSTED_PROXY_ADDRESSES` stays empty until the step after the first start.

## Starting the demo

One command starts every service of the demo: the proxy, the backend, the routing service and the database. It never applies a schema revision, and it never loads, replaces or deletes data. The image of the routing service is built first, because the backend image is built on it; the first build compiles Valhalla and takes about 12 minutes.

```bash
docker compose --env-file .env.demo -f deploy/compose.yaml build routing
docker compose --env-file .env.demo -f deploy/compose.yaml up -d --build --wait proxy backend routing database
```

Until data is loaded the routing service writes that it waits for `/data/current`, and every route ends with the message that a route cannot be planned right now.

After the first start, let the backend trust the proxy for the address of a person (`plans/community_facts_api/COMMUNITY_FACTS_API_PLAN.md` D-16). Read the subnet of the network of the proxy, write it into `API_TRUSTED_PROXY_ADDRESSES` in `.env.demo`, and start the backend again:

```bash
docker network inspect enableme_edge --format '{{(index .IPAM.Config 0).Subnet}}'
docker compose --env-file .env.demo -f deploy/compose.yaml up -d --wait backend
```

Until then every vote without an account counts as coming from one person. The value never enters the repository.

## Applying the schema revisions

The schema revisions are applied by hand, as a step of their own, with the consent given at the call (`docs/standards/standard_config.md`, section Environment entries). Run this step after the first start and after every update that brings a new revision:

```bash
docker compose --env-file .env.demo -f deploy/compose.yaml --profile migrate run --rm -e DB_REVISION_CONSENT=apply migrate
```

## Loading the data

The separate loading program loads four things: the OpenStreetMap copy together with the routing data built from it, the copy of the GTFS of ZTP Kraków together with the routing data with public transport built from it and from the same OpenStreetMap copy, the map tile archive and the sample reports. Run it by hand after the schema revisions. The start command never runs it. The step has finished when the program ends without an error and the map of Kraków shows at the public link.

The copy of the GTFS is loaded by `python -m worker.gtfs_import`, run after `python -m worker.osm_import` in the same one-off container (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-10). It needs access to the feeds of ZTP Kraków and to the timezone boundaries the routing tools download, keeps the last complete copy of the GTFS when a fresh fetch fails, and ends with an error when no routing data with public transport of the OpenStreetMap copy in use exists after it.

The map tile archive is not in the repository. Before the loading step, put the file `krakow.pmtiles` handed over by Adrian, the file itself and not a link to it, anywhere on the server outside the volumes of the demo. The tile step below binds that file at the call as `TILE_ARCHIVE_SOURCE` of its container, and writes into `TILE_ARCHIVE_DIR`, the volume `enableme_tile_archive`, from which the proxy serves the archive at `/tiles/krakow.pmtiles`. The tile step, run on its own by `python -m worker.tile_archive` in the same one-off container, checks the file against its recorded SHA-256 value and copies it into `TILE_ARCHIVE_DIR` (`plans_finished/tile_loading/TILE_LOADING_PLAN.md` D-7). It needs `IMPORT_WORKSPACE_ROOT` and the database, because it takes the exclusion of the import: while an import runs it ends with exit code 2 and writes nothing, and it is run again after the import ends. Its outcomes and the reasons of a failure, each with what a person does, are in `docs/setup/MAP_SETUP.md`, section Handing the archive to the server.

After the program ends, restart the routing service on the routing data it built. Until then every route ends with the message that a route cannot be planned right now (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-3). The routing service serves the routing data with public transport when it was built from the OpenStreetMap copy in use, and the walking routing data of that copy otherwise, so a walking route always has data of the copy in use (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-9).

`PUBLIC_TRANSPORT_ENABLED` stays `false` on the hosted demo until a route with a tram in Kraków works there (AC-1 of `plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PRD.md`); only then is it set to `true`, and it goes back to `false` when the time box of O9 ends without such a route.

Each part runs in the one-off container `loader`, in this order, the tile step with the file bound at the call:

```bash
docker compose --env-file .env.demo -f deploy/compose.yaml --profile load run --rm loader python -m worker.osm_import
docker compose --env-file .env.demo -f deploy/compose.yaml --profile load run --rm loader python -m worker.gtfs_import
docker compose --env-file .env.demo -f deploy/compose.yaml --profile load run --rm -v <path of krakow.pmtiles on the server>:/srv/tile_source/krakow.pmtiles:ro loader python -m worker.tile_archive
docker compose --env-file .env.demo -f deploy/compose.yaml restart routing
```

The step is not repeated after a restart of the demo.

## Restarting after a fix

Run the same start commands again, `build routing` and `up`. Every report, vote, account and loaded copy stays. Run the schema revisions step again only when the fix brings a new revision. Do not run the loading step again.

## Emptying the database

Emptying the database is a separate step, run only on purpose. It destroys every report, vote and account, and the loaded copy. After it, run the schema revisions step and the loading step again. The start command never empties the database. It also removes the import workspace, which belongs to one database; the routing data and the tile archive stay:

```bash
docker compose --env-file .env.demo -f deploy/compose.yaml down
docker volume rm enableme_database_data enableme_import_workspace
```

`down` also removes the networks of the demo, and the next start may give the network of the proxy another subnet. After the next start, repeat the step that writes `API_TRUSTED_PROXY_ADDRESSES` (section Starting the demo); without it the backend no longer trusts the proxy, and every vote without an account counts as coming from one person.

## Check before the link goes into the submission

Before 10:00 on 4 October 2026, check on a phone:

1. The public link opens.
2. The map of Kraków shows.
3. A walking route is planned between two addresses.
4. One address search returns a list of places.

If the address search shows the message that the search is unavailable, the public address search refuses requests from the server. The start and the destination can still be picked on the map. The team decides before 10:00 what the submission says about it.

## Known limits of the hosted demo

- The page is served over plain HTTP, without a certificate, so the browser marks it as not secure.
- The browser does not give the page the current location, so the start of a route is picked from an address or the map.
- Passwords and session tokens travel between the browser and the server unencrypted.
- Routing is not taken down during the live demo.
