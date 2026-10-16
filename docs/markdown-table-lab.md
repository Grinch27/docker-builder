# Markdown-only catalog feasibility lab

**Non-production / 仅研究** — no `docker_allinone.yml`, `monitor_state.py`, or `catalog.py` write path reads this prototype.

Run `python3 -m unittest discover -s scripts/ci -p 'test_table_catalog_lab.py' -v`.

The lab renders a strict **17-column, 30-row Markdown table** from the current schema-v2
README JSON, then parses it back and compares all 24 application definitions, 30
build targets, and 24 historical monitor observations for lossless equivalence.

One row per target means monitoring observations are duplicated for multi-target
applications (runner, samba, adguardvpn-cli). The parser rejects inconsistent
repeated monitor data, duplicate targets, missing columns and invalid escapes.

**Trade-off:** Complete removal of JSON is possible, but a 17-column table is harder
to maintain than the 8-column visible table and combined structured JSON. This
prototype is intentionally isolated; a cutover requires safe atomic writes, escaping
rules, conflict handling, backward compatibility, and full check/build/publish tests.
