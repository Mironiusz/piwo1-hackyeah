Using msip api integrate Do geometrii przystanków i ich wyposażenia (wiaty, ławki):

    MSIP WFS / WMS (Zbiór: Przystanki autobusowe i tramwajowe – ID: 1490).

Do analizy sieci pieszej i wyliczania izochron:

    MSIP WFS (Sieć transportowa – ID: 2961) lub zewnętrzny silnik routingu oparty o OpenStreetMap (np. OpenRouteService, ORS-Isochrone API).

APIs. I want the app's backend to get data from MSIP once in a while (like once a day) and it saves the data into the local database. Then frontend when it asks for the data the backend only takes it from the apps database.