#!/usr/bin/env python3
"""Materialize canonical README HTML-table shell tests in the Actions workspace.

The original application-specific shell logic is preserved byte-for-byte.
Never executes a README script on the host; the existing workflow invokes
the ephemeral file inside the built image.
"""
import argparse
from pathlib import Path
import catalog

ROOT=Path(__file__).resolve().parents[2]

def scripts(root):
    text=(root/'README.md').read_text(encoding='utf-8')
    return catalog.embedded_tests_from_text(text)

def materialize(root,app):
    script=scripts(root).get(app)
    if script is None:
        raise ValueError('No embedded README test for '+app)
    target=root/'application'/app/'test'/'test.sh'
    if target.is_file():
        if target.read_bytes()!=script.encode('utf-8'):
            raise ValueError('Existing app test differs from README: '+app)
        return 'existing'
    if target.exists():
        raise ValueError('Unexpected application test path: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(script.encode('utf-8'))
    target.chmod(0o755)
    return 'generated'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--app',required=True)
    args=p.parse_args()
    print(args.app+': '+materialize(ROOT,args.app))

if __name__=='__main__':
    main()
