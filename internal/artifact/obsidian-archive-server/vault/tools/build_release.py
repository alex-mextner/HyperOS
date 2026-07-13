#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import defaultdict, Counter
from datetime import date
import csv, hashlib, json, os, re, shutil, sys, textwrap, zipfile

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
TASKS_CSV = DOCS / 'planning' / 'tasks.csv'
RELEASE_DATE = '2026-07-12'
VERSION = '1.0.0-foundation'


def read_text(p: Path) -> str:
    return p.read_text(encoding='utf-8-sig', errors='replace')


def write_text(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + '\n', encoding='utf-8')


def read_csv(p: Path):
    with p.open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def write_csv(p: Path, rows, fields):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader(); w.writerows(rows)


def split_semis(v: str):
    return [x.strip() for x in (v or '').split(';') if x.strip()]


def sha256(p: Path):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()


def patch_project_name():
    # User-facing project name is Agent OS. Keep SMP only when it means symmetric multiprocessing.
    skip_prefixes=('sources/original/','sources/extracted/','sources/provenance/','wiki/')
    text_ext={'.md','.csv','.yaml','.yml','.mmd','.txt'}
    replacements={
        'SMP Architecture Council':'Agent OS Architecture Council',
        'SMP is organized':'Agent OS is organized',
        'Original SMP microkernel':'Original Agent OS microkernel',
        'The SMP microkernel':'The Agent OS microkernel',
        'SMP does not claim':'Agent OS does not claim',
        'SMP has no requirement':'Agent OS has no requirement',
        'SMP maintains several hardware targets':'Agent OS maintains several hardware targets',
        'Can SMP port cleanly':'Can Agent OS port cleanly',
        'SMP therefore runs':'Agent OS therefore runs',
        'Before requesting quotations, SMP must have':'Before requesting quotations, Agent OS must have',
        'with SMP native services':'with native Agent OS services',
        'native SMP reaches':'native Agent OS reaches',
        'Native SMP reaches':'Native Agent OS reaches',
        'Boot SMP to structured console':'Boot Agent OS to structured console',
        'needed for SMP':'needed for Agent OS',
        'in SMP':'in Agent OS',
        'for SMP':'for Agent OS',
        'to SMP':'to Agent OS',
        'SMP controls':'Agent OS controls',
        'SMP image manifest':'Agent OS image manifest',
        'SMP handoff record':'Agent OS handoff record',
        'SMP codec':'Agent OS codec',
        'SMP GPU service':'Agent OS GPU service',
        'SMP resource and service contracts':'Agent OS resource and service contracts',
        'SMP resource records':'Agent OS resource records',
        'SMP factory service':'Agent OS factory service',
        'SMP may cache':'Agent OS may cache',
        'SMP IDL':'Agent OS IDL',
        'SMP cellular':'Agent OS cellular',
        'SMP key':'Agent OS key',
        'SMP state machine':'Agent OS state machine',
        'SMP page tables':'Agent OS page tables',
        'SMP hardware-service':'Agent OS hardware-service',
        'SMP types':'Agent OS types',
        'SMP contracts':'Agent OS contracts',
        'SMP adapter':'Agent OS adapter',
        'SMP driver':'Agent OS driver',
        'SMP support':'Agent OS support',
        'SMP versions it':'Agent OS versions it',
        'SMP can design':'Agent OS can design',
        'SMP may need':'Agent OS may need',
        'SMP may be the product manufacturer':'Agent OS may be the product manufacturer',
        'SMP sends':'Agent OS sends',
        'SMP must still define':'Agent OS must still define',
        'SMP captures':'Agent OS captures',
        'explicit SMP capabilities':'explicit Agent OS capabilities',
        'but SMP normalizes':'but Agent OS normalizes',
        'board boots SMP':'board boots Agent OS',
        'In SMP, HAL':'In Agent OS, HAL',
        'native SMP MBIM':'native Agent OS MBIM',
        'SMP requires independent':'Agent OS requires independent',
        'native SMP,Hypothesis':'native Agent OS,Hypothesis',
        'portable SMP,Bounded':'portable Agent OS,Bounded',
        'reaches SMP early diagnostics':'reaches Agent OS early diagnostics',
        'claim that SMP inherits':'claim that Agent OS inherits',
        'Continue internal SMP designation without public brand launch':'Continue using the internal Agent OS working name without public brand launch',
    }
    for p in ROOT.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in text_ext: continue
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(skip_prefixes): continue
        t=read_text(p); old=t
        for a,b in replacements.items(): t=t.replace(a,b)
        # The glossary technical term must not imply a project acronym.
        t=t.replace('This meaning is distinct from the project working acronym.',
                    'This is the standard symmetric-multiprocessing meaning; it is not a project name or product acronym.')
        # Generic product uses that remain after phrase replacements.
        t=re.sub(r'\bSMP\b(?= (?:ABI|board|camera|command|component|device|firmware|image|implementation|kernel|modem|native|OS|platform|product|protocol|runtime|service|software|stack|system|target|toolchain))', 'Agent OS', t)
        if t!=old: write_text(p,t)


