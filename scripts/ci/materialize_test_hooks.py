#!/usr/bin/env python3
"""Generate an ephemeral legacy test.sh from README config.apps[app].image_probe.

No arbitrary eval or shell fragments. All arguments are quoted literals and the
extractor belongs to a small validated vocabulary. Existing custom test scripts
are preserved. Temporary files are never committed.
"""
import argparse
import shlex
from pathlib import Path

import catalog

ROOT = Path(__file__).resolve().parents[2]

def profiles(root):
    data = catalog.catalog_data_from_text((root / 'README.md').read_text(encoding='utf-8'))
    return {name: item['image_probe'] for name, item in data['apps'].items() if 'image_probe' in item}

def generate(app, profile):
    catalog.validate_image_probe(app, profile)
    argv = ' '.join(shlex.quote(p) for p in profile['argv'])
    extract = profile['extract']
    lines = [
        '#!/bin/sh',
        '# GENERATED FROM README.md image_probe; DO NOT COMMIT.',
        'set -eu',
        'set -- ' + argv,
        'result=$("$@")',
    ]
    kind = extract['kind']
    if kind == 'first_line':
        lines.append('version=$(printf "%s\n" "$result" | awk \'NR==1 { print; exit }\')')
    elif kind == 'first_field':
        lines.append('version=$(printf "%s\n" "$result" | awk -v field='+
                     shlex.quote(str(extract['field']))+
                     ' \'NR==1 { print $field; exit }\')')
    else:
        lines.append('version=$(printf "%s\n" "$result" | awk -v match='+
                     shlex.quote(extract['match'])+
                     ' -v field='+shlex.quote(str(extract['field']))+
                     ' \'index($0,match)==1 { print $field; exit }\')')
    lines += [
        'if [ -z "$version" ]; then echo "Empty actual image version: ' + app + '" >&2; exit 1; fi',
        'case "$version" in *[![:print:]]*) echo "Invalid multiline image version" >&2; exit 1;; esac',
        'printf "version=%s\n" "$version"',
    ]
    return '\n'.join(lines)+'\n'

def materialize(root: Path, app: str):
    data = profiles(root)
    target = root / 'application' / app / 'test' / 'test.sh'
    if app not in data:
        if not target.is_file():
            raise ValueError('Non-declarative app has no test.sh: ' + app)
        return 'existing'
    generated = generate(app, data[app])
    if target.is_file():
        if target.read_text(encoding='utf-8') != generated:
            raise ValueError('Refusing to replace independent app test: ' + str(target))
        return 'unchanged'
    if target.exists():
        raise ValueError('Unexpected test hook path: ' + str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(generated, encoding='utf-8')
    target.chmod(0o755)
    return 'generated'

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app', required=True)
    args = p.parse_args()
    print(args.app + ': ' + materialize(ROOT, args.app))

if __name__ == '__main__':
    main()
