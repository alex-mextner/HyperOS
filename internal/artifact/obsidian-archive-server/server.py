#!/usr/bin/env python3
"""Serve the HyperOS Obsidian-style planning vault as a local web app."""

from __future__ import annotations

import argparse
import csv
import html
import json
import posixpath
import re
import socketserver
from collections import Counter
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parent
DEFAULT_VAULT = ROOT / "vault"
DEFAULT_PORT = 8787

OBSIDIAN_LINK_RE = re.compile(r"\[\[([^|\]#]+)(?:#([^|\]]+))?(?:\|([^\]]+))?\]\]")
LOCAL_MARKDOWN_ANCHOR_RE = re.compile(r"\[[^\]]+\]\(([^)\s]+\.md)#([^)#\s]+)\)")
HTML_ID_RE = re.compile(r'\sid="([^"]+)"')
INLINE_MD_REPLACEMENTS = (
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\*\*([^*]+)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"\*([^*]+)\*"), r"<em>\1</em>"),
)


@dataclass(frozen=True)
class Vault:
    root: Path

    @property
    def wiki_dir(self) -> Path:
        return self.root / "wiki"

    @property
    def imports_dir(self) -> Path:
        return self.root / "imports"

    @property
    def diagrams_dir(self) -> Path:
        return self.root / "diagrams"

    def wiki_pages(self) -> list[Path]:
        return sorted(self.wiki_dir.glob("*.md"), key=lambda path: path.stem.lower())

    def wiki_page(self, page: str) -> Path | None:
        safe_page = re.sub(r"[^A-Za-z0-9_.-]", "", page).removesuffix(".md")
        path = self.wiki_dir / f"{safe_page}.md"
        if path.is_file() and path.resolve().is_relative_to(self.wiki_dir.resolve()):
            return path
        return None

    def csv_rows(self, name: str) -> list[dict[str, str]]:
        path = self.imports_dir / name
        if not path.is_file():
            return []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.DictReader(handle))

    def diagram_text(self, name: str) -> str | None:
        safe_name = re.sub(r"[^A-Za-z0-9_.-]", "", name)
        path = self.diagrams_dir / safe_name
        if path.is_file() and path.resolve().is_relative_to(self.diagrams_dir.resolve()):
            return path.read_text(encoding="utf-8")
        return None

    def linked_anchors_for(self, page_name: str) -> set[str]:
        anchors: set[str] = set()
        for path in self.wiki_pages():
            text = path.read_text(encoding="utf-8")
            for match in LOCAL_MARKDOWN_ANCHOR_RE.finditer(text):
                target, anchor = match.groups()
                if target == page_name:
                    anchors.add(anchor)
            for match in OBSIDIAN_LINK_RE.finditer(text):
                target, anchor, _label = match.groups()
                if anchor and f"{target.removesuffix('.md')}.md" == page_name:
                    anchors.add(slugify(anchor))
        return anchors


def slugify(value: str) -> str:
    value = re.sub(r"<[^>]+>", "", value).strip().lower()
    value = re.sub(r"[^a-z0-9а-яё]+", "-", value)
    return value.strip("-") or "section"


def page_href(page: str, anchor: str | None = None) -> str:
    href = f"/wiki/{html.escape(page.removesuffix('.md'), quote=True)}"
    if anchor:
        href += f"#{slugify(anchor)}"
    return href


def inline_markdown(text: str) -> str:
    escaped = html.escape(text)

    def replace_link(match: re.Match[str]) -> str:
        page, anchor, label = match.groups()
        label_text = label or page
        if anchor and not label:
            label_text = f"{page}#{anchor}"
        return f'<a href="{page_href(page, anchor)}">{html.escape(label_text)}</a>'

    escaped = OBSIDIAN_LINK_RE.sub(replace_link, escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{m.group(1)}</a>',
        escaped,
    )
    for pattern, replacement in INLINE_MD_REPLACEMENTS:
        escaped = pattern.sub(replacement, escaped)
    return escaped


def strip_frontmatter(markdown: str) -> tuple[dict[str, str], str]:
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return {}, markdown

    metadata: dict[str, str] = {}
    for line in lines[1:closing_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] == '"':
            value = value[1:-1]
        metadata[key.strip()] = value
    return metadata, "\n".join(lines[closing_index + 1 :]).lstrip()


