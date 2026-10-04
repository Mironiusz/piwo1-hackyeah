# Hosted demo deployment

Document state: 2026-10-04

## What this document covers

These are the steps for standing up the hosted demo of the MVP on the demo server, restarting it after a fix and checking it before its link goes into the submission. The steps are run by the owner of the server. The owner of the repository deletes the demo and all its data on 4 October 2026, after the results are announced. This document has no instructions for the deletion.

No address, host, login or secret of the server is written here or anywhere else in the repository (`docs/standards/standard_config.md`). What the agent may do on the server is in `CLAUDE.md`, section Target environment.

The steps were written before the deployment configuration existed. Where a step depends on the files of that configuration, the step ends with a pointer to the task that completes it.

## Before the first start

The server needs Docker Engine with the Compose plugin. The port of the public link has to be open to the internet. The server also needs outgoing HTTPS: the backend asks the public Nominatim instance for every address search (`plans_finished/address_search/ADDRESS_SEARCH_PLAN.md` D-13), and the loading step fetches the copies named in Loading the data. Both are settings of the host, made by its owner. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`: the minimum version of Docker Engine and the port.

## Getting the repository

Put on the server the version of the repository the team chose to deploy.

## Environment file

The demo reads its settings and secrets from one environment file. The file lives only on the server and is never committed. It holds every entry of the templates `.env.example` and `.env.local.example`. The meaning of each entry is in `docs/standards/standard_config.md`, section Environment entries. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`: the name of the file and how the start command reads it.

## Starting the demo

One command starts every service of the demo. It never applies a schema revision, and it never loads, replaces or deletes data. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`.

## Applying the schema revisions

The schema revisions are applied by hand, as a step of their own, with the consent given at the call (`docs/standards/standard_config.md`, section Environment entries). Run this step after the first start and after every update that brings a new revision. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`.

## Loading the data

The separate loading program loads four things: the OpenStreetMap copy together with the routing data built from it, the copy of the GTFS of ZTP Kraków together with the routing data with public transport built from it and from the same OpenStreetMap copy, the map tile archive and the sample reports. Run it by hand after the schema revisions. The start command never runs it. The step has finished when the program ends without an error and the map of Kraków shows at the public link.

The copy of the GTFS is loaded by `python -m worker.gtfs_import`, run after `python -m worker.osm_import` in the same one-off container (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-10). It needs access to the feeds of ZTP Kraków and to the timezone boundaries the routing tools download, keeps the last complete copy of the GTFS when a fresh fetch fails, and ends with an error when no routing data with public transport of the OpenStreetMap copy in use exists after it.

The map tile archive is not in the repository. Before the loading step, put the file `krakow.pmtiles` handed over by Adrian, the file itself and not a link to it, at the path of `TILE_ARCHIVE_SOURCE`, outside the directory of `TILE_ARCHIVE_DIR`, from which the server serves the archive at `/tiles/krakow.pmtiles`. The tile step, run on its own by `python -m worker.tile_archive` in the same one-off container, checks the file against its recorded SHA-256 value and copies it into `TILE_ARCHIVE_DIR` (`plans/tile_loading/TILE_LOADING_PLAN.md` D-7). It needs `IMPORT_WORKSPACE_ROOT` and the database, because it takes the exclusion of the import: while an import runs it ends with exit code 2 and writes nothing, and it is run again after the import ends. Its outcomes and the reasons of a failure, each with what a person does, are in `docs/setup/MAP_SETUP.md`, section Handing the archive to the server.

After the program ends, restart the routing service on the routing data it built. Until then every route ends with the message that a route cannot be planned right now (`plans_finished/valhalla_routing/VALHALLA_ROUTING_PLAN.md` D-3). The routing service serves the routing data with public transport when it was built from the OpenStreetMap copy in use, and the walking routing data of that copy otherwise, so a walking route always has data of the copy in use (`plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PLAN.md` D-9).

`PUBLIC_TRANSPORT_ENABLED` stays `false` on the hosted demo until a route with a tram in Kraków works there (AC-1 of `plans/public_transport_routing/PUBLIC_TRANSPORT_ROUTING_PRD.md`); only then is it set to `true`, and it goes back to `false` when the time box of O9 ends without such a route.

The step is not repeated after a restart of the demo. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`: the command of the program and the command that restarts the routing service.

## Restarting after a fix

Run the same start command again. Every report, vote, account and loaded copy stays. Run the schema revisions step again only when the fix brings a new revision. Do not run the loading step again.

## Emptying the database

Emptying the database is a separate step, run only on purpose. It destroys every report, vote and account, and the loaded copy. After it, run the schema revisions step and the loading step again. The start command never empties the database. Completed by the task `DEPLOYMENT_CONFIG` of `plans/deployment_config/`.

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
