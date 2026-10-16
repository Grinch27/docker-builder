#!/usr/bin/env python3
"""Materialize conventional test hooks for shared-version-probe applications.

Generated hooks are ephemeral workspace files; no Dockerfile, base image,
registry destination, upstream probe, or image version is changed.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILES = frozenset(("aria2", "curl", "privoxy", "squid", "dnscrypt-proxy"))

def materialize(root: Path, app: str) -> str:
    if app not in PROFILES:
        path = root / "application" / app / "test" / "test.sh"
        if not path.is_file():
            raise ValueError("Non-shared app has no test.sh: " + app)
        return "existing"
    source = root / "scripts" / "ci" / "probe-image.sh"
    text = source.read_text(encoding="utf-8")
    if not text.startswith("#!/bin/sh\n"):
        raise ValueError("Shared probe must remain POSIX sh")
    # set positional argument exactly as when the single shared probe is invoked.
    generated = "#!/bin/sh\n# GENERATED from scripts/ci/probe-image.sh; do not commit.\nset -- " + app + "\n" + text.split("\n", 1)[1]
    target = root / "application" / app / "test" / "test.sh"
    if target.is_file():
        if target.read_text(encoding="utf-8") != generated:
            raise ValueError("Refusing to replace independent app test: " + str(target))
        return "unchanged"
    if target.exists():
        raise ValueError("Unexpected test hook path: " + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generated, encoding="utf-8")
    target.chmod(0o755)
    return "generated"

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True)
    args = parser.parse_args()
    print(args.app + ": " + materialize(ROOT, args.app))

if __name__ == "__main__":
    main()
