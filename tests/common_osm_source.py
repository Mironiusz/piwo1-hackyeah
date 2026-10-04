"""Write small invented OpenStreetMap sources for importer tests; no real extract enters the repository."""

from pathlib import Path

import osmium

INVENTED_STATE = "2026-10-03T00:00:00Z"
INVENTED_TIMESTAMP = 'timestamp="2026-10-03T00:00:00Z" version="1"'
INVENTED_NODES_XML = (
    f'<node id="1" lon="19.9" lat="50" {INVENTED_TIMESTAMP}/><node id="2" lon="20" lat="50" {INVENTED_TIMESTAMP}/>'
    f'<node id="3" lon="20" lat="50.1" {INVENTED_TIMESTAMP}/><node id="4" lon="19.9" lat="50.1" {INVENTED_TIMESTAMP}/>'
    f'<node id="5" lon="19.92" lat="50.02" {INVENTED_TIMESTAMP}/><node id="6" lon="19.94" lat="50.02" {INVENTED_TIMESTAMP}/>'
    f'<node id="7" lon="19.96" lat="50.02" {INVENTED_TIMESTAMP}><tag k="barrier" v="kerb"/><tag k="kerb" v="lowered"/></node>'
    f'<node id="8" lon="19.95" lat="50.05" {INVENTED_TIMESTAMP}><tag k="amenity" v="bench"/></node>'
)
INVENTED_WAYS_XML = (
    f'<way id="1" {INVENTED_TIMESTAMP}><nd ref="1"/><nd ref="2"/><nd ref="3"/><nd ref="4"/><nd ref="1"/></way>'
    f'<way id="10" {INVENTED_TIMESTAMP}><nd ref="5"/><nd ref="6"/><tag k="highway" v="steps"/><tag k="step_count" v="4"/>'
    '<tag k="access" v="private"/><tag k="foot" v="yes"/></way>'
    f'<way id="11" {INVENTED_TIMESTAMP}><nd ref="6"/><nd ref="7"/><tag k="highway" v="residential"/><tag k="sidewalk" v="no"/>'
    '<tag k="surface" v="sett"/></way>'
    f'<way id="12" {INVENTED_TIMESTAMP}><nd ref="5"/><nd ref="7"/><tag k="highway" v="motorway"/></way>'
)
INVENTED_RELATIONS_XML = (
    f'<relation id="449696" {INVENTED_TIMESTAMP}><member type="way" ref="1" role="outer"/>'
    '<tag k="type" v="multipolygon"/><tag k="boundary" v="administrative"/></relation>'
)


def apply_invented_osm_source(directory: Path, elements_xml: str = INVENTED_NODES_XML + INVENTED_WAYS_XML + INVENTED_RELATIONS_XML, state: str = INVENTED_STATE) -> Path:
    """Write an invented PBF with a source-state header; nodes must precede ways and ways must precede relations."""
    xml = directory / "invented.osm"
    xml.write_text(f'<osm version="0.6">{elements_xml}</osm>', encoding="utf-8")
    header = osmium.io.Header()
    header.set("osmosis_replication_timestamp", state)
    source = directory / "invented.osm.pbf"
    with osmium.SimpleWriter(str(source), header=header) as writer:
        for element in osmium.FileProcessor(xml):
            writer.add(element)
    return source
