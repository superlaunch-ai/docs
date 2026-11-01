"""Exercise the public docs check with matching but invalid example copies."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


class ExampleSchemaTests(unittest.TestCase):
    def test_matching_invalid_example_copies_fail_validation(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            copied = Path(directory) / "docs"
            shutil.copytree(root, copied, ignore=shutil.ignore_patterns(
                ".git", ".venv", ".metrics", "tests", "__pycache__"
            ))
            path = copied / "maintenance/examples.json"
            examples = json.loads(path.read_text())
            examples[0]["args"]["limit"] = "twenty-five"
            path.write_text(json.dumps(examples))
            page = copied / "mcp/examples.mdx"
            page.write_text(re.sub(
                r"(\*\*Tool:\*\* `ad_accounts_list`.*?```json\n).*?(\n```)",
                lambda match: match[1] + json.dumps(examples[0]["args"]) + match[2],
                page.read_text(), count=1, flags=re.S,
            ))
            result = subprocess.run(
                [sys.executable, "scripts/verify_docs.py"], cwd=copied,
                capture_output=True, text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid example for ad_accounts_list", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
