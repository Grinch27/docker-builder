# Application file simplification — phase 1

Baseline: `main@91103299b7ad2d65f9d2389ff56d3461386b2b71` contained 24 canonical applications and 91 tracked files below their directories (not counting `application/.example` or `application/route.md`): 23 upstream `meta-app.sh` and 24 built-image `test.sh`.

Phase 1 removes five committed `test/test.sh` files from `aria2`, `curl`, `privoxy`, `squid`, and `dnscrypt-proxy`; a shared POSIX probe (`scripts/ci/probe-image.sh`) now determines the actual installed version from inside each built image.

The legacy production, Dev, GPT and compatibility workflow code continues to search `application/<app>/test/*.sh`. It first runs `scripts/ci/materialize_test_hooks.py --app APP`, which creates **an untracked, ephemeral** `test.sh` with identical invocation behavior for the five supported apps; other applications retain their committed tests. `.gitignore` excludes only the five generated hook paths.

The shared probe output contract remains `version=<actual-installed-version>`; the upstream `meta-app` scripts are unchanged. Neither build context / Dockerfile nor Registry / Tag / Release logic is modified.

## Evidence and scope

- First parity commit `ce61fe73` ran a real `linux/amd64` Buildx five-image comparison, and all five generated shared parser values matched the independently committed legacy `test.sh` values.
- Second commit `f6251b2` removed the five scripts and regenerated them at runtime; the subsequent real five-image AMD64 parity jobs passed.
- Third commit `3fa6449b` adds a 5×2 platform `linux/amd64` / `linux/arm64` nonpublishing parity matrix (requires final live Actions completion evidence).
- `scripts/ci/test_probe_image.py` tests POSIX parsing, invalid profiles, empty version and multiline rejection.
- `scripts/ci/test_materialize_test_hooks.py` tests five profile generation, idempotence, refusal to overwrite independent scripts, and identical wrapper output.
- All existing 24 apps, 30 build targets, base images, repositories and tag policies remain in README Schema v2.

## Next migration candidates

1. Move additional simple `test.sh` rules to `probe-image.sh` after per-image live parity, keeping more complex SD.Next/ROCm and OpenWrt/runner tests unchanged until separate experiments.
2. Introduce a declarative upstream version strategy in README catalog before deleting `meta-app.sh`; never replace upstream probes by expected Docker labels.
3. Investigate `ttrss` metadata probe/test currently mirroring `vlmcsd` despite having a TTRSS Dockerfile, and its Dockerfile resource references, without unsafe deletion or rewriting.
4. Check FFmpeg's extra Dockerfile variants and SD.Next startup files for build-context dependencies before touching them.

Release/build parity is **not** proven by five isolated image-version checks. Production check → build → test → publish has not been executed by this migration.

Phase 2: README `config.apps.<app>.image_probe` became the canonical command and extractor for the original five; commit `9c0234f` passed 5×2 real architecture smoke and read-only unit tests. `doh-nosni` is a sixth declarative profile using `dnscrypt-proxy -version` with first-line extraction. Its previously tracked `test.sh` is removed in the next incremental commit, with a separate multi-stage Dockerfile smoke requirement. Other non-declarative applications retain their scripts.

Phase 4: all 24 complete test scripts are embedded in one expandable README HTML table, with deterministic HTML entity encoding for special characters. The legacy 18 `test.sh` files are copied byte-for-byte; six previously shared image probes use equivalent shell routines. The new materializer reads README by stable per-app markers, validates names and encoding, and recreates the original test path in the Actions workspace. Existing 18 scripts remain as independent test oracles until the smoke and byte-equivalence gates pass.

Phase 5 — duplicate-file retirement: after GitHub Actions validated 24/24 README embedded source snippets and compared all 18 still-existing shell sources byte-for-byte, the 18 tracked test/test.sh copies are removed. `docker_allinone_gpt.yml`'s two remaining hardcoded test paths (vlmcsd per-arch and local-registry matrix) now call the shared materializer explicitly before accessing the test file. The 24 apps' build inputs and all upstream meta-app probes remain unchanged. Fully representative production releases are outside this migration's test coverage.
