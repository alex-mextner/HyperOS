#!/usr/bin/env python3
from pathlib import Path
from collections import defaultdict
import csv,re,sys
ROOT=Path(__file__).resolve().parents[1]
errors=[]; warnings=[]
reg={}; title={}
for p in ROOT.rglob('*.md'):
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith(('sources/original/','sources/extracted/','wiki/')): continue
    t=p.read_text(encoding='utf-8-sig',errors='replace')
    m=re.search(r'^id:\s*["\']?([^"\'\n]+)',t,re.M)
    if m:
        did=m.group(1).strip()
        if did in reg: errors.append(f'duplicate document id {did}: {reg[did]} and {rel}')
        reg[did]=rel
    else: warnings.append(f'no document id: {rel}')
    if rel not in ('README.md',) and '## Table of Contents' not in t:
        errors.append(f'{rel}: missing Table of Contents')
anchor_cache={}
def anchors(rel):
    if rel not in anchor_cache:
        t=(ROOT/rel).read_text(encoding='utf-8-sig',errors='replace')
        anchor_cache[rel]=set(re.findall(r'<a\s+id=["\']([^"\']+)',t))
    return anchor_cache[rel]
xre=re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
for p in ROOT.rglob('*.md'):
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith(('sources/original/','sources/extracted/','wiki/')): continue
    t=p.read_text(encoding='utf-8-sig',errors='replace')
    for ref in xre.findall(t):
        did,_,a=ref.partition('#')
        if did not in reg: errors.append(f'{rel}: unknown xref {did}')
        elif a and a not in anchors(reg[did]): errors.append(f'{rel}: missing anchor {did}#{a}')
    # Validate local Markdown links to bundled files.
    for target in re.findall(r'\[[^\]]*\]\((?!https?://|mailto:|#)([^) ]+)(?:#[^) ]*)?\)',t):
        pathpart=target.split('#',1)[0]
        if not pathpart: continue
        if not (p.parent/pathpart).resolve().exists(): errors.append(f'{rel}: broken local link {target}')
# Deprecated project acronym: allowed only in standard symmetric-multiprocessing contexts.
allow_smp=('SMP (Symmetric Multiprocessing)','symmetric multiprocessing','SMP scheduler','SMP page tables','SMP bring-up','SMP, isolation')
for p in ROOT.rglob('*'):
    if not p.is_file() or p.suffix.lower() not in {'.md','.csv','.yaml','.yml','.mmd','.txt'}: continue
    rel=p.relative_to(ROOT).as_posix()
    if rel.startswith(('sources/original/','sources/extracted/','sources/provenance/','wiki/')): continue
    for i,line in enumerate(p.read_text(encoding='utf-8-sig',errors='replace').splitlines(),1):
        if re.search(r'\bSMP\b',line) and not any(x in line for x in allow_smp): errors.append(f'{rel}:{i}: deprecated SMP project-name usage')
# Task graph and traceability.
def load(path):
    with open(path,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
tasks=load(ROOT/'docs/planning/tasks.csv'); ids={r['task_id'] for r in tasks}; graph=defaultdict(list)
for r in tasks:
    if not r['description'].strip() or not r['acceptance_criteria'].strip(): errors.append(f'{r["task_id"]}: missing description or acceptance criteria')
    if r['parent_id'] and r['parent_id'] not in ids: errors.append(f'{r["task_id"]}: unknown parent {r["parent_id"]}')
    for field in ('dependencies','related_tasks'):
        for x in filter(None,map(str.strip,r[field].split(';'))):
            if x not in ids: errors.append(f'{r["task_id"]}: unknown {field} {x}')
            if field=='dependencies': graph[r['task_id']].append(x)
    for ref in filter(None,map(str.strip,r['related_specs'].split(';'))):
        did,_,a=ref.partition('#')
        if did not in reg: errors.append(f'{r["task_id"]}: unknown spec {did}')
        elif a and a not in anchors(reg[did]): errors.append(f'{r["task_id"]}: missing spec anchor {did}#{a}')
state={}
def visit(n,stack):
    if state.get(n)==1: errors.append('dependency cycle: '+' -> '.join(stack+[n])); return
    if state.get(n)==2:return
    state[n]=1
    for m in graph[n]: visit(m,stack+[n])
    state[n]=2
for n in ids: visit(n,[])
def load_ids(path,field): return {r[field] for r in load(path)}
sources=load_ids(ROOT/'docs/research/source-register.csv','id'); claims=load_ids(ROOT/'docs/research/claim-register.csv','claim_id'); exps=load_ids(ROOT/'docs/research/experiment-register.csv','experiment_id')
for r in tasks:
    for field,valid in [('source_refs',sources),('claim_refs',claims),('experiment_refs',exps)]:
        for x in filter(None,map(str.strip,r[field].split(';'))):
            if x not in valid: errors.append(f'{r["task_id"]}: unknown {field} {x}')
# Import consistency.
def count(path): return len(load(path))
if count(ROOT/'imports/gantt.csv') != len(tasks): errors.append('gantt.csv row count differs from tasks.csv')
if count(ROOT/'imports/linear-issues.csv') != len(tasks): errors.append('linear-issues.csv row count differs from tasks.csv')
if count(ROOT/'imports/github-issues.csv') != len(tasks): errors.append('github-issues.csv row count differs from tasks.csv')
expected_deps=sum(len([x for x in r['dependencies'].split(';') if x.strip()])+len([x for x in r['related_tasks'].split(';') if x.strip()]) for r in tasks)
if count(ROOT/'imports/dependencies.csv') != expected_deps: errors.append('dependencies.csv edge count differs from tasks.csv')
expected_x=sum(sum(len([x for x in r[f].split(';') if x.strip()]) for f in ('related_specs','source_refs','claim_refs','experiment_refs')) for r in tasks)
if count(ROOT/'imports/task-crosslinks.csv') != expected_x: errors.append('task-crosslinks.csv edge count differs from tasks.csv')
# Wiki coverage.
for did in reg:
    if not (ROOT/'wiki'/f'{did}.md').exists(): errors.append(f'missing wiki page for {did}')
print(f'documents={len(reg)} tasks={len(tasks)} sources={len(sources)} claims={len(claims)} experiments={len(exps)} errors={len(errors)} warnings={len(warnings)}')
for x in errors[:500]: print('ERROR',x)
for x in warnings[:200]: print('WARN',x)
sys.exit(1 if errors else 0)