def dedupe_markdown_table_rows():
    for p in ROOT.rglob('*.md'):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(('sources/original/','sources/extracted/','wiki/')): continue
        lines=read_text(p).splitlines()
        out=[]; seen=set(); in_table=False
        for line in lines:
            if line.startswith('|'):
                if re.match(r'^\|\s*:?-+', line):
                    out.append(line); in_table=True; continue
                # Dedupe exact data rows within a document, but keep headers.
                if in_table and line in seen: continue
                if in_table: seen.add(line)
                out.append(line)
            else:
                if line.strip(): in_table=False; seen=set()
                out.append(line)
        write_text(p,'\n'.join(out))


def ensure_source_rows():
    p=DOCS/'research/source-register.csv'
    rows=read_csv(p); fields=list(rows[0].keys())
    existing={r['id'] for r in rows}
    digests=[]
    for f in sorted((ROOT/'sources/normalized').glob('*.md')):
        t=read_text(f)
        mid=re.search(r'^id:\s*["\']?([^"\'\n]+)',t,re.M)
        mt=re.search(r'^title:\s*["\']?([^"\'\n]+)',t,re.M)
        if not mid: continue
        did=mid.group(1).strip(); title=mt.group(1).strip() if mt else f.stem
        if did not in existing:
            digests.append({'id':did,'title':title,'url':f.relative_to(ROOT).as_posix(),
                'authority':'Project normalized source','domain':'Source corpus','access':'Bundled',
                'note':'English digest with explicit disposition; original material remains immutable in sources/original.'})
    rows.extend(digests)
    # deterministic order: public SRC first, then AOS-SRC digests
    rows.sort(key=lambda r:(0 if r['id'].startswith('SRC-') else 1,r['id']))
    write_csv(p,rows,fields)


def fix_links_and_tocs():
    repl={
      'research/RES-002-hardware-source-register.md':'research/source-register.md',
      'research/RES-003-claim-verification-register.md':'research/claim-register.md',
      'research/RES-004-experiment-catalog.md':'research/experiment-register.md',
      '../research/RES-003-claim-verification-register.md':'../research/claim-register.md',
      '../research/RES-004-experiment-catalog.md':'../research/experiment-register.md',
      'RES-002-hardware-source-register.md':'source-register.md',
      '../MANIFEST.md':'../MANIFEST.md',
    }
    for p in ROOT.rglob('*.md'):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(('sources/original/','sources/extracted/','wiki/')): continue
        t=read_text(p); old=t
        for a,b in repl.items(): t=t.replace(a,b)
        if t!=old: write_text(p,t)
    nidx=ROOT/'sources/normalized/INDEX.md'
    t=read_text(nidx)
    if '## Table of Contents' not in t:
        marker='# Normalized Source Digest Index\n'
        insert='''# Normalized Source Digest Index\n\n## Table of Contents\n\n- [Normalized Source Digests](#normalized-source-digests)\n- [Authority and Use](#authority-and-use)\n\n<a id="normalized-source-digests"></a>\n\n## Normalized Source Digests\n'''
        t=t.replace(marker,insert,1)
        if '<a id="authority-and-use"></a>' not in t:
            t += '''\n<a id="authority-and-use"></a>\n\n## Authority and Use\n\nNormalized digests are navigational and analytical aids. Normative requirements live under `docs/`; original files remain immutable evidence under `sources/original/`.\n'''
        write_text(nidx,t)


def frontmatter(doc_id,title,status,summary):
    return f'''---\nid: "{doc_id}"\ntitle: "{title}"\nstatus: "{status}"\nversion: "{VERSION}"\nbaseline_date: "2026-07-13"\nowners: "Agent OS Architecture Council"\naudience: "Engineering, product, security, legal, programme, partner, and community readers"\nsummary: "{summary}"\n---\n'''


