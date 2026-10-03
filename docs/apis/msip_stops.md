# MSIP bus and tram stop API

Document state: 2026-10-03

## Purpose and verification scope

This document describes the public upstream stop service for the planned MSIP import. It records live read-only checks performed on 2026-10-03, not an implemented backend endpoint. No project integration or database writes were performed.

The [official dataset 1490 catalogue](https://msip.krakow.pl/dataset/1490) describes bus and tram stop locations. Its online-data link points to the bus layer of the ArcGIS REST service below. Both stop layers were verified through that service. WFS and WMS endpoints were not tested; this document does not claim they provide the same contract.

## Service and layers

Base URL:

```text
https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer
```

| Layer | Source name | Mode | Observed records |
| ----- | ----------- | ---- | ---------------- |
| 0 | Przystanki autobusowe | Bus | 3170 |
| 1 | Przystanki tramwajowe | Tram | 352 |

Use `/{layer}?f=pjson` for metadata and `/{layer}/query` for data. Public reads succeeded without credentials. Other layers in the service are outside the agreed stop-import scope.

Both layers contain point geometry, advertise pagination and have a maximum response size of 2000 records. Counts above cover the complete upstream layers, before any Kraków administrative-boundary filtering.

## Fields and data quality

Both layers expose the same fields in their metadata:

| Field | Source type | Meaning |
| ----- | ----------- | ------- |
| `objectid` | OID | Layer object identifier |
| `stop_id` | String | Stop identifier |
| `stop_name` | String | Stop name |
| `stop_lat` | Double | Latitude attribute |
| `stop_lon` | Double | Longitude attribute |
| `shape` | Geometry | Point geometry |
| `aktualnosc` | Date | Source freshness field |
| `linie` | String | Lines, when provided |

JSON query results contain attributes and a separate `geometry` object. The `shape` metadata field is not a separate scalar attribute in the tested responses. Mode is determined by the source layer; neither layer has a bus/tram mode field.

Across the complete tested layers, `objectid` and `stop_id` were unique within each layer. This observation does not establish identifier stability across future refreshes or uniqueness across different layers. Preserve layer provenance rather than assuming a cross-layer identifier contract.

No tested record lacked an identifier, name, latitude, longitude or source freshness value. The `linie` field was null for 1587 of 3170 bus records and 18 of 352 tram records. Non-null examples were comma-separated strings such as `207, 317` and `22, 7, 8`; do not assume every record supplies lines or interpret null as no service.

Neither layer exposes bench, shelter or accessibility fields. These endpoints therefore cannot supply the requested equipment information. Missing equipment data remains unknown, never false or a confirmation of accessibility.

All tested records had `aktualnosc=1791005450000`, corresponding numerically to `2026-10-03T05:30:50Z` when interpreted as Unix milliseconds. Layer metadata has `dateFieldsTimeReference=null`. The source's intended freshness semantics and time reference were not established; do not equate this value with a stop edit time or the application's successful-import timestamp.

## Coordinates and geographic scope

The native source reference is EPSG:2178. Request `outSR=4326` explicitly to obtain WGS84 geometry. In ArcGIS JSON, `geometry.x` is longitude and `geometry.y` is latitude. The tested GeoJSON response used `[longitude, latitude]` coordinates.

Every point in the fully retrieved layers had finite, valid WGS84 coordinates. Projected geometry agreed with `stop_lon` and `stop_lat` to within `7.1e-10` degrees in this sample. This does not validate real-world stop positioning.

The bus layer spans longitude 19.58379 to 20.35261 and latitude 49.90249 to 50.24532. It must not be assumed to represent only Kraków. The agreed import requires filtering against the administrative polygon of Kraków, not its bounding rectangle. No polygon filter was executed in these checks, and the number of stops inside the city has not been established.

## Request examples

Use the bus layer below; replace `/0/` with `/1/` for tram stops. Commands require network access and `curl`. Each request has a 30-second client timeout.

Count all source records:

```bash
curl --fail --silent --show-error --max-time 30 --get \
  'https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0/query' \
  --data-urlencode 'where=1=1' \
  --data-urlencode 'returnCountOnly=true' \
  --data-urlencode 'f=json'
```

Retrieve the first page in WGS84:

```bash
curl --fail --silent --show-error --max-time 30 --get \
  'https://msip.um.krakow.pl/arcgis/rest/services/Obserwatorium/K04_KOMUNIKACJA/MapServer/0/query' \
  --data-urlencode 'where=1=1' \
  --data-urlencode 'outFields=*' \
  --data-urlencode 'outSR=4326' \
  --data-urlencode 'orderByFields=objectid' \
  --data-urlencode 'resultOffset=0' \
  --data-urlencode 'resultRecordCount=2000' \
  --data-urlencode 'f=json'
```

For the next page, use `resultOffset=2000` with the same filter, ordering and page size. A small GeoJSON query with `f=geojson`, `outSR=4326` and `resultRecordCount=2` was also tested successfully on the tram layer.

## Pagination and completeness

The tested bus retrieval returned 2000 features on the first page with `exceededTransferLimit=true`, then 1170 at offset 2000 without that property. Their union contained 3170 distinct object IDs, matching the count query. The tram query returned 352 distinct records, matching its count query, without a transfer-limit flag.

A two-record bus page returned object IDs 2 and 3; offset 2 returned 4 and 5. Object IDs are not contiguous from zero and must not be used as offsets.

Use explicit ordering and inspect `exceededTransferLimit`. According to the [Esri layer query reference](https://developers.arcgis.com/rest/services-reference/enterprise/query-map-service-layer/), false or an absent flag means paging is complete; page length alone is insufficient to decide completeness. Advance the offset by the requested page size, including when a spatially filtered page contains fewer rows than requested.

Before reconciling removals, validate all pages and identifiers and check completeness. Offset pages and a separate count query do not guarantee a consistent snapshot if the upstream source changes during retrieval. Cross-refresh stability and concurrent-update behavior were not tested. An incomplete or failed download must not replace the previous stored dataset.

## Empty results and errors

Both layers returned a valid JSON response with `features=[]` for `where=1=0`.

An invalid bus query with `where=nonexistent_field=1` returned HTTP 200 with this body:

```json
{
  "error": {
    "code": 400,
    "message": "Failed to execute query.",
    "details": []
  }
}
```

HTTP success alone is therefore insufficient. Inspect the parsed body for an ArcGIS `error` before treating it as a feature response. `curl --fail` in the examples catches HTTP errors but does not catch this application error. Do not interpret an error, invalid JSON, missing features or a timeout as an empty dataset.

## Live check results

| Check | Result |
| ----- | ------ |
| Service and both layer metadata | Read successfully without credentials |
| Bus count and complete retrieval | 3170, matching two pages |
| Tram count and complete retrieval | 352, matching one page |
| Bus offset pagination | Distinct successive pages |
| WGS84 geometry | Valid coordinates for all retrieved stops |
| Tram GeoJSON sample | Two Point features |
| Empty filter on both layers | Valid empty feature lists |
| Invalid query | HTTP 200 with ArcGIS error code 400 |
| Equipment fields | Not available in either tested layer |

Responses were parsed as JSON and checked locally for counts, duplicate identifiers, null attributes and coordinate validity. These checks demonstrate current read behavior, not uptime, correctness of transport information, licensing, rate limits or identifier stability. Load tests, retries, city-polygon filtering and scheduled imports were not executed.

## Reuse terms and project boundary

The [MSIP catalogue](https://msip.krakow.pl/dataset/1490) refers reuse to the MSIP regulations. Anonymous read access is not evidence of permission to redistribute. The applicable terms and required attribution still need verification before integration.

The agreed application behavior is a separate local stop dataset with public database-only reads, daily refresh at 03:00 Europe/Warsaw, a prompt initial import, and retries after failures. Import dates remain internal. This document does not implement those behaviors or define a project endpoint.
