import importlib.util
import sys
import unittest
from pathlib import Path


SERVER_PATH = Path(__file__).resolve().parents[1] / "server.py"
SPEC = importlib.util.spec_from_file_location("obsidian_server", SERVER_PATH)
server = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = server
SPEC.loader.exec_module(server)


class ServerRenderingTests(unittest.TestCase):
    def test_render_markdown_handles_frontmatter_lists_and_tables(self):
        rendered = server.render_markdown(
            """---
title: "Example"
---
# Start

1. First
2. Second

| A | B |
| --- | --- |
| one | two |
"""
        )

        self.assertIn("<h1", rendered)
        self.assertIn("<ol>", rendered)
        self.assertIn("<li>First</li>", rendered)
        self.assertIn("<table>", rendered)
        self.assertIn("<td>one</td>", rendered)

    def test_render_markdown_handles_obsidian_links_and_mermaid(self):
        rendered = server.render_markdown(
            """See [[AOS-TASKS#task-catalog|tasks]].

```mermaid
gantt
    title Demo
```
"""
        )

        self.assertIn('<a href="/wiki/AOS-TASKS#task-catalog">tasks</a>', rendered)
        self.assertIn('<pre class="mermaid">', rendered)

    def test_strip_frontmatter_requires_fenced_lines(self):
        metadata, body = server.strip_frontmatter("--- not frontmatter ---\nbody")

        self.assertEqual({}, metadata)
        self.assertEqual("--- not frontmatter ---\nbody", body)


if __name__ == "__main__":
    unittest.main()