def generate_register_markdown():
    configs=[
      ('source-register.csv','source-register.md','AOS-RES-002','Hardware Evidence and Source Register','Primary and project sources used to support architecture, hardware, legal, product, and programme decisions.','source-register',['id','title','authority','domain','url']),
      ('claim-register.csv','claim-register.md','AOS-RES-003','Claim Verification Register','Claims are classified as decisions, supported findings, hypotheses, bounded inferences, contradictions, or unresolved questions.','claim-register',['claim_id','claim','state','finding','normative_ref','experiment','gate']),
      ('experiment-register.csv','experiment-register.md','AOS-RES-004','Experiment and Evidence Catalog','Experiments turn material uncertainty into bounded, reproducible evidence and explicit decision gates.','experiment-catalog',['experiment_id','title','hypothesis','owner_task','evidence','gate']),
    ]
    base=DOCS/'research'
    for csvname,mdname,did,title,summary,anchor,cols in configs:
        rows=read_csv(base/csvname)
        extra_toc=[]; extra_sections=[]
        if did=='AOS-RES-003':
            extra_toc=['- [Claim States](#claim-states)','- [Camera Claims](#camera-claims)']
            extra_sections=['<a id="claim-states"></a>','','## Claim States','','Each claim state distinguishes normative decisions, supported findings, hypotheses, bounded inferences, contradictions, and unresolved questions. State changes require evidence and downstream review.','', '<a id="camera-claims"></a>','','## Camera Claims','','Camera claims must name the target, optics, sensor, firmware, controls, capture conditions, metrics, reference, uncertainty, and acceptance gate; brand or sensor identity alone is not evidence of image quality.','']
        elif did=='AOS-RES-004':
            extra_toc=['- [Evidence Integrity](#evidence-integrity)']
            extra_sections=['<a id="evidence-integrity"></a>','','## Evidence Integrity','','An evidence bundle identifies target and revision, firmware, source commit, toolchain, configuration, seed, time, procedure, expected and actual results, raw artifacts, checksums, access class, and reviewer. Redaction must preserve correlation without leaking protected content.','']
        lines=[frontmatter(did,title,'Generated evidence view',summary),f'# {title}','', '## Table of Contents','', '- [Purpose](#purpose)']+extra_toc+[f'- [Register](#{anchor})','- [Operating Rule](#operating-rule)','', '<a id="purpose"></a>','', '## Purpose','',summary,'']+extra_sections+[f'<a id="{anchor}"></a>','', '## Register','', '| '+' | '.join(cols)+' |','| '+' | '.join(['---']*len(cols))+' |']
        for r in rows:
            vals=[]
            for c in cols:
                v=(r.get(c,'') or '').replace('|','\\|').replace('\n',' ')
                vals.append(v)
            lines.append('| '+' | '.join(vals)+' |')
        lines += ['', '<a id="operating-rule"></a>','', '## Operating Rule','', 'Every material use must preserve the record ID and link the claim, experiment, task, or normative specification that depends on it. Generated Markdown is a reviewable view; the CSV is the canonical machine-readable register.']
        write_text(base/mdname,'\n'.join(lines))


