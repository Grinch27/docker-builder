#!/usr/bin/env python3
"""Read or update the application catalog embedded in README.md.

The config block is human-maintained. Version-table and version-json remain
generated run output; catalog writes never rewrite those other blocks.
"""
import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

START = '<!-- app-config:start -->'
END = '<!-- app-config:end -->'
FENCE = chr(96) * 3
SUMMARY_START = '<!-- app-summary:start -->'
SUMMARY_END = '<!-- app-summary:end -->'
TAG = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$')
NAME = re.compile(r'^[a-z0-9][a-z0-9_.-]*$')
POLICIES = {'none', 'keep', 'strip_channel', 'strip_channel_and_spaces'}
APP_KEYS = {'repository', 'base_image', 'platforms', 'tag_policy', 'targets'}
TARGET_KEYS = {'tag', 'dockerfile', 'build_arg', 'base_image', 'tag_policy'}

def catalog_from_readme(path):
    data = path.read_text(encoding='utf-8')
    if data.count(START) != 1 or data.count(END) != 1:
        raise ValueError('Expected exactly one app-config marker pair')
    raw = data.split(START, 1)[1].split(END, 1)[0].strip()
    if not raw.startswith(FENCE+'json\n') or not raw.endswith('\n'+FENCE):
        raise ValueError('app-config must be a single fenced JSON block')
    catalog = json.loads(raw[len(FENCE)+5:-len(FENCE)-1])
    validate(catalog, path.parent)
    return catalog

def validate(c, root):
    if not isinstance(c, dict) or c.get('schema_version') != 1:
        raise ValueError('Unsupported catalog schema')
    unexpected = set(c) - {'schema_version', 'apps'}
    if unexpected:
        raise ValueError('Unknown catalog fields: ' + ', '.join(sorted(unexpected)))
    apps = c.get('apps')
    if not isinstance(apps, dict) or not apps:
        raise ValueError('Empty or invalid apps object')
    existing = {path.name for path in (root / "application").iterdir()
                if path.is_dir() and not path.name.startswith(".")}
    missing_from_catalog = sorted(existing - set(apps))
    if missing_from_catalog:
        raise ValueError("Unregistered application directories: " + ", ".join(missing_from_catalog))
    refs, seen = {}, set()
    for name, app in apps.items():
        if not isinstance(app, dict):
            raise ValueError(name+': app must be object')
        unexpected = set(app) - APP_KEYS
        if unexpected:
            raise ValueError(name+': unknown app fields: '+', '.join(sorted(unexpected)))
        if not NAME.fullmatch(name) or not (root/'application'/name).is_dir():
            raise ValueError('Unknown or unsafe app: '+name)
        repo, platforms, base = app.get('repository'), app.get('platforms'), app.get('base_image')
        if not isinstance(repo,str) or not re.fullmatch(r'[a-z0-9][a-z0-9._/-]*/[a-z0-9._-]+',repo):
            raise ValueError(name+': invalid repository')
        if not isinstance(platforms,list) or not platforms or len(platforms)!=len(set(platforms)):
            raise ValueError(name+': invalid platforms')
        if any(not isinstance(p,str) or not re.fullmatch(r'linux/[a-zA-Z0-9_/.-]+',p) for p in platforms):
            raise ValueError(name+': bad platform')
        if not isinstance(base,str) or not base or '\n' in base:
            raise ValueError(name+': invalid base')
        if app.get('tag_policy','keep') not in POLICIES:
            raise ValueError(name+': invalid policy')
        ts=app.get('targets')
        if not isinstance(ts,list) or not ts:
            raise ValueError(name+': targets missing')
        for t in ts:
            if not isinstance(t,dict): raise ValueError(name+': target must be object')
            unexpected = set(t) - TARGET_KEYS
            if unexpected:
                raise ValueError(name+': unknown target fields: '+', '.join(sorted(unexpected)))
            tag,df=t.get('tag'),t.get('dockerfile','Dockerfile')
            if not isinstance(tag,str) or not TAG.fullmatch(tag):
                raise ValueError(name+': invalid tag')
            if not isinstance(df,str) or not re.fullmatch(r'[A-Za-z0-9_.-]+',df):
                raise ValueError(name+': invalid Dockerfile')
            if not (root/'application'/name/'build'/df).is_file():
                raise ValueError(name+': missing Dockerfile '+df)
            for key in ('build_arg','base_image'):
                val=t.get(key,'')
                if not isinstance(val,str) or '\n' in val or '\r' in val:
                    raise ValueError(name+': invalid '+key)
            if t.get('tag_policy',app.get('tag_policy','keep')) not in POLICIES:
                raise ValueError(name+': invalid target policy')
            if (name,tag) in seen: raise ValueError('Duplicate '+name+':'+tag)
            seen.add((name,tag))
            refs.setdefault((repo,tag),[]).append(name)
    return {'apps':len(apps),'targets':len(seen),
            'legacy_ref_conflicts':{r+':'+t:n for (r,t),n in refs.items() if len(n)>1}}

