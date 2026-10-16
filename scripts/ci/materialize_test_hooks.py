#!/usr/bin/env python3
"""Materialize canonical README test and meta-app shell scripts.

Unknowns: future applications may legitimately lack a metadata probe.
Risks: prevent foreign-file overwrites, symlink following and host execution.
Verification: byte parity, explicit absence, idempotence and workflow behavior.
"""
import argparse
from pathlib import Path
import catalog

ROOT=Path(__file__).resolve().parents[2]

def scripts(root,kind='test'):
    text=(root/'README.md').read_text(encoding='utf-8')
    if kind=='test':
        return catalog.embedded_tests_from_text(text)
    if kind=='meta':
        return catalog.embedded_meta_from_text(text)
    raise ValueError('Unknown script kind: '+kind)

def materialize(root,app,kind='test'):
    text=(root/'README.md').read_text(encoding='utf-8')
    if app not in catalog.catalog_data_from_text(text)['apps']:
        raise ValueError('No embedded README script for '+app)
    script=scripts(root,kind).get(app)
    directory,filename=('meta-app','meta-app.sh') if kind=='meta' else ('test','test.sh')
    target=root/'application'/app/directory/filename
    if script is None:
        if kind!='meta':
            raise ValueError('No embedded README test for '+app)
        if target.exists() or target.is_symlink():
            raise ValueError('Unexpected script for missing meta-app: '+app)
        return 'missing'
    if target.is_symlink():
        raise ValueError('Symlink at generated script path: '+str(target))
    if target.is_file():
        if target.read_bytes()!=script.encode('utf-8'):
            raise ValueError('Existing app script differs from README: '+app)
        return 'existing'
    if target.exists():
        raise ValueError('Unexpected application script path: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(script.encode('utf-8'))
    target.chmod(0o755)
    return 'generated'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app',required=True)
    p.add_argument('--kind',choices=('test','meta'),default='test')
    args=p.parse_args()
    print(args.app+': '+materialize(ROOT,args.app,args.kind))

if __name__=='__main__':
    main()
