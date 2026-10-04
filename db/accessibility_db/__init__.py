"""
The shared model of the accessibility database and the chain of its schema revisions.

The OpenStreetMap import and the backend both import the tables and the closed lists from here instead of describing
them each on its own. The target schema is `docs/product/schema.md`; the revisions in `migrations/versions/` create it,
and the tests of `db/tests/` check that this model matches what the revisions stored.
"""