def get(c,app,tag):
    a=c['apps'].get(app)
    if a is None: raise ValueError('Unknown app: '+app)
    ts=[x for x in a['targets'] if x['tag']==tag]
    if len(ts)!=1: raise ValueError('Unknown target: '+app+':'+tag)
    t=ts[0]
    return {'app_branch':app,'tag_repo':tag,'repo_dockerhub':a['repository'],
            'arch_branch':','.join(a['platforms']),
            'base_image':t.get('base_image',a['base_image']),
            'dockerfile':t.get('dockerfile','Dockerfile'),
            'build_arg':t.get('build_arg',''),
            'tag_policy':t.get('tag_policy',a.get('tag_policy','keep'))}

def matrix(c,kind,runner):
    if kind=='version':
        items=[{'app_branch':a,'tag_repo':'latest','custom_env':'','runner_image':runner} for a in c['apps']]
    else:
        items=[{'app_branch':a,'tag_repo':t['tag'],'custom_env':'','runner_image':runner}
               for a,app in c['apps'].items() for t in app['targets']]
    return {'include':items}

def tags(item,version,consistent):
    result=[item['tag_repo']]
    if consistent and item['tag_policy']!='none':
        value=item['tag_repo']+'-'+version
        if item['tag_policy'].startswith('strip_channel'):
            value=value.split('-',1)[-1]
        if item['tag_policy']=='strip_channel_and_spaces':
            value=value.replace(' ','-')
        if value and value not in result:
            if not TAG.fullmatch(value): raise ValueError('Invalid computed tag: '+repr(value))
            result.append(value)
    return result

def render_summary(c):
    n=sum(len(a['targets']) for a in c['apps'].values())
    rows=[f'**{len(c["apps"])} applications / {n} build targets** (generated from configuration below).',
          '', '| Application | Registry repository | Tags | Platforms | Base image | Dockerfiles |',
          '|---|---|---|---|---|---|']
    for name,a in sorted(c['apps'].items()):
        tags=', '.join('`'+t['tag']+'`' for t in a['targets'])
        platforms=', '.join('`'+p.replace('linux/','',1)+'`' for p in a['platforms'])
        o=['`'+t['tag']+': '+t['base_image']+'`' for t in a['targets']
           if t.get('base_image') and t['base_image']!=a['base_image']]
        base='`'+a['base_image']+'`'+(' + '+', '.join(o) if o else '')
        files=', '.join('`'+f+'`' for f in dict.fromkeys(
            t.get('dockerfile','Dockerfile') for t in a['targets']))
        rows.append('| ['+name+'](application/'+name+'/) | `'+a['repository']+'` | '+
                    tags+' | '+platforms+' | '+base+' | '+files+' |')
    return '\n'.join(rows)

def updated_summary(text,c):
    if text.count(SUMMARY_START)!=1 or text.count(SUMMARY_END)!=1:
        raise ValueError('Expected one app-summary marker pair')
    left,rest=text.split(SUMMARY_START,1)
    middle,right=rest.split(SUMMARY_END,1)
    if SUMMARY_END in middle: raise ValueError('Out-of-order summary markers')
    return left+SUMMARY_START+'\n'+render_summary(c)+'\n'+SUMMARY_END+right

def atomic_write(path,old,new):
    if new==old: return 'unchanged'
    with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=path.parent,delete=False,prefix='.app-config-') as f:
        f.write(new)
        name=f.name
    try:
        os.chmod(name,path.stat().st_mode & 0o777)
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)
    return 'updated'

