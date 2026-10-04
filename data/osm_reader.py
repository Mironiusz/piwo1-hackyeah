"""Read owned source snapshots without keeping pyosmium callback objects alive."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import MappingProxyType
from typing import Literal

import osmium

from common_time import Deadline, DeadlineExpiredError, fetch_monotonic_seconds, resolve_remaining_milliseconds


class OsmReadError(ValueError):
    """Describe a source file whose required elements cannot be read completely."""


@dataclass(frozen=True)
class OsmElementSnapshot:
    """Own an element's identity, metadata and geometry independently of the input iterator."""

    element_type: Literal["node", "way", "relation"]
    element_id: int
    edited_at: datetime
    tags: Mapping[str, str]
    node_ids: tuple[int, ...] = ()
    coordinates: tuple[tuple[float, float], ...] = ()
    members: tuple[tuple[str, int, str], ...] = ()
    area_wkb: bytes | None = None


@dataclass
class OsmInvalidAreaTally:
    """Count the areas one read skipped because native assembly left them without an outer ring."""

    count: int = 0


def fetch_osm_header_timestamp(path: Path) -> str:
    """Read the source header value for subsequent rules-layer validation."""
    try:
        with osmium.io.Reader(str(path)) as reader:
            return reader.header().get("osmosis_replication_timestamp")
    except (RuntimeError, OSError) as error:
        raise OsmReadError("Cannot read source header") from error


def fetch_osm_elements(path: Path, deadline: Deadline, invalid_areas: OsmInvalidAreaTally | None = None) -> Iterator[OsmElementSnapshot]:
    """
    Stream copied nodes, ways, relations and assembled areas from the complete source, refusing to continue past the deadline.

    An area that native assembly left without an outer ring, from a broken multipolygon or a broken closed way of the
    source, has no geometry to copy, so it is skipped and counted in the given tally; its way or relation is still
    streamed. Every other failure to read or to build a geometry stops the read.
    """
    factory = osmium.geom.WKBFactory()
    try:
        processor = osmium.FileProcessor(path).with_locations().with_areas()
        for element in processor:
            resolve_remaining_milliseconds(deadline, fetch_monotonic_seconds())
            if not isinstance(element, (osmium.osm.Node, osmium.osm.Way, osmium.osm.Relation, osmium.osm.Area)):
                raise OsmReadError("Unexpected source entity type")
            edited_at = element.timestamp
            if edited_at.utcoffset() is None or edited_at == datetime(1970, 1, 1, tzinfo=UTC):
                raise OsmReadError("Missing or unusable element edit timestamp")
            tags = MappingProxyType(dict(element.tags))
            if isinstance(element, osmium.osm.Node):
                if not element.location.valid():
                    raise OsmReadError("Missing node location")
                yield OsmElementSnapshot("node", element.id, edited_at, tags, coordinates=((element.lon, element.lat),))
            elif isinstance(element, osmium.osm.Way):
                if any(not node.location.valid() for node in element.nodes):
                    raise OsmReadError("Missing referenced node location")
                yield OsmElementSnapshot("way", element.id, edited_at, tags, tuple(node.ref for node in element.nodes), tuple((node.lon, node.lat) for node in element.nodes))
            elif isinstance(element, osmium.osm.Relation):
                yield OsmElementSnapshot("relation", element.id, edited_at, tags, members=tuple((member.type, member.ref, member.role) for member in element.members))
            elif isinstance(element, osmium.osm.Area):
                if element.num_rings()[0] == 0:
                    if invalid_areas is not None:
                        invalid_areas.count += 1
                    continue
                element_type: Literal["node", "way", "relation"] = "way" if element.from_way() else "relation"
                yield OsmElementSnapshot(element_type, element.orig_id(), edited_at, tags, area_wkb=bytes.fromhex(factory.create_multipolygon(element)))
    except DeadlineExpiredError:
        raise
    except (RuntimeError, OSError) as error:
        raise OsmReadError("Cannot read complete source elements") from error