def generate_tasks_and_imports():
    tasks=read_csv(TASKS_CSV); fields=list(tasks[0].keys())
    # Project naming in canonical task data.
    for r in tasks:
        for k,v in list(r.items()):
            if isinstance(v,str):
                v=v.replace('Boot SMP to structured console','Boot Agent OS to structured console')
                if k == 'workstream' and v == 'SMP': v = 'Symmetric Multiprocessing'
                v=v.replace(' for SMP',' for Agent OS').replace(' to SMP',' to Agent OS').replace(' native SMP',' native Agent OS')
                r[k]=v
    write_csv(TASKS_CSV,tasks,fields)

    tracks=defaultdict(list)
    for r in tasks: tracks[r['track']].append(r)
    lines=[frontmatter('AOS-TASKS','Canonical Task Catalog','Generated planning view','Human-readable projection of the canonical task CSV, including descriptions, acceptance criteria, dependencies, evidence, and traceability.'),
      '# Canonical Task Catalog','', '## Table of Contents','', '- [Catalog Rules](#catalog-rules)','- [Track Index](#track-index)','- [Task Catalog](#task-catalog)','', '<a id="catalog-rules"></a>','', '## Catalog Rules','',
      '`docs/planning/tasks.csv` is canonical. This Markdown view is generated from it. Dependencies use task IDs; specifications use stable `AOS-*#anchor` references; source, claim, and experiment IDs resolve through their registers.','',
      '<a id="track-index"></a>','', '## Track Index','']
    for tr in sorted(tracks): lines.append(f'- [{tr}](#track-{tr.lower()}) — {len(tracks[tr])} tasks')
    lines += ['', '<a id="task-catalog"></a>','', '## Task Catalog','']
    for tr in sorted(tracks):
        lines += [f'<a id="track-{tr.lower()}"></a>','',f'### {tr}','']
        for r in tracks[tr]:
            anchor='task-'+r['task_id'].lower()
            lines += [f'<a id="{anchor}"></a>','',f'#### {r["task_id"]} — {r["title"]}','',
              f'**Type / priority / status:** {r["issue_type"]} · {r["priority"]} · {r["status"]}',
              f'**Owner / workstream:** {r["owner_role"]} · {r["workstream"]}',
              f'**Schedule:** {r["start_date"]} → {r["target_date"]} · {r["estimate_days"]} estimated days · {r["milestone"]}',
              f'**Parent:** {r["parent_id"] or "none"}',
              f'**Dependencies:** {r["dependencies"] or "none"}',
              f'**Related tasks:** {r["related_tasks"] or "none"}','',
              r['description'],'', '**Acceptance criteria**','']
            for ac in split_semis(r['acceptance_criteria']): lines.append(f'- {ac}')
            lines += ['',f'**Deliverables:** {r["deliverables"]}',f'**Verification:** {r["verification"]}',f'**Evidence:** {r["evidence"]}',
              f'**Traceability:** specs: {r["related_specs"] or "none"}; sources: {r["source_refs"] or "none"}; claims: {r["claim_refs"] or "none"}; experiments: {r["experiment_refs"] or "none"}',
              f'**Phase / volume:** {r["implementation_phase"]} · {r["documentation_volume"]}',f'**Specialist review:** {r["review_required"] or "none"}','']
    write_text(DOCS/'planning/TASKS.md','\n'.join(lines))

    imp=ROOT/'imports'; imp.mkdir(exist_ok=True)
    # Dependencies and crosslinks.
    deps=[]; xlinks=[]
    for r in tasks:
        for x in split_semis(r['dependencies']): deps.append({'from_id':r['task_id'],'to_id':x,'relation':'blocked_by'})
        for x in split_semis(r['related_tasks']): deps.append({'from_id':r['task_id'],'to_id':x,'relation':'related'})
        for field,typ in [('related_specs','spec'),('source_refs','source'),('claim_refs','claim'),('experiment_refs','experiment')]:
            for x in split_semis(r[field]): xlinks.append({'task_id':r['task_id'],'reference_type':typ,'reference':x})
    write_csv(imp/'dependencies.csv',deps,['from_id','to_id','relation'])
    write_csv(imp/'task-crosslinks.csv',xlinks,['task_id','reference_type','reference'])

    # Gantt.
    gantt=[]
    for r in tasks:
        gantt.append({'id':r['task_id'],'parent_id':r['parent_id'],'title':r['title'],'type':r['issue_type'],'project':r['linear_project'],'track':r['track'],'phase':r['implementation_phase'],'volume':r['documentation_volume'],'milestone':r['milestone'],'start_date':r['start_date'],'end_date':r['target_date'],'duration_weeks':r['duration_weeks'],'dependencies':r['dependencies'],'priority':r['priority'],'risk':r['risk'],'status':r['status']})
    write_csv(imp/'gantt.csv',gantt,list(gantt[0].keys()))

    # Projects.
    pg=defaultdict(list)
    for r in tasks: pg[r['linear_project']].append(r)
    projects=[]
    for i,(name,rs) in enumerate(sorted(pg.items()),1):
        projects.append({'project_key':f'PRJ-{i:02d}','project_name':name,'tracks':';'.join(sorted({x['track'] for x in rs})),'description':f'Contains {len(rs)} canonical tasks across '+', '.join(sorted({x['workstream'] for x in rs})[:8])+'.','status':'Planned'})
    write_csv(imp/'projects.csv',projects,list(projects[0].keys()))

    # Milestones, phases, volumes.
    def grouped(field, keyname, purpose_map=None):
        g=defaultdict(list)
        for r in tasks: g[r[field]].append(r)
        out=[]
        for k,rs in sorted(g.items()):
            starts=[x['start_date'] for x in rs if x['start_date']]; ends=[x['target_date'] for x in rs if x['target_date']]
            row={keyname:k,'start_date':min(starts) if starts else '','target_date':max(ends) if ends else '','task_count':len(rs)}
            if purpose_map is not None: row['purpose']=purpose_map.get(k,f'Execution scope for {k}.')
            out.append(row)
        return out
    mg=defaultdict(list)
    for r in tasks: mg[r['milestone']].append(r)
    milestones=[]
    for k,rs in sorted(mg.items()):
        milestones.append({'milestone':k,'title':f'{k} evidence gate','start_date':min(x['start_date'] for x in rs),'target_date':max(x['target_date'] for x in rs),'task_count':len(rs),'acceptance':'All P0 blockers closed or explicitly waived; evidence bundle linked; dependent tracks reviewed.'})
    write_csv(imp/'milestones.csv',milestones,list(milestones[0].keys()))
    phase_purpose={f'Phase {i}':p for i,p in enumerate(['Source intake, decisions, governance, and reproducible baseline','Prior-art research, proof-checking, legal routing, and bounded experiments','Portable architecture, IDL, device contracts, and threat model','Normative kernel, system, product, and hardware specifications','Rust toolchain, coding, unsafe, verification, and CI standards','Workspace, QEMU, generators, mocks, and test scaffold','Microkernel and portable vertical slice','Physical boards, camera/cellular labs, and Pixel evidence tracks','Review, release, community launch, and partner transition'])}
    phases=grouped('implementation_phase','phase',phase_purpose)
    write_csv(imp/'phases.csv',phases,['phase','start_date','target_date','task_count','purpose'])
    vol_purpose={f'Volume {i:02d}':f'Thematic documentation and execution coverage for Volume {i:02d}.' for i in range(1,11)}
    vg=defaultdict(list)
    for r in tasks: vg[r['documentation_volume']].append(r)
    volumes=[]
    for k,rs in sorted(vg.items()): volumes.append({'volume':k,'task_count':len(rs),'tracks':';'.join(sorted({x['track'] for x in rs})),'purpose':vol_purpose.get(k,f'Documentation scope for {k}.')})
    write_csv(imp/'volumes.csv',volumes,['volume','task_count','tracks','purpose'])

    # Linear/GitHub staging files.
    lin=[]; gh=[]
    pmap={p['project_name']:p['project_key'] for p in projects}
    for r in tasks:
        body=r['description']+'\n\n## Acceptance criteria\n'+'\n'.join('- '+x for x in split_semis(r['acceptance_criteria']))+f'\n\n## Deliverables\n{r["deliverables"]}\n\n## Verification\n{r["verification"]}\n\n## Evidence\n{r["evidence"]}\n\n## Traceability\nSpecs: {r["related_specs"] or "none"}\nSources: {r["source_refs"] or "none"}\nClaims: {r["claim_refs"] or "none"}\nExperiments: {r["experiment_refs"] or "none"}'
        lin.append({'External ID':r['task_id'],'Title':r['title'],'Description':body,'Status':r['status'],'Priority':r['priority'],'Assignee':'','Project':r['linear_project'],'Team':r['linear_team'],'Labels':r['github_labels'].replace(';',','),'Parent External ID':r['parent_id'],'Start Date':r['start_date'],'Due Date':r['target_date'],'Milestone':r['milestone'],'Estimate Days':r['estimate_days']})
        gh.append({'title':r['title'],'body':body,'labels':r['github_labels'].replace(';',','),'milestone':r['milestone'],'project':pmap.get(r['linear_project'],r['linear_project']),'external_id':r['task_id'],'start_date':r['start_date'],'target_date':r['target_date']})
    write_csv(imp/'linear-issues.csv',lin,list(lin[0].keys()))
    write_csv(imp/'github-issues.csv',gh,list(gh[0].keys()))

    manifest={'schema_version':'1.0','canonical_task_file':'docs/planning/tasks.csv','import_order':['projects.csv','milestones.csv','linear-issues.csv or github-issues.csv','dependencies.csv','task-crosslinks.csv'],'identity_key':'task_id / External ID / external_id','reconciliation_required':True,'notes':['CSV import capabilities vary by tracker. Preserve canonical IDs and apply dependencies/crosslinks through API or agent reconciliation.','Never treat tracker-only edits as canonical until exported and reconciled into tasks.csv.']}
    write_text(imp/'agent-import-manifest.yaml', '\n'.join(['schema_version: "1.0"','canonical_task_file: "docs/planning/tasks.csv"','identity_key: "task_id"','reconciliation_required: true','import_order:','  - projects.csv','  - milestones.csv','  - linear-issues.csv or github-issues.csv','  - dependencies.csv','  - task-crosslinks.csv','rules:','  - Preserve task IDs as external identities.','  - Create parents before children.','  - Apply blocked-by and related edges after issue creation.','  - Reconcile dates, labels, milestones, and cross-links after import.','  - Report unresolved references and do not silently drop them.']))


