"""
Recorded answers of the public Nominatim instance, trimmed to the fields the search reads, for the tests that replace the network.

Copied on 2026-10-04 from plans_finished/nominatim_client/attachments/nominatim_check_2026-10-04.json, the answers to the searches
of 2026-10-03, so that no test reads the archive. Data (c) OpenStreetMap contributors, ODbL 1.0, http://osm.org/copyright;
every result keeps its licence field.
"""

RECORDED_ANSWERS: dict[str, list[dict[str, object]]] = {
    "Tauron Arena": [
        {
            "name": "Tauron Arena Kraków",
            "lat": "50.0677202",
            "lon": "19.9915490",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Stanisława Lema", "house_number": "7", "quarter": "Czyżyny", "suburb": "Czyżyny", "city_district": "Czyżyny", "postcode": "31-571", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 02",
            "lat": "50.0709433",
            "lon": "19.9825992",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Mogilska", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-443", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 01",
            "lat": "50.0717579",
            "lon": "19.9838626",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Aleja Jana Pawła II", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-446", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 03",
            "lat": "50.0718072",
            "lon": "19.9827240",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Janusza Meissnera", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-443", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków al. Pokoju 01",
            "lat": "50.0640930",
            "lon": "19.9886438",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Aleja Pokoju", "quarter": "Łęg", "suburb": "Czyżyny", "city_district": "Czyżyny", "postcode": "31-564", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 04-91",
            "lat": "50.0718763",
            "lon": "19.9848874",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Aleja Jana Pawła II", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-446", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 04",
            "lat": "50.0721208",
            "lon": "19.9852062",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Aleja Jana Pawła II", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-446", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków 02",
            "lat": "50.0669315",
            "lon": "19.9885472",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Stanisława Lema", "quarter": "Czyżyny", "suburb": "Czyżyny", "city_district": "Czyżyny", "postcode": "31-572", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 06",
            "lat": "50.0710078",
            "lon": "19.9824856",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Mogilska", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-443", "city": "Kraków"},
        },
        {
            "name": "TAURON Arena Kraków Wieczysta 02",
            "lat": "50.0710634",
            "lon": "19.9828213",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Mogilska", "quarter": "Rakowice", "city_district": "Prądnik Czerwony", "postcode": "31-443", "city": "Kraków"},
        },
    ],
    "Rynek Górny, Wieliczka": [
        {
            "name": "Rynek Górny",
            "lat": "49.9823654",
            "lon": "20.0601976",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Rynek Górny", "neighbourhood": "Osiedle Boża Wola", "suburb": "Osiedle Śródmieście", "postcode": "32-020", "town": "Wieliczka"},
        },
        {
            "name": "Rynek Górny",
            "lat": "49.9826118",
            "lon": "20.0602219",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Rynek Górny", "neighbourhood": "Osiedle Boża Wola", "suburb": "Osiedle Śródmieście", "postcode": "32-020", "town": "Wieliczka"},
        },
    ],
    "Florianska 1": [
        {
            "name": "",
            "lat": "50.0621261",
            "lon": "19.9393927",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Floriańska", "house_number": "1", "quarter": "Stare Miasto", "suburb": "Stare Miasto", "city_district": "Stare Miasto", "postcode": "31-019", "city": "Kraków"},
        }
    ],
    "Lipska 5": [
        {
            "name": "Lipska",
            "lat": "50.0401827",
            "lon": "19.9965120",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Rogatka", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-721", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0406913",
            "lon": "19.9885036",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Zagumnie", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-724", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0395338",
            "lon": "20.0033082",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Rogatka", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-716", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0397803",
            "lon": "20.0007388",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Rogatka", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-733", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0405708",
            "lon": "19.9926409",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-725", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0397307",
            "lon": "19.9995065",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Rogatka", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-721", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0396920",
            "lon": "20.0000776",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Rogatka", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-733", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0405600",
            "lon": "19.9848068",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "neighbourhood": "Zagumnie", "quarter": "Płaszów", "suburb": "Podgórze", "postcode": "30-720", "city": "Kraków"},
        },
        {
            "name": "Lipska",
            "lat": "50.0391481",
            "lon": "20.0043961",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {"road": "Lipska", "quarter": "Rybitwy", "suburb": "Podgórze", "postcode": "30-716", "city": "Kraków"},
        },
    ],
    "os. Strusia 23": [
        {
            "name": "Biedronka",
            "lat": "50.0877740",
            "lon": "20.0064636",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "address": {
                "house_number": "23",
                "neighbourhood": "Osiedle Józefa Strusia",
                "quarter": "Bieńczyce",
                "suburb": "Bieńczyce",
                "city_district": "Bieńczyce",
                "postcode": "31-810",
                "city": "Kraków",
            },
        }
    ],
    "Qwxzvbn": [],
}
