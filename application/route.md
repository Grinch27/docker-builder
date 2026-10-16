# docker-builder application layout

The canonical app and target configuration is the JSON block in
[../README.md](../README.md) between the app-config markers. It replaces
per-app env/vars.env, build/build.sh and push/tag_version.sh.

Use this directory structure for a new app:

    application/<app>/
    ├── build/
    │   ├── Dockerfile
    │   └── any files used by COPY, ADD or Dockerfile build steps
    ├── meta-app/
    │   └── meta-app.sh
    └── test/
        └── test.sh

Multiple Dockerfiles, build support scripts and configuration assets remain
inside build/; each target names its Dockerfile in the root README catalog.

To manage configs from the repository root:

    python3 scripts/ci/catalog.py validate
    python3 scripts/ci/catalog.py matrix --kind build
    python3 scripts/ci/catalog.py get --app runner --tag actions
    python3 scripts/ci/catalog.py env --app runner --tag actions
    python3 scripts/ci/catalog.py tags --app runner --tag actions --version 1.0 --consistent true

Supported simple write (only affects app-config):

    python3 scripts/ci/catalog.py set --app runner --field base_image --value debian:testing-slim

For target additions or changes to platforms, edit the single JSON block,
run validate and the non-publishing GPT Actions smoke before relying on
the production workflow. The app-version-table and app-version-json sections
are generated runtime state, not configuration inputs.

Existing compatibility notes:
- Both novnc and novnc_alpine currently target grinch27/novnc:latest.
  The parser reports this pre-existing ownership conflict; it does not
  change published tags without an explicit decision.
- samba:alpine now uses alpine.Dockerfile with alpine:latest base image.
- Legacy manual/Dev workflows consume the shared catalog and generic
  build executor; their full publishing paths need separate regression.

Target-specific update example (preserves all other README sections):

    python3 scripts/ci/catalog.py set --scope target --app samba --tag alpine --field base_image --value alpine:latest
    python3 scripts/ci/catalog.py set --scope target --app runner --tag actions --field dockerfile --value actions.Dockerfile

Application platform update:

    python3 scripts/ci/catalog.py set --scope app --app vlmcsd --field platforms --value linux/amd64,linux/arm64,linux/386

README's human-readable `app-summary` is derived from the canonical `app-config` JSON. The `catalog.py set` operation updates both atomically; after manually editing the JSON run `python3 scripts/ci/catalog.py summary --write` followed by `summary --check`. Collapsible JSON containers are presentation only and do not affect Actions.

Unified README data schema v2: a single `app-config` fenced JSON document contains `config` (reviewed static settings) and `monitor.records` (Actions-owned historical observations). The visible table combines both. The legacy separate version JSON is removed; the parser retains read-only compatibility for historical v1 documents. Do not edit `monitor.records` manually unless restoring an audited snapshot.

Shared actual-image probe migration: `scripts/ci/probe-image.sh` supports `aria2`, `curl`, `privoxy`, `squid`, and `dnscrypt-proxy` via `sh probe-image.sh APP` executed inside the built image. Do not remove application test scripts until the non-publishing `[probe-smoke]` parity matrix and every caller migration pass. Expected upstream version and actual installed version remain separate.