def render_markdown(markdown: str) -> str:
    metadata, body = strip_frontmatter(markdown)
    lines = body.splitlines()
    rendered: list[str] = []
    paragraph: list[str] = []
    unordered_list_open = False
    ordered_list_open = False
    table_rows: list[list[str]] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            rendered.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph = []

    def flush_lists() -> None:
        nonlocal ordered_list_open, unordered_list_open
        if unordered_list_open:
            rendered.append("</ul>")
            unordered_list_open = False
        if ordered_list_open:
            rendered.append("</ol>")
            ordered_list_open = False

    def flush_table() -> None:
        nonlocal table_rows
        if not table_rows:
            return
        rendered.append("<table>")
        for index, row in enumerate(table_rows):
            if index == 1 and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in row):
                continue
            tag = "th" if index == 0 else "td"
            rendered.append("<tr>" + "".join(f"<{tag}>{inline_markdown(cell.strip())}</{tag}>" for cell in row) + "</tr>")
        rendered.append("</table>")
        table_rows = []

    def flush_code() -> None:
        language = html.escape(code_lang)
        code = "\n".join(code_lines)
        if code_lang in {"mermaid", "mmd"}:
            rendered.append(f'<pre class="mermaid">{html.escape(code)}</pre>')
        else:
            rendered.append(f'<pre><code class="language-{language}">{html.escape(code)}</code></pre>')

    if metadata:
        title = metadata.get("title") or metadata.get("id")
        summary = metadata.get("summary")
        if title or summary:
            rendered.append('<section class="frontmatter">')
            if title:
                rendered.append(f"<div><strong>{html.escape(title)}</strong></div>")
            if summary:
                rendered.append(f"<div>{html.escape(summary)}</div>")
            rendered.append("</section>")

    for line in lines:
        if line.startswith("```"):
            if in_code:
                flush_code()
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                flush_paragraph()
                flush_lists()
                flush_table()
                in_code = True
                code_lang = line.strip("`").strip().lower()
            continue
        if in_code:
            code_lines.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_lists()
            flush_table()
            continue

        if line.lstrip().startswith("<a id="):
            flush_paragraph()
            flush_lists()
            flush_table()
            rendered.append(line.strip())
            continue

        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_lists()
            flush_table()
            level = len(heading.group(1))
            title = heading.group(2).strip()
            rendered.append(f'<h{level} id="{slugify(title)}">{inline_markdown(title)}</h{level}>')
            continue

        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            flush_paragraph()
            flush_lists()
            table_rows.append([cell for cell in stripped.strip("|").split("|")])
            continue

        list_item = re.match(r"^\s*[-*]\s+(.+)$", line)
        if list_item:
            flush_paragraph()
            flush_table()
            if ordered_list_open:
                rendered.append("</ol>")
                ordered_list_open = False
            if not unordered_list_open:
                rendered.append("<ul>")
                unordered_list_open = True
            rendered.append(f"<li>{inline_markdown(list_item.group(1))}</li>")
            continue

        ordered_item = re.match(r"^\s*\d+\.\s+(.+)$", line)
        if ordered_item:
            flush_paragraph()
            flush_table()
            if unordered_list_open:
                rendered.append("</ul>")
                unordered_list_open = False
            if not ordered_list_open:
                rendered.append("<ol>")
                ordered_list_open = True
            rendered.append(f"<li>{inline_markdown(ordered_item.group(1))}</li>")
            continue

        paragraph.append(line.strip())

    if in_code:
        flush_code()
    flush_paragraph()
    flush_lists()
    flush_table()
    return "\n".join(rendered)


def task_stats(tasks: list[dict[str, str]]) -> dict[str, int]:
    return {
        "total": len(tasks),
        "p0": sum(1 for task in tasks if task.get("priority") == "P0"),
        "critical": sum(1 for task in tasks if task.get("risk") == "Critical"),
        "planned": sum(1 for task in tasks if task.get("status") == "Planned"),
    }


