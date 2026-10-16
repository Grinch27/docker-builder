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
