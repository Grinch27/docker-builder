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

P1 runtime migration: five simple image version hooks are now **generated only in the Actions workspace** by `python3 scripts/ci/materialize_test_hooks.py --app APP`. The generator embeds the shared POSIX `probe-image.sh` logic into the legacy `application/APP/test/test.sh` execution path, allowing existing production, Dev, GPT and compatibility build jobs to run unchanged tests while no longer committing five redundant per-app scripts. Calls must occur before scanning `test/*.sh` or checking whether the `test/` directory exists. Do not use generated files as permanent repository sources.

Declarative image tests (Phase 2): `README.md` Schema v2 `config.apps.<app>.image_probe` contains an `argv` array and an `extract` descriptor (`first_line`, `first_field` or `prefix_field`). `scripts/ci/materialize_test_hooks.py` validates these fields and creates a short `test.sh` in the Actions checkout only. It does not evaluate arbitrary shell snippets from README. The old `scripts/ci/probe-image.sh` is a temporary test oracle for the first five profiles and not the production configuration source.

The same declarative `first_line` extractor now covers `doh-nosni` (installed `dnscrypt-proxy -version`). Its custom multi-stage Dockerfile is unchanged; both architectures remain gated by non-publishing Buildx parity.

All 24 built-image tests are now stored **in an expandable HTML table in root README.md** (24 rows, one per application), enclosed by `app-tests` and per-app `app-test` markers. Scripts retain exact POSIX shell source; HTML escape codes preserve newline and pipe within table cells. `scripts/ci/materialize_test_hooks.py` generates the legacy `application/<app>/test/test.sh` only in the Actions checkout. The 18 original files are retained during byte-for-byte parity validation and are to be retired only after test success. The six previously declarative `image_probe` values are now replaced by scripts in that table; the production JSON still solely controls build settings and monitored state.

The `Applications / 应用清单` Markdown table includes a ninth **Test** column, with one expandable `<details><pre><code>` shell script per application. The former standalone `Application test scripts` section has been removed. Test markers stay inside `app-summary`; catalog and monitor regeneration parse the existing scripts first, preserving all 24 script bodies. Scripts only execute inside the built container.


### README-embedded meta-app scripts

The Applications table now contains 23 expandable upstream metadata scripts;
ffmpeg deliberately has no metadata probe. Run `python3 scripts/ci/materialize_test_hooks.py --app APP --kind meta` before scanning `application/APP/meta-app/*.sh`.
The generator preserves original shell source and does not execute it on the host.
`--kind test` remains the default for built-image testing.
