#!/usr/bin/env python3
"""Validate this specification pack, not an implemented Dovet application.

Usage: python scripts/validate_pack.py
Dependency: jsonschema (pip install jsonschema)
No network or paid provider calls are made.
"""
from __future__ import annotations
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    from jsonschema import Draft202012Validator, FormatChecker, ValidationError
except ImportError:
    raise SystemExit('Install jsonschema before running: python -m pip install jsonschema')

ROOT = Path(__file__).resolve().parents[1]
checks: list[dict[str, object]] = []

def record(name: str, condition: bool, detail: object = None) -> None:
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})
    if not condition:
        raise AssertionError(f'{name}: {detail}')

def canonical(data: object) -> bytes:
    return json.dumps(data, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False).encode('utf-8')

def insert(db: sqlite3.Connection, table: str, **values: object) -> None:
    # table and field names are constants controlled by this validation script.
    cols = ','.join(values)
    marks = ','.join('?' for _ in values)
    db.execute(f'INSERT INTO {table} ({cols}) VALUES ({marks})', tuple(values.values()))

def expect_sql_reject(db: sqlite3.Connection, label: str, fn) -> None:
    try:
        fn()
    except sqlite3.IntegrityError:
        record(label, True)
    else:
        record(label, False, 'Invalid row was accepted')

def luminance(h: str) -> float:
    channels = [int(h[i:i+2], 16)/255 for i in (1,3,5)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in channels]
    return .2126*linear[0]+.7152*linear[1]+.0722*linear[2]

def ratio(a: str,b: str) -> float:
    x,y=sorted([luminance(a),luminance(b)])
    return (y+.05)/(x+.05)

