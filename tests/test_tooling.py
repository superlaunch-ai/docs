"""Test public documentation tooling with private copies of its input files."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ToolingTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="ub-docs-fixture-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "docs"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(
            ".git", ".venv", ".metrics", "tests", "target", "coverage", ".coverage*",
            "__pycache__",
        ))
        for name in ("verify_docs.py", "generate_llms.py", "generate_tool_reference.py"):
            self.assertEqual((self.root / "scripts" / name).read_bytes(),
                             (ROOT / "scripts" / name).read_bytes())

    def run_cli(self, name, *arguments):
        return subprocess.run([sys.executable, str(self.root / "scripts" / name), *arguments],
                              cwd=self.root, capture_output=True, text=True)

    def succeeds(self, name, *arguments):
        result = self.run_cli(name, *arguments)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result

    def fails(self, name, message, *arguments):
        result = self.run_cli(name, *arguments)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(message, result.stdout + result.stderr)

    def test_current_sources_pass_all_public_checks(self):
        self.succeeds("verify_docs.py")
        self.succeeds("generate_llms.py", "--check")
        self.succeeds("generate_tool_reference.py", "--check")

    def test_regeneration_preserves_all_checked_exports_and_references(self):
        expected = {name: (self.root / name).read_bytes()
                    for name in ("llms.txt", "llms-full.txt")}
        self.succeeds("generate_llms.py")
        for name, content in expected.items():
            self.assertEqual((self.root / name).read_bytes(), content)
        output = self.root / "private-output"
        self.succeeds("generate_tool_reference.py", "--output-dir", str(output))
        self.succeeds("generate_tool_reference.py", "--check", "--output-dir", str(output))
        self.assertEqual(len(list(output.rglob("*.mdx"))), 13)
        self.succeeds("verify_docs.py")

    def test_stale_text_export_is_rejected(self):
        path = self.root / "llms.txt"
        path.write_text(path.read_text() + "\nStale export\n")
        self.fails("generate_llms.py", "refresh llms.txt", "--check")

    def test_stale_tool_reference_is_rejected(self):
        path = self.root / "mcp/tools.mdx"
        path.write_text(path.read_text() + "\nStale reference\n")
        self.fails("generate_tool_reference.py", "Stale tool reference", "--check")

    def test_tool_reference_check_ignores_layout_space(self):
        path = self.root / "mcp/tools.mdx"
        path.write_text("\n".join("  " + line + "  " for line in path.read_text().splitlines()))
        self.succeeds("generate_tool_reference.py", "--check")

    def test_duplicate_tool_group_entry_is_rejected(self):
        path = self.root / "maintenance/tool-groups.json"
        groups = json.loads(path.read_text())
        first = next(iter(groups.values()))
        first.append(first[0])
        path.write_text(json.dumps(groups))
        self.fails("generate_tool_reference.py", "Tool groups must cover the current catalog exactly once",
                   "--output-dir", str(self.root / "private-output"))

    def test_missing_tool_group_entry_is_rejected(self):
        path = self.root / "maintenance/tool-groups.json"
        groups = json.loads(path.read_text())
        next(iter(groups.values())).pop()
        path.write_text(json.dumps(groups))
        self.fails("generate_tool_reference.py", "Tool groups must cover the current catalog exactly once",
                   "--output-dir", str(self.root / "private-output"))

    def test_external_navigation_is_not_a_local_page(self):
        path = self.root / "docs.json"
        config = json.loads(path.read_text())
        config["navigation"]["pages"].append({"group": "External", "pages": ["https://example.test/help"]})
        path.write_text(json.dumps(config))
        self.succeeds("verify_docs.py")

    def test_duplicate_navigation_is_rejected(self):
        path = self.root / "docs.json"
        config = json.loads(path.read_text())
        config["navigation"]["pages"][0]["pages"].append("index")
        path.write_text(json.dumps(config))
        self.fails("verify_docs.py", "Expected unique navigation pages")

    def test_broken_local_link_is_rejected(self):
        path = self.root / "index.mdx"
        path.write_text(path.read_text() + "\n[Missing](/no-such-page)\n")
        self.fails("verify_docs.py", "Broken link index")

    def test_missing_tool_anchor_is_rejected(self):
        path = self.root / "index.mdx"
        path.write_text(path.read_text() + "\n[Missing](/mcp/tools#no-such-anchor)\n")
        self.fails("verify_docs.py", "Missing tool anchor")

    def test_missing_metadata_is_rejected(self):
        path = self.root / "index.mdx"
        path.write_text(path.read_text().replace("description:", "missing:", 1))
        self.fails("verify_docs.py", "index.mdx")

    def test_filler_and_em_dash_are_rejected(self):
        path = self.root / "index.mdx"
        original = path.read_text()
        for text, message in (("unlock", "Filler in index"), ("\u2014", "Em dash in index")):
            with self.subTest(text=text):
                path.write_text(original + "\n" + text + "\n")
                self.fails("verify_docs.py", message)

    def test_hidden_pages_and_wrappers_preserve_public_text_and_code(self):
        config = {"description": "Fixture", "navigation": {"pages": [
            {"group": "Fixture", "pages": ["visible", "hidden", "noindex"]}]}}
        (self.root / "docs.json").write_text(json.dumps(config))
        code = '```json\n{"href": "/inside-code", "text": "<Accordion>"}\n```'
        (self.root / "visible.mdx").write_text('''---
title: "Visible title"
description: Unquoted description
---
<span id="visible-anchor" />
<CardGroup><Card title="Go" href="/target"> Useful link </Card></CardGroup>
<Accordion title="Details">Detail text</Accordion>
[Read](/target)
''' + code)
        for name, flag in (("hidden", "hidden"), ("noindex", "noindex")):
            (self.root / (name + ".mdx")).write_text(
                f'---\ntitle: "Secret title"\ndescription: "Private fixture"\n{flag}: true\n---\nSecret body\n')
        result = self.succeeds("generate_llms.py")
        self.assertIn("all 1 public navigation pages", result.stdout)
        index = (self.root / "llms.txt").read_text()
        full = (self.root / "llms-full.txt").read_text()
        self.assertIn("[Visible title](https://docs.superlaunch.pro/visible.md): Unquoted description", index)
        self.assertNotIn("Secret", index + full)
        self.assertIn("- [Go](https://docs.superlaunch.pro/target): Useful link", full)
        self.assertIn("Detail text", full)
        self.assertIn("[Read](https://docs.superlaunch.pro/target)", full)
        self.assertIn(code, full)
        self.assertNotIn("<Card", full)
        self.assertNotIn("<span", full)
        self.assertNotIn("<Accordion title", full)
        self.succeeds("generate_llms.py", "--check")

    def test_unicode_schema_and_empty_arguments_are_preserved(self):
        tool = {"name": "fixture_read", "description": "Read café | items. More detail.",
                "annotations": {"readOnlyHint": True},
                "inputSchema": {"type": "object", "properties": {
                    "label": {"type": "string", "default": "café"}}}}
        empty = {"name": "fixture_write", "description": "Write items.",
                 "annotations": {"readOnlyHint": False},
                 "inputSchema": {"type": "object"}}
        (self.root / "maintenance/tool-catalog.json").write_text(json.dumps([tool, empty]))
        (self.root / "maintenance/tool-groups.json").write_text(json.dumps({
            "mcp/reference/actions": ["fixture_read", "fixture_write"]}))
        self.succeeds("generate_tool_reference.py")
        page = (self.root / "mcp/reference/actions.mdx").read_text()
        index = (self.root / "mcp/tools.mdx").read_text()
        self.assertIn('"default": "café"', page)
        self.assertNotIn('"default": "caf\\u00e9"', page)
        self.assertIn("**Arguments:** none.", page)
        self.assertIn("`mcp:read` and `mcp:write`", page)
        self.assertIn("Read café  /  items.", index)
        self.assertIn("| Write | Write items. |", index)
        schemas = re.findall(r"```json\n(.*?)\n```", page, flags=re.S)
        self.assertEqual([json.loads(schema) for schema in schemas],
                         [tool["inputSchema"], empty["inputSchema"]])
        self.succeeds("generate_tool_reference.py", "--check")


if __name__ == "__main__":
    unittest.main()
