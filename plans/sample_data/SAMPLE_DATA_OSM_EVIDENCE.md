# OpenStreetMap evidence for the sample places

Document state: 2026-10-04, rewritten for the scenario dataset; public-source and proxy-route checks completed, imported-copy and actual-route checks remain joint

## Source and limits

On 2026-10-04 the agent downloaded the public [OpenStreetMap map response](https://api.openstreetmap.org/api/0.6/map?bbox=19.985,50.062,20.012,50.076) with a project-specific User-Agent and parsed it locally. It holds 43605 nodes and 7960 ways, and its newest element was edited at 2026-10-04T06:45:43Z. The XML and the analysis script stay outside the repository.

The script classified the data with the importer's own tag rules: `resolve_is_pedestrian_network_way`, `resolve_way_facts` and `resolve_node_facts` of `service/osm_tag_rule.py`. It found 2451 network ways and kerb points of 136 lowered, 8 high and 5 unknown kerbs.

This is evidence of public geometry and tags. It does not show that the Geofabrik copy loaded by the project holds the same elements. The routes below are a proxy:

- a shortest path by planar length over consecutive node pairs of network ways;
- for the wheelchair preset, it leaves out ways whose stairs, poor surface, steep incline or narrow passage is present, and nodes with a high kerb;
- a geozone leaves out the node pairs within its radius.

The proxy is not Valhalla with the project's costing, and it does not model route snapping or the alternative logic of `route_planning`. The loader rechecks the conditions it can check against the imported copy at every loading. The actual route is a joint check with Mateusz and Rafał.

The schematic positions of `DemoSeed.ets` were not used. The content of the facts is fictional, whatever the real geometry.

OpenStreetMap data are provided by OpenStreetMap contributors under the ODbL ([copyright and licence](https://www.openstreetmap.org/copyright)).

## Route and destination

The start is [Tauron Arena Kraków, way 292867512](https://www.openstreetmap.org/way/292867512), Stanisława Lema 7, taken at its centroid 50.067638, 19.991534.

- To the default destination, [Ogród Doświadczeń im. Stanisława Lema, way 26003892](https://www.openstreetmap.org/way/26003892), taken at its centroid 50.068411, 19.996812, the shortest walking path is 477 m. It uses the steps of way 360942540 and the grass path of way 1104532501.
- The wheelchair path to the same destination is 1024 m. Neither path takes a single crossing node or kerb point, so the default route has no crossing for S-5 and does not run along al. Pokoju. Scenario 2 of `STAGE7_DEMO_SCENARIO_SHAPE.md` covers this case.
- A search of named places with an address between 400 and 1300 m from the start found the wheelchair paths that take a lowered kerb. The nearest are the shops of [M1 Kraków, way 164250193](https://www.openstreetmap.org/way/164250193), al. Pokoju 67, about 0.95 km away.
- The wheelchair path to the centroid of M1 Kraków, 50.064086, 19.999452, is 1091 m. It crosses al. Pokoju on the signal-controlled crossing at the stops Ogród Doświadczeń 01 and 02, on way 252778084 and way 943824141. Both crossing nodes carry `kerb=lowered`: [node 317034340](https://www.openstreetmap.org/node/317034340), edited 2025-05-23, and node 944018781.

On 2026-10-04 the user chose to propose M1 Kraków as the replacement destination of the scenario, and the places below are fitted to it. Rafał and Mateusz accept or change it in `stage7_demo_scenario`, and Kuber decides whether `DemoSeed.ets` follows. Whether M1 Kraków lies inside the boundary of the district Czyżyny was not established.

## Places

Distances are planar, in metres, from the sample point to the nearest segment of a network way. Element edit dates are those of the response.

| Fact | Point                    | Reference way                                                                 | Way tags read                                        | Nearest ways                       | Condition                                                                                                                                                              |
| ---- | ------------------------ | ----------------------------------------------------------------------------- | ---------------------------------------------------- | ---------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S-1  | 50.0676150, 19.9888900   | [1222443126](https://www.openstreetmap.org/way/1222443126), edited 2023-11-10 | `highway=path`, crossing of ul. Stanisława Lema      | 0.03 to it, 1.41 to way 926032109  | No kerb point within 6 m, so no contradiction; 109.8 m from the proxy route.                                                                                           |
| S-2  | 50.0663721, 19.99663575  | [926589685](https://www.openstreetmap.org/way/926589685), edited 2025-06-10   | `highway=footway`, `surface=paving_stones`, no steps | 0 to it, 16.2 to way 288017191     | On the proxy route; without this way a path of 1179 m exists, so a way around it exists.                                                                               |
| S-3  | 50.0668, 19.99536        | [28837534](https://www.openstreetmap.org/way/28837534), edited 2025-06-10     | `highway=footway`, `surface=asphalt`                 | 0.14 to it, 9.65 to way 1394016043 | 10.4 m from the proxy route, on a footway between the Tauron Arena and the park Ogród Doświadczeń; whether it is at a park entrance was not established.               |
| S-4  | 50.06645, 19.99455       | [360935725](https://www.openstreetmap.org/way/360935725), edited 2025-10-04   | `highway=footway`, `surface=paving_stones`           | 7.25 to it, 48.73 to way 28837534  | The 25 m circle covers part of this way only. The route bends to way 28837534 and is 1112 m instead of 1091 m.                                                         |
| S-5  | 50.06574634, 19.99708082 | [252778084](https://www.openstreetmap.org/way/252778084), edited 2021-08-27   | `highway=path`, crossing of al. Pokoju               | 0 to it, 4.96 to way 943824139     | 1.49 m from node 317034340, `kerb=lowered`, on the one stretch of this way between the junction nodes 8738705859 and 8738705860. The proxy route passes 0.8 m from it. |
| S-6  | 50.06763615, 19.9893127  | [306727457](https://www.openstreetmap.org/way/306727457), edited 2023-03-30   | `highway=footway`, `surface=paving_stones`           | 0 to it, 12.5 to way 1158451679    | 81.9 m from the proxy route.                                                                                                                                           |
| S-7  | 50.07595, 20.00285       | [83093546](https://www.openstreetmap.org/way/83093546), edited 2025-12-19     | `highway=path`, `surface=paving_stones`              | 7.67 to it, 16.19 to way 545136754 | 23.1 m from ul. Mieczysława Medweckiego, way 21923951; over 1 km from the proxy route.                                                                                 |
| S-8  | 50.06754, 19.98907       | [1222443122](https://www.openstreetmap.org/way/1222443122), edited 2023-11-10 | `highway=path`, `surface=paved`                      | 0.05 to it, 1.02 to way 306727452  | 95.3 m from the proxy route; hidden, so its place changes nothing.                                                                                                     |

## Scenario checks on the proxy route

| Case                                                 | Length | Result                                                                                       |
| ---------------------------------------------------- | ------ | -------------------------------------------------------------------------------------------- |
| Wheelchair path, S-4 and S-7 avoided                 | 1112 m | Takes the crossing of S-5 and the way of S-2; S-3 within 50 m; S-1, S-6 - S-8 off the route. |
| The same without the way of S-2                      | 1179 m | A way around S-2 exists; it crosses al. Pokoju elsewhere.                                    |
| The same with node 317034340 excluded, S-5 confirmed | 1123 m | The route avoids the crossing of S-5 and crosses at a nearby crossing.                       |

The proxy does not decide which route `route_planning` returns as the main route and which as the alternative around unverified barriers. PRD AC-5 settles that on the running service.
