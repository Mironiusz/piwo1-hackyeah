/**
 * English words of the deck: the material of the Imagine What's Next submission for Huawei, presented only if the
 * jury invites the team. The notes of each slide are the spoken text.
 *
 * The structure must match `src/content/pl.js` key for key; `npm run lint` checks it (`scripts/content-check.mjs`).
 */
export default {
  page: {
    title: "EnableMe - Imagine What's Next",
    icons: { arrow: 'to', approx: 'approximately', check: 'yes', cross: 'no' },
  },
  slides: {
    title: {
      summary: 'title: EnableMe',
      kicker: "HackYeah 2026 - Imagine What's Next",
      heading: 'EnableMe',
      subtitle: 'Check the route before you leave home',
      notes: '<p>Hello, we are the EnableMe team. We will show an app that lets a person check a walking route in Kraków before they take it, built as a native HarmonyOS client.</p>',
    },
    problem: {
      summary: 'the problem: you learn about the barrier when you reach it',
      heading: 'You learn about the barrier when you reach it',
      who: 'Wheelchair users, parents with baby strollers, people for whom walking is difficult',
      barriers: ['stairs', 'high kerb', 'poor surface', 'steep incline', 'narrow passage'],
      gap: 'A map says: accessible or not. It does not say how it knows, or since when.',
      notes: `<p>A wheelchair user, a parent with a baby stroller or someone for whom walking is difficult usually learns about the stairs or the high kerb only when they reach it.</p>
<p>[click] If they have a map at all, it gives one label: accessible or not. It does not say where the information comes from, how old it is, or whether anyone checked it.</p>`,
    },
    solution: {
      summary: 'the answer: needs, route, facts',
      heading: 'Needs, route, facts',
      steps: [
        { head: 'Needs', text: 'What you avoid and what you need. No question about disability.' },
        { head: 'Route', text: 'A walking route in Kraków that avoids the barriers of your needs.' },
        { head: 'Facts', text: 'Every barrier and amenity with its source, date and status.' },
      ],
      footer: 'The app shows facts. The judgement stays with you.',
      notes: `<p>EnableMe works in three steps.</p>
<p>[click] First the needs: you mark what you avoid and what you need, or pick a preset. We never ask about a disability, because preferences are enough to match a route.</p>
<p>[click] Then a walking route in Kraków that avoids the barriers of your needs.</p>
<p>[click] And the facts: every barrier and every amenity has a source, a date and a status. No stars and no verdict. The judgement stays with you.</p>`,
    },
    states: {
      summary: 'the four states of a route segment',
      heading: 'Every segment tells what we know about it',
      legend: [
        { key: 'barrier', label: 'a barrier from your needs' },
        { key: 'clear', label: 'no barriers, full data' },
        { key: 'partial', label: 'partial data' },
        { key: 'nodata', label: 'no data' },
      ],
      grayscale: 'the same route in grayscale',
      rule: 'Missing information is never shown as accessible.',
      channels: 'A state is carried by color, icon and line pattern. Under the map the same route is a text list.',
      notes: `<p>A route is not simply green or red. Every segment has one of four states: a barrier from your needs, no barriers with full data, partial data, or no data.</p>
<p>[click] The key rule: missing information never pretends to be accessible. A segment we know nothing about is grey and dashed, not green.</p>
<p>[click] Each state is carried by color, an icon and a line pattern, so the states stay apart even in grayscale. Under the map the same route is a text list: the text alternative of the map for a screen reader.</p>`,
    },
    facts: {
      summary: 'facts, votes and contradictory data',
      heading: 'The community keeps the data current',
      card: {
        type: 'High kerb',
        sourceLabel: 'source',
        source: 'user report',
        dateLabel: 'date',
        date: '2026-10-04',
        statusLabel: 'status',
        status: 'unverified',
        conflict: 'Map data (OpenStreetMap): lowered kerb',
        rule: 'Until the report has 2 confirmations, the map data counts.',
      },
      votes: ['Still there', 'Gone'],
      statuses: ['unverified', 'confirmed', 'disputed', 'outdated'],
      rules: ['one vote per fact per day', 'the latest 5 people count', 'a vote without an account weighs half', 'flags and moderation'],
      notes: `<p>The data lives because of people. Anyone can report a barrier, an amenity or an inaccessible area, with or without an account.</p>
<p>[click] Every fact, OpenStreetMap facts included, can be confirmed as still there or reported as gone. The latest votes of five people give the status: unverified, confirmed, disputed or outdated.</p>
<p>[click] Here is the case of contradictory data: a user reported a high kerb, OpenStreetMap says the kerb is lowered. We show both with their status instead of deciding for the user. Until the report collects two confirmations, the map data counts. Vote limits, flags and a moderator protect against abuse.</p>`,
    },
    demo: {
      summary: 'the live demo',
      heading: 'Live',
      steps: [
        { head: 'Needs', text: 'I use a wheelchair' },
        { head: 'Route', text: 'Tauron Arena - Ogród Doświadczeń' },
        { head: 'No barrier-free route', text: 'Park Lotników Polskich' },
        { head: 'Contradictory data', text: 'a report against the map data' },
      ],
      footnote: 'The HarmonyOS app on the emulator. The reports in the demo are sample data around the Tauron Arena, marked as such in the app.',
      notes: `<p>Now live, on the HarmonyOS emulator.</p>
<p>We set the needs: I use a wheelchair. We plan a route from the Tauron Arena to Ogród Doświadczeń: a confirmed high kerb, unverified stairs with an alternative route, the stretches without data under What we do not know.</p>
<p>To Park Lotników Polskich there is no route without barriers: the app says so plainly and shows the route with the fewest barriers.</p>
<p>Finally a high kerb reported by a user that contradicts OpenStreetMap: source, date, status and the vote.</p>
<p>What the emulator cannot show: the location of a real walk, so the start is an address. If the emulator fails: the recorded video from the same scene.</p>`,
    },
    data: {
      summary: 'the data sources, their freshness and unavailability',
      heading: 'Where the data comes from, and when it is missing',
      head: ['source', 'what it gives', 'freshness', 'when unavailable'],
      rows: [
        ['OpenStreetMap (ODbL)', 'barriers, amenities, pedestrian network, map', 'a copy dated by the OSM state', 'the last complete copy with its date'],
        ["People's reports", 'points and areas', 'the date of the last confirmation', '-'],
        ['Address search (Nominatim)', 'an address to a point', 'on request, from our server', 'a plain message, no guessing'],
        ['City data (open data, MSIP)', 'the next step', 'after checking the terms', 'not used yet'],
      ],
      footer: 'Every fact has a status from votes, an OpenStreetMap fact included.',
      notes: `<p>We need neither a database kept by hand by the city nor access to its internal systems. The base is OpenStreetMap: an extract of Kraków, taken as a whole or not at all. The app always shows the date of the copy, and when the source is unavailable it works on the last complete copy.</p>
<p>On top of it come people's reports, with the date of their last confirmation. Addresses are searched from our server, without anything that identifies the person. Open city data joins once the terms of each dataset are checked.</p>`,
    },
    architecture: {
      summary: 'the architecture: data apart from presentation',
      heading: 'Data apart from presentation',
      ingest: { head: 'Data acquisition', items: ['OpenStreetMap extract', 'tag importer', 'PostGIS: facts and votes', 'Valhalla: route graph'] },
      api: { head: 'API', items: ['Python, FastAPI', '16 operations', 'one contract'] },
      clients: { head: 'Clients', items: ['web: React, MapLibre', 'HarmonyOS: ArkTS'] },
      extendHead: 'How it grows',
      extend: ['a new source: an importer to the fact model', 'a new category: a tag rule', 'a new city: an extract and a graph'],
      privacyHead: 'Privacy',
      privacy: ['needs stay on the device', 'a route request never leaves the project', 'an account without an email'],
      notes: `<p>The architecture separates data acquisition from presentation. The importer reads the OpenStreetMap extract, turns tags into barriers and amenities and stores them in PostGIS, and the Valhalla engine computes routes on our own graph.</p>
<p>[click] One API with sixteen operations serves two independent clients: the web app and the native HarmonyOS app in ArkTS and ArkUI. The HarmonyOS client uses the platform: LocationKit for the start from the current location, LocalizationKit for the language of the system, CoreFileKit to keep the needs and votes on the device, CryptoArchitectureKit for passwords, InputKit for the map with a keyboard.</p>
<p>[click] A new source is a new importer into the same fact model, a new category is a tag rule, a new city is a new extract and graph. Privacy is built in: the needs stay on the device, a route request never leaves the project, an account needs no email.</p>`,
    },
    business: {
      summary: 'the business model and operation',
      heading: 'Business model and operation',
      free: { head: 'Free', items: ['residents and tourists', 'no ads', 'no selling of data about people'] },
      paid: {
        head: 'Paying',
        items: [
          'cities and road authorities: deployment and barrier reports in one place',
          'venues and event organizers: a barrier-free route to their entrance',
          'partners of a reward programme for confirmations',
        ],
      },
      run: { head: 'Run outside the city infrastructure', items: ['an operator hosts one server with containers', 'data refresh and updates', 'moderation of reports'] },
      footer: 'We sell the service, not the data: OpenStreetMap data stays open.',
      notes: `<p>For residents and tourists the app is free.</p>
<p>[click] Those who gain from accessibility pay. Cities and road authorities get the deployment and the barrier reports confirmed by residents in one place. Hotels, museums and event organizers buy a barrier-free route to their entrance. Partners can fund rewards for confirmations, such as a public transport ticket.</p>
<p>[click] An operator runs the service outside the infrastructure of the city: one server with containers, data refresh, updates and moderation. We sell the service, not the data: what comes from OpenStreetMap stays open.</p>`,
    },
    status: {
      summary: 'what works and what is next',
      heading: 'What works and what is next',
      works: {
        head: 'Works today',
        items: [
          'needs and presets',
          'a route with four segment states and a list',
          'an alternative route and no barrier-free route',
          'facts with source, date, status and votes',
          'reports, accounts, moderation, Polish and English',
        ],
      },
      next: { head: 'Next', items: ['the server with the data of all of Kraków', 'photos in reports', 'open city data', 'reports back to OpenStreetMap', 'more cities'] },
      limits: 'Known limits of the prototype: sample data around the Tauron Arena, the hosted demo over plain HTTP.',
      closing: 'EnableMe - facts instead of labels.',
      notes: `<p>Today the whole main scenario runs on HarmonyOS, on sample data marked as such.</p>
<p>[click] Next: the server with the data of all of Kraków, photos in reports, open city data, sending reports back to OpenStreetMap and more cities.</p>
<p>[click] EnableMe: facts instead of labels, and uncertainty shown honestly. Thank you.</p>`,
    },
  },
};