def extract_metadata(p: Path):
    t=read_text(p)
    mid=re.search(r'^id:\s*["\']?([^"\'\n]+)',t,re.M)
    mt=re.search(r'^title:\s*["\']?([^"\'\n]+)',t,re.M)
    return (mid.group(1).strip() if mid else None, mt.group(1).strip() if mt else p.stem)


def canonical_docs():
    out=[]
    for p in ROOT.rglob('*.md'):
        rel=p.relative_to(ROOT).as_posix()
        if rel.startswith(('wiki/','sources/original/','sources/extracted/')): continue
        did,title=extract_metadata(p)
        if did: out.append((did,p,title))
    return sorted(out)


def generate_manifest(pre_validation='pending'):
    docs=canonical_docs(); tasks=read_csv(TASKS_CSV); sources=read_csv(DOCS/'research/source-register.csv'); claims=read_csv(DOCS/'research/claim-register.csv'); exps=read_csv(DOCS/'research/experiment-register.csv')
    sections=Counter(p.relative_to(ROOT).parts[1] if p.relative_to(ROOT).parts[0]=='docs' and len(p.relative_to(ROOT).parts)>1 else p.relative_to(ROOT).parts[0] for _,p,_ in docs)
    text=frontmatter('AOS-MANIFEST','Release Manifest','Foundation release manifest','Inventory, validation state, reproducibility rules, canonical datasets, and release boundaries for the Agent OS Engineering Bible.')+f'''\n# Release Manifest\n\n## Table of Contents\n\n- [Release Identity](#release-identity)\n- [Release Scope](#release-scope)\n- [Canonical Artifacts](#canonical-artifacts)\n- [Inventory](#inventory)\n- [Validation Status](#validation-status)\n- [Rebuild and Publication](#rebuild-and-publication)\n- [Limitations](#limitations)\n\n<a id="release-identity"></a>\n\n## Release Identity\n\n- **Edition:** Foundation Release\n- **Version:** `{VERSION}`\n- **Release date:** `{RELEASE_DATE}`\n- **Working name:** Agent OS; not trademark-cleared\n- **Stable namespace:** `AOS-*`\n\n<a id="release-scope"></a>\n\n## Release Scope\n\nThis release is a normative planning and research foundation for an independently implemented Rust-first microkernel, portable system and product layers, parallel hardware tracks, and a future partner/custom-device route. It is not a claim that the operating system, drivers, Pixel 9 support, camera stack, cellular stack, certifications, or production device already exist.\n\nHistorical Fuchsia-oriented and Android/Linux-oriented material is retained as immutable prior art and provenance. Current requirements are defined by canonical `AOS-*` documents and ADRs.\n\n<a id="canonical-artifacts"></a>\n\n## Canonical Artifacts\n\n| Artifact | Role |\n| --- | --- |\n| `docs/**/*.md` | Normative and research documentation |\n| `docs/planning/tasks.csv` | Canonical task graph |\n| `docs/research/source-register.csv` | Source registry |\n| `docs/research/claim-register.csv` | Claim state registry |\n| `docs/research/experiment-register.csv` | Experiment/evidence registry |\n| `docs/hardware/procurement.csv` | Procurement planning data |\n| `docs/legal/contacts.csv` | Contact acquisition plan |\n| `sources/original/` | Immutable supplied archives |\n| `sources/normalized/` | English source digests and dispositions |\n| `imports/` | Derived tracker-neutral and tracker staging views |\n| `wiki/` | Derived flat GitHub Wiki view |\n\n<a id="inventory"></a>\n\n## Inventory\n\n- **Registered Markdown documents:** {len(docs)}\n- **Canonical tasks:** {len(tasks)}\n- **Registered sources:** {len(sources)}\n- **Claim records:** {len(claims)}\n- **Experiment records:** {len(exps)}\n- **Wiki pages:** generated during release build\n- **File checksums:** `validation/CHECKSUMS.sha256`\n- **Machine-readable file inventory:** `validation/FILE-MANIFEST.csv`\n\n<a id="validation-status"></a>\n\n## Validation Status\n\n**Status:** {pre_validation}.\n\nThe release validator checks document IDs, explicit anchors, cross-references, local Markdown links, task parents and dependency cycles, task-to-spec anchors, source/claim/experiment IDs, import row consistency, Wiki coverage, language constraints outside immutable sources, and deprecated project-name usage. The authoritative report is `validation/VALIDATION.md`.\n\n<a id="rebuild-and-publication"></a>\n\n## Rebuild and Publication\n\nRun:\n\n```bash\npython3 tools/build_release.py --rebuild\npython3 tools/validate.py\n```\n\nThe build regenerates evidence views, task projections, imports, link map, Wiki, validation inventory, and checksums from canonical files. GitHub/Linear imports require post-import reconciliation because tracker CSV importers do not preserve every dependency and cross-link type.\n\n<a id="limitations"></a>\n\n## Limitations\n\nThis edition contains researched specifications and executable planning data, but many engineering claims remain hypotheses pending experiments or specialist review. Legal documents are issue-spotting and process specifications, not jurisdiction-specific legal advice. Cost ranges are planning estimates, not supplier quotations. Hardware candidates must pass SKU, documentation, recovery, licensing, availability, and unique-evidence gates before purchase.\n'''
    write_text(ROOT/'MANIFEST.md',text)