def mermaid_gantt(vault: Vault) -> str:
    phases = vault.csv_rows("phases.csv")
    milestones = vault.csv_rows("milestones.csv")
    lines = [
        "gantt",
        "    title HyperOS / Agent OS programme roadmap",
        "    dateFormat  YYYY-MM-DD",
        "    axisFormat  %Y-%m",
        "    excludes    weekends",
        "    section Phases",
    ]
    for phase in phases:
        title = phase.get("phase", "Phase")
        start = phase.get("start_date", "")
        end = phase.get("target_date", "")
        if start and end:
            lines.append(f"    {title} :{slugify(title)}, {start}, {end}")
    lines.append("    section Milestones")
    for row in milestones:
        milestone = row.get("milestone", "M")
        title = row.get("title", milestone)
        target = row.get("target_date", "")
        if target:
            lines.append(f"    {milestone} - {title} :milestone, {slugify(milestone)}, {target}, 0d")
    return "\n".join(lines)


def render_task_table(tasks: list[dict[str, str]]) -> str:
    rows = []
    for task in tasks:
        page = "AOS-TASKS"
        task_id = html.escape(task.get("id", ""))
        rows.append(
            "<tr>"
            f'<td><a href="{page_href(page, "task-" + task_id.lower())}">{task_id}</a></td>'
            f"<td>{html.escape(task.get('title', ''))}</td>"
            f"<td>{html.escape(task.get('project', ''))}</td>"
            f"<td>{html.escape(task.get('phase', ''))}</td>"
            f"<td>{html.escape(task.get('milestone', ''))}</td>"
            f"<td>{html.escape(task.get('priority', ''))}</td>"
            f"<td>{html.escape(task.get('risk', ''))}</td>"
            f"<td>{html.escape(task.get('status', ''))}</td>"
            f"<td>{html.escape(task.get('start_date', ''))}</td>"
            f"<td>{html.escape(task.get('end_date', ''))}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def layout(title: str, body: str) -> bytes:
    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · HyperOS Obsidian</title>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
    // The vault is an imported, reviewed, static artifact. Reconsider this if
    // serving untrusted or user-editable Mermaid content.
    mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose', theme: 'neutral' }});
  </script>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fb;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #65758b;
      --line: #d8dee8;
      --accent: #1b6f8f;
      --accent-2: #786018;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: var(--bg); color: var(--text); }}
    a {{ color: var(--accent); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    header {{ position: sticky; top: 0; z-index: 10; display: flex; align-items: center; gap: 18px; min-height: 56px; padding: 0 22px; border-bottom: 1px solid var(--line); background: rgba(255,255,255,.94); backdrop-filter: blur(10px); }}
    header strong {{ font-size: 15px; }}
    nav {{ display: flex; gap: 12px; flex-wrap: wrap; font-size: 14px; }}
    main {{ max-width: 1440px; margin: 0 auto; padding: 22px; }}
    h1, h2, h3 {{ line-height: 1.25; letter-spacing: 0; }}
    h1 {{ font-size: 28px; margin: 0 0 14px; }}
    h2 {{ font-size: 22px; margin-top: 28px; }}
    h3 {{ font-size: 18px; margin-top: 22px; }}
    p, li {{ line-height: 1.6; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }}
    .panel, .metric, .frontmatter {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 16px; }}
    .metric b {{ display: block; font-size: 30px; line-height: 1; margin-bottom: 8px; }}
    .metric span, .muted {{ color: var(--muted); }}
    .content {{ display: grid; grid-template-columns: 280px minmax(0, 1fr); gap: 18px; align-items: start; }}
    .sidebar {{ position: sticky; top: 78px; max-height: calc(100vh - 96px); overflow: auto; }}
    .sidebar a {{ display: block; padding: 7px 8px; border-radius: 6px; color: var(--text); }}
    .sidebar a:hover {{ background: #eef4f7; text-decoration: none; }}
    article {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 22px; overflow: auto; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0; font-size: 14px; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 9px 8px; text-align: left; vertical-align: top; }}
    th {{ color: #314256; background: #f1f4f8; position: sticky; top: 56px; }}
    pre {{ overflow: auto; padding: 14px; border: 1px solid var(--line); border-radius: 8px; background: #f4f6f9; }}
    pre.mermaid {{ background: var(--panel); }}
    .anchor-alias {{ display: block; height: 0; overflow: hidden; position: relative; top: -72px; }}
    input, select {{ min-height: 34px; border: 1px solid var(--line); border-radius: 6px; padding: 6px 9px; background: white; color: var(--text); }}
    .filters {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; margin: 14px 0; }}
    .wide {{ min-width: min(420px, 100%); }}
    @media (max-width: 860px) {{
      header {{ align-items: flex-start; flex-direction: column; padding: 12px 16px; }}
      main {{ padding: 14px; }}
      .content {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static; max-height: 260px; }}
      th {{ position: static; }}
    }}
  </style>
</head>
<body>
  <header>
    <strong>HyperOS Obsidian</strong>
    <nav>
      <a href="/">Dashboard</a>
      <a href="/wiki/Home">Wiki</a>
      <a href="/tasks">Tasks</a>
      <a href="/gantt">Gantt</a>
      <a href="/diagrams">Diagrams</a>
    </nav>
  </header>
  <main>{body}</main>
</body>
</html>"""
    return page.encode("utf-8")


class ObsidianHandler(BaseHTTPRequestHandler):
    vault: Vault

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = unquote(parsed.path)
        if route == "/":
            self.respond_html(self.dashboard())
        elif route == "/wiki":
            self.respond_html(self.wiki_index())
        elif route.startswith("/wiki/"):
            self.respond_html(self.wiki_page(route.removeprefix("/wiki/")))
        elif route == "/tasks":
            self.respond_html(self.tasks_page())
        elif route == "/gantt":
            self.respond_html(self.gantt_page())
        elif route == "/diagrams":
            self.respond_html(self.diagrams_page())
        elif route == "/favicon.ico":
            self.respond_no_content()
        elif route == "/healthz":
            self.respond_json(self.health())
        elif route == "/api/tasks.json":
            self.respond_json(self.vault.csv_rows("gantt.csv"))
        elif route.startswith("/raw/diagrams/"):
            self.respond_text(self.vault.diagram_text(route.removeprefix("/raw/diagrams/")))
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")

    def log_message(self, format: str, *args: object) -> None:
        print(f"{self.address_string()} - {format % args}")

    def respond_html(self, body: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        payload = layout("HyperOS", body)
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def respond_json(self, data: object) -> None:
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def respond_no_content(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def respond_text(self, text: str | None) -> None:
        if text is None:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return
        payload = text.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def dashboard(self) -> str:
        tasks = self.vault.csv_rows("gantt.csv")
        stats = task_stats(tasks)
        projects = self.vault.csv_rows("projects.csv")
        phases = self.vault.csv_rows("phases.csv")
        risks = Counter(task.get("risk", "Unknown") for task in tasks)
        return f"""
<h1>Agent OS Engineering Bible</h1>
<p class="muted">Local Obsidian-style server for the imported HyperOS planning vault.</p>
<section class="grid">
  <div class="metric"><b>{stats['total']}</b><span>canonical tasks</span></div>
  <div class="metric"><b>{stats['p0']}</b><span>P0 tasks</span></div>
  <div class="metric"><b>{stats['critical']}</b><span>critical-risk tasks</span></div>
  <div class="metric"><b>{len(projects)}</b><span>project tracks</span></div>
</section>
<section class="grid" style="margin-top: 16px">
  <div class="panel"><h2>Start</h2><p><a href="/wiki/Home">Open wiki home</a></p><p><a href="/tasks">Browse task catalog</a></p><p><a href="/gantt">Open programme Gantt</a></p></div>
  <div class="panel"><h2>Risk Mix</h2><p>{html.escape(', '.join(f'{k}: {v}' for k, v in sorted(risks.items())))}</p></div>
  <div class="panel"><h2>Phases</h2><p>{html.escape(', '.join(phase.get('phase', '') for phase in phases))}</p></div>
</section>
"""

    def health(self) -> dict[str, str | int]:
        tasks = self.vault.csv_rows("gantt.csv")
        return {
            "status": "ok",
            "wiki_pages": len(self.vault.wiki_pages()),
            "tasks": len(tasks),
            "vault_ok": self.vault.root.is_dir(),
        }

    def wiki_index(self) -> str:
        pages = self.vault.wiki_pages()
        links = "\n".join(f'<a href="/wiki/{html.escape(path.stem)}">{html.escape(path.stem)}</a>' for path in pages)
        return f'<h1>Wiki Pages</h1><section class="content"><aside class="panel sidebar">{links}</aside><article><p>{len(pages)} pages imported from the Obsidian/GitHub Wiki view.</p></article></section>'

    def wiki_page(self, page: str) -> str:
        path = self.vault.wiki_page(posixpath.basename(page))
        if path is None:
            return '<h1>Not found</h1><p>The requested wiki page does not exist.</p>'
        pages = self.vault.wiki_pages()
        links = "\n".join(f'<a href="/wiki/{html.escape(item.stem)}">{html.escape(item.stem)}</a>' for item in pages)
        article = render_markdown(path.read_text(encoding="utf-8"))
        article = self.with_anchor_aliases(path.name, article)
        return f'<section class="content"><aside class="panel sidebar">{links}</aside><article>{article}</article></section>'

    def with_anchor_aliases(self, page_name: str, article: str) -> str:
        existing = set(HTML_ID_RE.findall(article))
        missing = sorted(self.vault.linked_anchors_for(page_name) - existing)
        aliases = "".join(f'<span class="anchor-alias" id="{html.escape(anchor, quote=True)}"></span>' for anchor in missing)
        return aliases + article

    def tasks_page(self) -> str:
        tasks = self.vault.csv_rows("gantt.csv")
        projects = sorted({task.get("project", "") for task in tasks if task.get("project")})
        project_options = "".join(f'<option value="{html.escape(project)}">{html.escape(project)}</option>' for project in projects)
        rows = render_task_table(tasks)
        return f"""
<h1>Tasks</h1>
<p class="muted">Canonical task projection from <code>imports/gantt.csv</code>. Use filters locally in the browser.</p>
<div class="filters">
  <input id="q" class="wide" placeholder="Search title, id, project, phase">
  <select id="project"><option value="">All projects</option>{project_options}</select>
  <select id="priority"><option value="">All priorities</option><option>P0</option><option>P1</option><option>P2</option></select>
  <select id="risk"><option value="">All risks</option><option>Critical</option><option>High</option><option>Medium</option><option>Low</option></select>
</div>
<table id="tasks">
  <thead><tr><th>ID</th><th>Title</th><th>Project</th><th>Phase</th><th>Milestone</th><th>Priority</th><th>Risk</th><th>Status</th><th>Start</th><th>End</th></tr></thead>
  <tbody>{rows}</tbody>
</table>
<script>
const filters = ['q', 'project', 'priority', 'risk'].map(id => document.getElementById(id));
const rows = [...document.querySelectorAll('#tasks tbody tr')];
function applyFilters() {{
  const q = document.getElementById('q').value.toLowerCase();
  const project = document.getElementById('project').value;
  const priority = document.getElementById('priority').value;
  const risk = document.getElementById('risk').value;
  for (const row of rows) {{
    const cells = row.children;
    const text = row.innerText.toLowerCase();
    const visible = (!q || text.includes(q)) && (!project || cells[2].innerText === project) && (!priority || cells[5].innerText === priority) && (!risk || cells[6].innerText === risk);
    row.style.display = visible ? '' : 'none';
  }}
}}
filters.forEach(input => input.addEventListener('input', applyFilters));
</script>
"""

    def gantt_page(self) -> str:
        return f"""
<h1>Programme Gantt</h1>
<p class="muted">Overview generated from <code>imports/phases.csv</code> and <code>imports/milestones.csv</code>. Full task dates remain in <a href="/tasks">Tasks</a>.</p>
<pre class="mermaid">{html.escape(mermaid_gantt(self.vault))}</pre>
"""

    def diagrams_page(self) -> str:
        diagrams = sorted(self.vault.diagrams_dir.glob("*.mmd"))
        blocks = []
        for path in diagrams:
            text = path.read_text(encoding="utf-8")
            blocks.append(f"<h2>{html.escape(path.stem)}</h2><pre class=\"mermaid\">{html.escape(text)}</pre>")
        return "<h1>Diagrams</h1>" + "\n".join(blocks)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the HyperOS Obsidian planning vault.")
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT, help="Path to AgentOS-Engineering-Bible vault")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host; use 0.0.0.0 for LAN/Tailscale access")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Bind port")
    args = parser.parse_args()

    vault_root = args.vault.resolve()
    if not (vault_root / "wiki").is_dir() or not (vault_root / "imports").is_dir():
        raise SystemExit(f"Vault is missing wiki/ or imports/: {vault_root}")

    class Handler(ObsidianHandler):
        vault = Vault(vault_root)

    class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
        allow_reuse_address = True
        daemon_threads = True

    with ReusableThreadingTCPServer((args.host, args.port), Handler) as server:
        print(f"Serving HyperOS Obsidian vault at http://{args.host}:{args.port}")
        print(f"Vault: {vault_root}")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping HyperOS Obsidian server")


if __name__ == "__main__":
    main()
