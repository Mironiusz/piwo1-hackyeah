"""Write invented GTFS feeds for the tests of the GTFS step; no row of a real feed enters the repository."""

import zipfile
from collections.abc import Mapping
from pathlib import Path

INVENTED_GTFS_TABLES: Mapping[str, str] = {
    "agency.txt": "agency_id,agency_name,agency_url,agency_timezone\r\nA1,Invented agency,https://invented.invalid,Europe/Warsaw\r\n",
    "stops.txt": (
        "stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station,wheelchair_boarding\r\n"
        "S1,Invented station,50.01,19.91,1,,2\r\n"
        "S1a,Invented platform,50.01,19.91,0,S1,\r\n"
        "S2,Invented stop,50.02,19.92,0,,0\r\n"
    ),
    "routes.txt": "route_id,route_short_name,route_type\r\nR1,1,900\r\nR2,2,3\r\n",
    "trips.txt": "route_id,service_id,trip_id\r\nR1,SV1,T1\r\n",
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\r\nT1,08:00:00,08:00:00,S1a,1\r\nT1,08:05:00,08:05:00,S2,2\r\n",
    "calendar_dates.txt": "service_id,date,exception_type\r\nSV1,20261004,1\r\n",
}


def apply_invented_gtfs_feed(path: Path, tables: Mapping[str, str] = INVENTED_GTFS_TABLES) -> Path:
    """Write a zip of invented GTFS tables, each named member holding the given text in UTF-8."""
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in tables.items():
            archive.writestr(name, content.encode("utf-8"))
    return path