def generate_link_map_and_wiki():
    docs=canonical_docs()
    fields=['id','path','title','wiki_file']
    rows=[]; by_rel={}; by_id={}
    for did,p,title in docs:
        rel=p.relative_to(ROOT).as_posix(); row={'id':did,'path':rel,'title':title,'wiki_file':did+'.md'}
        rows.append(row); by_rel[rel]=did; by_id[did]=row
    write_csv(DOCS/'_meta/link-map.csv',rows,fields)
    wiki=ROOT/'wiki'
    if wiki.exists(): shutil.rmtree(wiki)
    wiki.mkdir()
    xref_wiki=re.compile(r'\[\[([^\]|#]+)(?:#([^\]|]+))?(?:\|([^\]]+))?\]\]')
    md_xref=re.compile(r'\[([^\]]+)\]\(([^)]+)\)\s*<!--\s*xref:([^\s>]+)\s*-->')
    md_link=re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    for did,p,title in docs:
        text=read_text(p)
        def mx(m):
            label,target,xid=m.group(1),m.group(2),m.group(3)
            base,sep,anch=xid.partition('#')
            return f'[{label}]({base}.md'+(f'#{anch}' if anch else '')+')'
        text=md_xref.sub(mx,text)
        def wx(m):
            base,anch,label=m.group(1),m.group(2),m.group(3)
            label=label or (base+(f'#{anch}' if anch else ''))
            return f'[{label}]({base}.md'+(f'#{anch}' if anch else '')+')'
        text=xref_wiki.sub(wx,text)
        def ml(m):
            label,target=m.group(1),m.group(2)
            if re.match(r'^(https?://|mailto:|#)',target): return m.group(0)
            pathpart,sep,anch=target.partition('#')
            resolved=(p.parent/pathpart).resolve()
            try: rel=resolved.relative_to(ROOT).as_posix()
            except Exception: return m.group(0)
            tid=by_rel.get(rel)
            if not tid: return m.group(0)
            return f'[{label}]({tid}.md'+(f'#{anch}' if anch else '')+')'
        text=md_link.sub(ml,text)
        write_text(wiki/(did+'.md'),text)
    # GitHub Wiki conventional pages.
    readme_id='AOS-README'
    if readme_id in by_id:
        shutil.copyfile(wiki/(readme_id+'.md'),wiki/'Home.md')
    groups=defaultdict(list)
    for r in rows:
        prefix=r['id'].split('-',2)[:2]
        groups['-'.join(prefix)].append(r)
    side=['# Agent OS Engineering Bible','', '[Home](Home.md)','', '## Core','', '- [Executive Briefing](AOS-BRIEF.md)','- [Documentation Index](AOS-INDEX.md)','- [Release Manifest](AOS-MANIFEST.md)','- [Roadmap](AOS-PLAN-002.md)','- [Task Catalog](AOS-TASKS.md)','- [Glossary](AOS-GLOSSARY.md)','', '## Collections','']
    for g,rs in sorted(groups.items()):
        if len(rs)>1: side.append(f'- **{g}** — {len(rs)} pages')
    write_text(wiki/'_Sidebar.md','\n'.join(side))


