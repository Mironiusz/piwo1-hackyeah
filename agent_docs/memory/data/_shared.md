## 2026-10-04 - Crash-safe import ownership (backend skeleton)

- What changed: Dedicated service sessions, a persistent private workspace journal and local OS exclusion protect import admission through cleanup.
- Why: Session-bound database locks alone cannot protect file cleanup after every database session disappears.
- Reusable pattern: Keep apply_import_exclusion open through all work; execute mutating tools through apply_import_process; use one publication deadline and distinguish unknown commit acknowledgement from confirmed rollback.
- Risk / notes: One database uses one machine and one persistent local filesystem root. Linux tools must preserve inherited descriptors and stay in the supervised group; Windows uses a non-breakaway Job Object. Consumer pointer reconciliation is not a foundation contract. There is no product domain rule yet; create DATA.md and DATA_ALGORITHM.md when product access is implemented.

## 2026-10-04 - Owner-crash semantics differ by platform (backend skeleton, Windows acceptance)

- What changed: The owner-crash acceptance of the import exclusion has a Linux and a Windows variant, and the Linux-only functions of `data/import_process.py` refuse other platforms in a form mypy narrows.
- Why: On Linux a contained writer can outlive its killed owner and keeps exclusion through the inherited descriptor; on Windows the kill-on-close job ends the whole tree with its owner, so the next launch recovers at once. One cross-platform expectation was wrong on one of the two systems.
- Reusable pattern: Write a crash or process test per platform with its own expectation, and guard platform-only code with `if sys.platform != "<platform>": raise ...` so mypy checks the module on both Windows and Linux.
- Risk / notes: A Windows run never proves the Linux orphan path and a Linux run never proves the Job Object path; check `mypy --platform linux` next to the native run.

## 2026-10-04 - Two copies of the immutable directory and pointer mechanism (public_transport_routing, S-9)

- What changed: `data/routing_directories.py` holds the preparation directory, the placement by a rename and the pointer replaced through a synced temporary file for any parent and pattern of names, used by `gtfs/` and `transit/` under `ROUTING_DATA_DIR`; `data/routing_data.py` keeps its own copy of the same mechanism for `copies/` and `current`.
- Why: `route_planning` was changing `data/routing_data.py` on the same tree while the GTFS step was written, so it was not generalized then.
- Reusable pattern: a new kind of immutable routing data takes `routing_directories.py` with its own parent and name pattern, and its pointer is written only after the placement.
- Risk / notes: once `route_planning` is merged, `routing_data.py` should delegate its preparation, placement and pointer to `routing_directories.py`, keeping its function names and `RoutingDataError`.

## 2026-10-04 - A broad ValueError catch hides a configuration failure (route_planning)

- What changed: `fetch_valhalla_answer` of `data/valhalla.py` builds its client, which loads the configuration facade, before the `try` that catches `httpx.HTTPError` and `ValueError`.
- Why: `ConfigurationError` of `config/settings.py` derives from `ValueError`, so a missing entry was reported as an unavailable routing service; `ValueError` is caught there only for an answer that is not JSON.
- Reusable pattern: in the data layer, call whatever reads `config.config` outside a `try` that catches `ValueError`, and keep that `try` around the call and the decoding alone.
- Risk / notes: `fetch_krakow_boundary` of `service/route_boundary.py` follows the same rule; a new adapter that catches `ValueError` has to as well.

## 2026-10-04 - Sample transaction completion and data-layer documentation (sample_data)

- What changed: sample storage uses one Repeatable Read snapshot, explicit bound projections and batch inserts, returning provider success only after acknowledged commit.
- Why: site checks must not mix published network versions, and a retry after uncertainty must preserve existing facts and votes.
- Reusable pattern: a primary-key conflict does not overwrite; only returned new identifiers receive author votes. A failed or invalidated connection is insufficient rollback evidence, and failure around a sent commit remains unknown unless the server explicitly rejects it.
- Risk / notes: use the sole shared engine factory; no runtime delete or DDL belongs in this provider. `data/DATA.md` and `data/DATA_ALGORITHM.md` do not describe `data/sample_data.py` yet; its storage contract lives in `service/SERVICE.md`, `service/SERVICE_ALGORITHM.md` and `docs/data/sample_data.md`.
