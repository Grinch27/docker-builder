#!/usr/bin/env python3
"""Experimental Markdown-only catalog codec; never consumed by production Actions.

This is a strict, deliberately wide, ONE-TABLE lossless roundtrip study.
No GitHub workflow, Docker build, or README write path imports this module.
"""

import json
import re

FIELDS = (
    'App', 'Repository', 'App base', 'Platforms', 'App tag policy',
    'Target tag', 'Dockerfile', 'Target base override', 'Build arg',
    'Target tag policy override', 'Probe tag', 'Probe repository',
    'Probe base', 'Probe architectures', 'Probe platform',
    'Probe version', 'Probe status', 'Image probe JSON',
)

def encode(value):
    text=str(value)
    if '\n' in text or '\r' in text:
        raise ValueError('Multiline values are not allowed in strict tables')
    return text.replace('\\','\\\\').replace('|','\\|')

def parse_line(line):
    if not line.startswith('|') or not line.endswith('|'):
        raise ValueError('Table row must have both boundary pipes')
    fields=[]
    buf=''
    escape=False
    for char in line[1:-1]:
        if escape:
            if char not in ('|','\\'):
                raise ValueError('Unknown Markdown cell escape')
            buf+=char
            escape=False
        elif char=='\\':
            escape=True
        elif char=='|':
            fields.append(buf.strip())
            buf=''
        else:
            buf+=char
    if escape: raise ValueError('Dangling escape')
    fields.append(buf.strip())
    return fields

def render(config, records):
    observed={r['app_branch']:r for r in records}
    lines=['| '+' | '.join(FIELDS)+' |',
           '| '+' | '.join('---' for _ in FIELDS)+' |']
    for app,settings in config['apps'].items():
        r=observed.get(app)
        if r is None: raise ValueError('Missing observation for '+app)
        for target in settings['targets']:
            values=[app,settings['repository'],settings['base_image'],
                    ','.join(settings['platforms']),settings['tag_policy'],
                    target['tag'],target.get('dockerfile','Dockerfile'),
                    target.get('base_image',''),target.get('build_arg',''),
                    target.get('tag_policy',''),r['tag_repo'],r['repo_dockerhub'],
                    r['base_image'],r['arch_branch'],r['platform_used'],
                    r['version'],r['status'],
                    json.dumps(settings['image_probe'],sort_keys=True,separators=(',',':')) if 'image_probe' in settings else '']
            lines.append('| '+' | '.join(encode(v) for v in values)+' |')
    return '\n'.join(lines)+'\n'

def parse(table):
    lines=[line for line in table.splitlines() if line.strip()]
    if len(lines)<3: raise ValueError("Empty table")
    if parse_line(lines[0]) != list(FIELDS): raise ValueError("Unknown column schema")
    if parse_line(lines[1]) != ['---']*len(FIELDS):
        raise ValueError("Incorrect header delimiter")
    apps={}
    seen=set()
    observations={}
    for line in lines[2:]:
        fields=parse_line(line)
        if len(fields)!=len(FIELDS): raise ValueError("Missing or excess columns")
        (app,repo,base,platforms,policy,tag,doc,override,arg,tag_policy,
         probe_tag,probe_repo,probe_base,probe_arch,probe_platform,version,status,probe_json)=fields
        if not app or not repo or not tag or not base or not policy:
            raise ValueError("Required configuration cell empty")
        if (app,tag) in seen: raise ValueError("Duplicate target")
        seen.add((app,tag))
        shared={'repository':repo,'base_image':base,
                'platforms':platforms.split(','),'tag_policy':policy}
        if probe_json:
            shared['image_probe']=json.loads(probe_json)
        if app not in apps: apps[app]={**shared,'targets':[]}
        if set(apps[app]) - {'targets'} != set(shared) or any(apps[app][key]!=value for key,value in shared.items()):
            raise ValueError("Conflicting application settings")
        target={'tag':tag,'dockerfile':doc}
        if override: target['base_image']=override
        if arg: target['build_arg']=arg
        if tag_policy: target['tag_policy']=tag_policy
        apps[app]['targets'].append(target)
        observation={'app_branch':app,'tag_repo':probe_tag,
                     'repo_dockerhub':probe_repo,'version':version,
                     'base_image':probe_base,'arch_branch':probe_arch,
                     'platform_used':probe_platform,'status':status}
        if app in observations and observations[app]!=observation:
            raise ValueError("Conflicting per-app monitoring metadata")
        observations[app]=observation
    return {'schema_version':1,'apps':apps}, [observations[k] for k in sorted(observations)]

def compare_with_readme(readme, catalog_module):
    text=readme.read_text(encoding='utf-8')
    config=catalog_module.catalog_data_from_text(text)
    versions=catalog_module.snapshot_from_readme(text)
    restored_config,restored_monitor=parse(render(config,versions))
    if restored_config != config: raise AssertionError("Target config changed in roundtrip")
    if sorted(restored_monitor,key=lambda r:r["app_branch"])!=sorted(versions,key=lambda r:r["app_branch"]):
        raise AssertionError("Monitoring history changed in roundtrip")
    return {"apps":len(config["apps"]),"targets":sum(len(a["targets"]) for a in config["apps"].values()),
            "observations":len(versions),"table_columns":len(FIELDS),
            "table_bytes":len(render(config,versions).encode("utf-8"))}