def write_summary(readme,c):
    old=readme.read_text(encoding='utf-8')
    return atomic_write(readme,old,updated_summary(old,c))

def check_summary(readme,c):
    text=readme.read_text(encoding='utf-8')
    if text!=updated_summary(text,c):
        raise ValueError('README app-summary is stale; run catalog.py summary --write')
    return True
def update(readme, c, app, field, value, *, scope='app', tag='latest'):
    """Atomically change only the static README catalog JSON block."""
    if app not in c['apps']:
        raise ValueError('Unknown app: '+app)
    if scope == 'app':
        if field not in ('repository', 'base_image', 'platforms', 'tag_policy'):
            raise ValueError('Unsupported app field: '+str(field))
        dest = c['apps'][app]
    elif scope == 'target':
        if field not in ('base_image', 'dockerfile', 'build_arg', 'tag_policy'):
            raise ValueError('Unsupported target field: '+str(field))
        targets = [t for t in c['apps'][app]['targets'] if t['tag'] == tag]
        if len(targets) != 1:
            raise ValueError('Unknown target: '+app+':'+tag)
        dest = targets[0]
    else:
        raise ValueError('Invalid scope: '+str(scope))
    if field == 'platforms':
        value = [p.strip() for p in value.split(',') if p.strip()]
    dest[field] = value
    validate(c, readme.parent)
    current = readme.read_text(encoding='utf-8')
    before, remaining = current.split(START, 1)
    _, after = remaining.split(END, 1)
    payload = (before + START + '\n' + FENCE + 'json\n' +
               json.dumps(c, indent=2, ensure_ascii=False) +
               '\n' + FENCE + '\n' + END + after)
    payload=updated_summary(payload,c)
    return atomic_write(readme,current,payload)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('command',choices=['validate','matrix','get','env','tags','set','summary'])
    p.add_argument('--readme',default='README.md')
    p.add_argument('--kind',choices=['version','build'],default='build')
    p.add_argument('--runner',default='ubuntu-latest')
    p.add_argument('--app')
    p.add_argument('--tag',default='latest')
    p.add_argument('--version',default='')
    p.add_argument('--consistent',default='false')
    p.add_argument('--output')
    p.add_argument('--app-only',action='store_true')
    p.add_argument('--check',action='store_true')
    p.add_argument('--write',action='store_true')
    p.add_argument('--scope',choices=['app','target'],default='app')
    p.add_argument('--field')
    p.add_argument('--value')
    args=p.parse_args()
    try:
        readme=Path(args.readme).resolve()
        c=catalog_from_readme(readme)
        if args.command=='validate':
            print(json.dumps(validate(c,readme.parent),sort_keys=True))
        elif args.command=='summary':
            if args.check and args.write: raise ValueError('check and write conflict')
            if args.check:
                check_summary(readme,c)
                print('app-summary: current')
            elif args.write: print(write_summary(readme,c))
            else: print(render_summary(c))
        elif args.command=='matrix':
            print(json.dumps(matrix(c,args.kind,args.runner),separators=(',',':')))
        elif args.command in ('get','env','tags'):
            if not args.app: raise ValueError('--app is required')
            item=(get(c,args.app,c['apps'][args.app]['targets'][0]['tag']) if args.app_only and args.command in ('env','tags') else get(c,args.app,args.tag))
            if args.app_only and args.command=='tags': item['tag_repo']=args.tag
            if args.command=='get':
                print(json.dumps(item,sort_keys=True))
            elif args.command=='tags':
                print(json.dumps(tags(item,args.version,args.consistent.lower()=='true')))
            else:
                keys=('repo_dockerhub','arch_branch','base_image','dockerfile','build_arg','tag_policy')
                data=''.join(k+'='+item[k]+'\n' for k in keys if not args.app_only or k in ('repo_dockerhub','arch_branch','base_image'))
                if args.output:
                    with open(args.output,'a',encoding='utf-8') as f: f.write(data)
                else: print(data,end='')
        else:
            if not args.app or args.field is None or args.value is None:
                raise ValueError('--app --field --value required')
            print(update(readme,c,args.app,args.field,args.value,scope=args.scope,tag=args.tag))
    except (KeyError,ValueError,OSError,json.JSONDecodeError) as e:
        print('catalog:',e,file=sys.stderr)
        return 2
    return 0

if __name__=='__main__':
    sys.exit(main())
