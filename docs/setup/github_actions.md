# GitHub Actions

Document state: 2026-10-04

## What this document covers

The workflows in `.github/workflows/`: what starts each of them, what it checks or publishes, and why it is built the way it is. The workflow files have no comments, by the no line comments rule, so their decisions are described here, the way `valhalla/README.md` describes `valhalla-image.yml`. Using the published images on the server is described in `docs/deployment/hosted_demo.md`, section Pulling the published images.

| Workflow             | Started by                                                  | What it does                                                                             |
| -------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `ci.yml`             | a pull request to `dev` or `main`, a push to them, a person | the gates of the Definition of Done that need no real database                           |
| `demo-images.yml`    | a pull request to `dev` or `main`                           | builds the five images of the hosted demo and publishes nothing                          |
| `demo-images.yml`    | a push to `main`, a person                                  | builds the five images and publishes them to the GitHub container registry               |
| `valhalla-image.yml` | a person only                                               | publishes the versioned routing image `valhalla-a11y`, described in `valhalla/README.md` |

Nothing here deploys anything. A server uses a published image only after a person pulls it.

## The pipeline of the Definition of Done

`ci.yml` is the pipeline that `docs/standards/standard_git.md`, section Branch roles and merge directions, asks for. It has two jobs, one per check ecosystem, as the comment above the target `lint` of `makefile` foresees.

The job Python gates installs the tools the way `README.md`, section Requirements, does: a virtual environment `venv` with `./db` first and then the root project with `.[dev]`, on the newest Python 3.13 of the runner. Then it runs, each as its own step, the `make` targets `lint-python`, `typecheck`, `deadcode`, `deps`, `security`, `audit` and `test-unit`. The job Node gates installs the root `node_modules` and those of `frontend/` with `npm ci` and runs `lint-docs`, `frontend-format-check`, `frontend-typecheck`, `frontend-lint` and `frontend-test`. Together they are `make check-unit` and `make frontend-check`; the steps call the same targets, so a gate changed in `makefile` changes here too.

Every gate is a step of its own and runs even when an earlier gate failed, as long as the installation succeeded. One run then shows every failing gate, not only the first one.

The Node version is `22.22.0`, the one of the build stage of `deploy/proxy.Dockerfile`, so the frontend is checked with the Node that builds it for the demo. A change of one is made in both places.

The runner has no environment file, so the test of the environment contract skips its check of the local files with the name of the file, as it does on any machine without them.

What the pipeline does not run:

- The critical tests, `make test-critical` and `db/tests/`, need a real database with PostGIS and pgRouting. Kuba decided on 2026-10-04 to keep them out of the pipeline, so `docs/standards/standard_tests.md` still asks a person and the review to run them for code that reads or writes the database.
- The check of the generated map style, `npm --prefix frontend run map-style:check`, is not a gate of `docs/standards/standard_frontend.md`, section Gates.

A new push to a pull request cancels the run of its previous push. A run of a push to `dev` or `main` is never cancelled.

That merging waits for a green pipeline is a setting of the branch protection of `dev` and `main` on GitHub, which names the checks Python gates and Node gates as required. It lives outside this tree and nothing here sets or verifies it.

## The images of the hosted demo

`demo-images.yml` builds the five images that `deploy/compose.yaml` builds on the server, from the same Dockerfiles and contexts:

| Image      | Dockerfile                  | Context     |
| ---------- | --------------------------- | ----------- |
| `routing`  | `valhalla/Dockerfile`       | `valhalla/` |
| `backend`  | `deploy/backend.Dockerfile` | the root    |
| `proxy`    | `deploy/proxy.Dockerfile`   | the root    |
| `database` | `db/image/Dockerfile`       | `db/image/` |
| `migrate`  | `db/image/Dockerfile.tools` | `db/`       |

A run of a pull request builds all five and publishes nothing, so a broken Dockerfile, a dependency that no longer installs or a frontend that no longer builds fails the pull request, before the server meets it.

A run of a push to `main`, or one started by a person, pushes each image to `ghcr.io/<owner>/enableme-<image>`, where `<owner>` is the owner of the repository on GitHub in lower case, with the tag `sha-<commit>` and the full hash of the commit. After all five are pushed, a run on `main` moves the tag `main` of each of them to that commit. The tag `main` moves only after the last push, so the five `main` tags always name one commit, and a run that fails halfway leaves them where they were. A run a person starts on another branch publishes only its `sha-` tags, so a branch can be tried on the server before it is merged. There is no `latest` tag.

The backend image is built `FROM` the routing image through the build context `routing`. On the server Compose takes it from the local image `enableme-routing:local`. On the runner the builder runs in a container of its own and cannot see the images of the Docker daemon, so the run pushes the routing image to a throwaway registry, a service container of the job at `localhost:5000`, and gives it to the backend build by its digest. The builder runs on the network of the host to reach that registry, and the registry ends with the job.

Each image keeps its build layers in its own scope of the GitHub Actions cache. The first run compiles Valhalla from scratch, which took 11 min 33 s on the machine of the spike (`valhalla/README.md`); later runs reuse the compiled layers until `valhalla/` changes. A run is stopped after 120 minutes.

The run pushes with the token GitHub gives every run, `GITHUB_TOKEN`, allowed to write packages. A run of a pull request never logs in.

The routing image is published twice under two names: `valhalla-a11y` by `valhalla-image.yml`, with a version tag a person raises, and `enableme-routing` here, with the tags of a commit. The images of the demo use `enableme-routing`, so the five images of one commit always come from that commit.

The first publish creates the five packages. Whether a package is public is set on its page on GitHub, under Package settings, by the owner of the repository. A private package needs a login on the server first, as in `valhalla/README.md`, section Pulling the image on a server.

The build of the backend through the throwaway registry, and the builds of the proxy, the database and the schema revision image with a builder in its own container, were run on a developer machine on 2026-10-04 with Docker 27.2.1 and Buildx 0.16.2. No run on GitHub has been made yet, so its time and its use of the disk of the runner are not measured.