def write_validator():
    # Kept as a standalone file so the packaged release can be checked without the build script.
    code=r'''#!/usr/bin/env python3
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
'''
    write_text(ROOT/'tools/validate.py',code)
    os.chmod(ROOT/'tools/validate.py',0o755)


def build_inventory(validation_status='PASS'):
    val=ROOT/'validation'; val.mkdir(exist_ok=True)
    exclude={'validation/CHECKSUMS.sha256','validation/FILE-MANIFEST.csv','validation/VALIDATION.md'}
    files=[]
    for p in sorted(ROOT.rglob('*')):
        if not p.is_file(): continue
        rel=p.relative_to(ROOT).as_posix()
        if rel in exclude: continue
        files.append({'path':rel,'size_bytes':p.stat().st_size,'sha256':sha256(p)})
    write_csv(val/'FILE-MANIFEST.csv',files,['path','size_bytes','sha256'])
    write_text(val/'CHECKSUMS.sha256','\n'.join(f"{r['sha256']}  {r['path']}" for r in files))
    counts=Counter(Path(r['path']).parts[0] for r in files)
    report=frontmatter('AOS-VALIDATION','Release Validation Report','Generated release evidence','Validation scope, counts, integrity results, and known limitations for the packaged foundation release.')+f'''\n# Release Validation Report\n\n## Table of Contents\n\n- [Result](#result)\n- [Validated Invariants](#validated-invariants)\n- [Inventory](#inventory)\n- [Known Limitations](#known-limitations)\n\n<a id="result"></a>\n\n## Result\n\n**{validation_status}** — generated on {RELEASE_DATE}.\n\n<a id="validated-invariants"></a>\n\n## Validated Invariants\n\n- Unique canonical document IDs and stable explicit anchors.\n- Resolved canonical document-and-anchor references and bundled local Markdown links.\n- Table of contents in every canonical document except the repository README entry page.\n- Task parents, references, dependency edges, and acyclic dependency graph.\n- Task-to-spec anchors and source/claim/experiment identifiers.\n- Row consistency for Gantt, Linear, GitHub, dependency, and cross-link exports.\n- Flat Wiki page coverage for every canonical document.\n- Deprecated project-name use of `SMP` removed; the term remains only for symmetric multiprocessing.\n- SHA-256 inventory for packaged release files.\n\n<a id="inventory"></a>\n\n## Inventory\n\n- Files covered by checksum inventory: {len(files)}\n- Canonical registered documents: {len(canonical_docs())}\n- Canonical tasks: {len(read_csv(TASKS_CSV))}\n- Sources: {len(read_csv(DOCS/'research/source-register.csv'))}\n- Claims: {len(read_csv(DOCS/'research/claim-register.csv'))}\n- Experiments: {len(read_csv(DOCS/'research/experiment-register.csv'))}\n- Top-level file groups: {', '.join(f'{k}={v}' for k,v in sorted(counts.items()))}\n\n<a id="known-limitations"></a>\n\n## Known Limitations\n\nStructural validation does not substitute for implementation evidence, independent security review, jurisdiction-specific legal advice, carrier certification, camera tuning, silicon documentation, or production supplier quotations. Documents explicitly label hypotheses, experiments, review gates, and stop criteria where these remain unresolved.\n'''
    write_text(val/'VALIDATION.md',report)


