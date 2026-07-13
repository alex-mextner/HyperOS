# HyperOS Obsidian Server

This artifact serves the imported `AgentOS-Engineering-Bible` vault from the
Telegram archive `599469301.zip`.

Run the local server:

```bash
python3 internal/artifact/obsidian-archive-server/server.py
```

Open:

- `http://127.0.0.1:8787/` — dashboard
- `http://127.0.0.1:8787/wiki/Home` — wiki home
- `http://127.0.0.1:8787/tasks` — searchable task table
- `http://127.0.0.1:8787/gantt` — Mermaid programme Gantt
- `http://127.0.0.1:8787/diagrams` — Mermaid architecture diagrams

For phone access over Tailscale or LAN:

```bash
python3 internal/artifact/obsidian-archive-server/server.py --host 0.0.0.0
```

The server uses only the Python standard library. Mermaid diagrams render in the
browser through the Mermaid CDN.