def main() -> None:
    required = [
      'START_HERE.md','CODEX_MASTER_PROMPT.md','AGENTS.md','contracts/schema.sql',
      'contracts/checkpoint.schema.json','contracts/recovery.schema.json','contracts/event.schema.json',
      'contracts/manifest.schema.json','contracts/README.md','design/tokens.css',
      'config/.env.example','config/policy.example.yaml','config/release-manifest.example.json',
      'hackathon/REQUIREMENTS.md','hackathon/VIDEO_PRODUCTION.md','hackathon/NARRATION.md',
      'hackathon/DEVPOST_DRAFT.md','hackathon/BUILDER_POSTS.md','diagrams/architecture.mmd','diagrams/erd.mmd'
    ]
    required += [f'spec/{name}' for name in (
      '01_PRD.md','02_ARCHITECTURE.md','03_ERD.md','04_CODEX_PLUGIN.md','05_AGENTS_AND_CONTRACTS.md',
      '06_SECURITY.md','07_UI_UX.md','08_MARKETING_WEBSITE.md','09_API.md','10_BUILD_PLAN.md',
      '11_TESTING.md','12_DEPLOYMENT.md','13_SOURCES.md')]
    record('required files', all((ROOT/x).is_file() for x in required), len(required))
    for p in sorted(ROOT.rglob('*.json')):
        json.loads(p.read_text())
    record('all JSON parses', True)
    validators = {}
    for kind in ('manifest','checkpoint','recovery','event'):
        schema=json.loads((ROOT/f'contracts/{kind}.schema.json').read_text())
        Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema, format_checker=FormatChecker())
        example=json.loads((ROOT/f'contracts/{kind}.example.json').read_text())
        validator.validate(example)
        validators[kind]=validator
        record(f'{kind} schema and example',True)
    recovery=json.loads((ROOT/'contracts/recovery.example.json').read_text())
    for label, change in (
      ('reject arbitrary command', {'command':'echo unauthorized'}),
      ('reject handoff without target', {'targetProviderProfileId':None}),
      ('reject invalid snapshot digest', {'expectedSnapshotSha256':'not-a-hash'}),
      ('reject unknown action', {'action':'approve_everything'}),
    ):
        bad={**recovery,**change}
        record(label, not validators['recovery'].is_valid(bad))
    manifest=json.loads((ROOT/'contracts/manifest.example.json').read_text())
    for bad_path in ('../escape','/absolute','a/../../escape','C:/outside','a\\b','a\x00b'):
        bad=json.loads(json.dumps(manifest));bad['files'][0]['path']=bad_path
        record(f'reject unsafe path {bad_path!r}',not validators['manifest'].is_valid(bad))
    blob=(ROOT/'contracts/fixture_stub.example.py').read_bytes()
    record('example blob digest',hashlib.sha256(blob).hexdigest()==manifest['files'][0]['sha256'])
    record('example blob size',len(blob)==manifest['files'][0]['sizeBytes'])
    checkpoint=json.loads((ROOT/'contracts/checkpoint.example.json').read_text())
    record('canonical manifest digest',hashlib.sha256(canonical(manifest)).hexdigest()==checkpoint['source']['snapshotSha256'])

    db=sqlite3.connect(':memory:')
    db.executescript((ROOT/'contracts/schema.sql').read_text())
    tables=db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    record('SQLite migration executes',True,len(tables))
    now='2026-09-13T00:00:00Z'
    for n in (1,2):
        insert(db,'projects',id=f'p{n}',name=f'Example {n}',root_path=f'/example/{n}',root_fingerprint=f'fp{n}',trust_state='approved',mode='managed',created_at=now,updated_at=now)
        insert(db,'project_policies',id=f'pol{n}',project_id=f'p{n}',version=1,body_json='{}',digest='a'*64,created_at=now)
        insert(db,'tasks',id=f't{n}',project_id=f'p{n}',policy_id=f'pol{n}',title='Example',objective='Synthetic validation',acceptance_json='[]',scope_json='{}',status='ready',created_at=now,updated_at=now)
    insert(db,'provider_profiles',id='profile1',label='Disabled sample',provider_kind='bedrock',config_json='{}',created_at=now,updated_at=now)
    run=dict(task_id='t1',provider_profile_id='profile1',attempt=1,mode='managed',status='queued',base_commit='0'*40,task_version=1,created_at=now)
    insert(db,'runs',id='run1',**run)
    expect_sql_reject(db,'reject cross-project task policy',lambda:insert(db,'tasks',id='bad-task',project_id='p2',policy_id='pol1',title='Bad',objective='Bad',acceptance_json='[]',scope_json='{}',status='ready',created_at=now,updated_at=now))
    expect_sql_reject(db,'reject cross-task parent run',lambda:insert(db,'runs',id='bad-parent',**{**run,'task_id':'t2','parent_run_id':'run1'}))
    expect_sql_reject(db,'reject missing provider FK',lambda:insert(db,'runs',id='bad-fk',**{**run,'provider_profile_id':'missing','attempt':2}))
    expect_sql_reject(db,'reject invalid run status',lambda:insert(db,'runs',id='bad-status',**{**run,'status':'fake_success','attempt':3}))
    ev=dict(run_id='run1',seq=1,event_type='run.created',source_kind='system',knowledge_kind='observed',payload_json='{}',observed_at=now)
    insert(db,'run_events',id='e1',**ev)
    expect_sql_reject(db,'reject duplicate event sequence',lambda:insert(db,'run_events',id='e2',**ev))
    record('SQLite foreign_key_check', not db.execute('PRAGMA foreign_key_check').fetchall())
    db.close()

    css=(ROOT/'design/tokens.css').read_text()
    for theme, selector in [('light',':root'),('dark','[data-theme="dark"]')]:
        body=css.split(selector+' {',1)[1].split('}',1)[0]
        colors=dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{6})',body))
        for foreground,background,min_ratio in (
          ('ink','canvas',4.5),('muted','canvas',4.5),('on-accent','accent',4.5),
          ('success','success-soft',4.5),('warning','warning-soft',4.5),('danger','danger-soft',4.5),('focus','surface',3),
        ):
            measured=ratio(colors[foreground],colors[background])
            record(f'{theme} contrast {foreground}/{background}', measured>=min_ratio, round(measured,2))
    fonts=list(ROOT.rglob('*.ttf'))+list(ROOT.rglob('*.otf'))+list(ROOT.rglob('*.woff*'))
    record('no font binaries',not fonts)
    deadline=datetime(2026,9,14,17,0,tzinfo=ZoneInfo('America/Los_Angeles'))
    cairo=deadline.astimezone(ZoneInfo('Africa/Cairo'))
    record('deadline timezone conversion',cairo.isoformat()=='2026-09-15T03:00:00+03:00',cairo.isoformat())
    sources=(ROOT/'spec/13_SOURCES.md').read_text()
    refs=set()
    for p in ROOT.rglob('*.md'):
        refs.update(re.findall(r'\bS\d{2}\b',p.read_text()))
    record('source IDs resolve in ledger',all(ref in sources for ref in refs),sorted(refs))
    report={
      'kind':'Dovet specification-pack validation',
      'preparedDate':'2026-09-13',
      'executedAtContainerClock':datetime.now(timezone.utc).isoformat(),
      'applicationBuilt':False,'deploymentVerified':False,'videoCreated':False,'submissionMade':False,
      'passed':True,'checksPassed':len(checks),'checks':checks,
      'limitations':['Does not validate future implementation, real providers, sandbox isolation, domain availability, deployment or video.', 'JSON Schema checks are not substitutes for runtime path, lineage and authorization validation.']
    }
    (ROOT/'evidence').mkdir(exist_ok=True)
    (ROOT/'evidence/PACK_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':True,'checks':len(checks),'sqliteTables':len(tables),'report':'evidence/PACK_VALIDATION.json'}))

if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        print(f'PACK VALIDATION FAILED: {exc}',file=sys.stderr)
        sys.exit(1)