def rebuild():
    patch_project_name()
    dedupe_markdown_table_rows()
    ensure_source_rows()
    fix_links_and_tocs()
    generate_register_markdown()
    generate_tasks_and_imports()
    generate_manifest('pending final validator run')
    write_validator()
    generate_link_map_and_wiki()
    # Validation needs wiki and manifest.
    import subprocess
    result=subprocess.run([sys.executable,str(ROOT/'tools/validate.py')],cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        print(result.stdout); print(result.stderr,file=sys.stderr); raise SystemExit(result.returncode)
    generate_manifest('PASS — zero blocking errors in the packaged structural and traceability validator')
    generate_link_map_and_wiki()
    # Validate again after final manifest/wiki.
    result=subprocess.run([sys.executable,str(ROOT/'tools/validate.py')],cwd=ROOT,text=True,capture_output=True)
    if result.returncode:
        print(result.stdout); print(result.stderr,file=sys.stderr); raise SystemExit(result.returncode)
    build_inventory('PASS')
    # Re-run once more; validation report is now a registered doc and requires a wiki page.
    generate_link_map_and_wiki()
    result=subprocess.run([sys.executable,str(ROOT/'tools/validate.py')],cwd=ROOT,text=True,capture_output=True)
    print(result.stdout,end='')
    if result.returncode: raise SystemExit(result.returncode)
    build_inventory('PASS')

if __name__=='__main__':
    rebuild()
