"""Check navigation, links, tool coverage, schemas, and editorial rules."""
import json
import re
from pathlib import Path
root = Path(__file__).resolve().parents[1]
config = json.loads((root / "docs.json").read_text())
catalog = json.loads((root / "maintenance/tool-catalog.json").read_text())
pages = []
def walk(value):
    if isinstance(value, str):
        if not value.startswith("https:"): pages.append(value)
    elif isinstance(value, list):
        for item in value: walk(item)
    elif isinstance(value, dict):
        for key in ("pages", "groups", "tabs"):
            if key in value: walk(value[key])
walk(config["navigation"])
assert len(pages) == len(set(pages)) == 41, f"Expected 41 unique pages: {len(pages)}"
names = {t["name"] for t in catalog}
documented = set()
for page in pages:
    path = root / (page + ".mdx")
    text = path.read_text()
    assert text.startswith("---\n") and all(key in text.split("---", 2)[1] for key in ("title:", "description:")), path
    visible = re.sub(r"```.*?```", "", text, flags=re.S)
    assert not re.search(r"\b(?:delve|leverage|game-changing|seamless|unlock|in conclusion)\b", visible, re.I), f"Filler in {page}"
    assert "\u2014" not in visible, f"Em dash in {page}"
    for target in re.findall(r'\]\((/[^)]+)\)|href="(/[^"\n]+)"', text):
        link = next(x for x in target if x)
        base = link.split("#")[0].split("?")[0].removesuffix(".md")
        if base in ("/llms.txt", "/llms-full.txt"): continue
        dest = root / (base.strip("/") + ".mdx")
        assert dest.exists(), f"Broken link {page}: {link}"
        if "#" in link:
            anchor = link.split("#", 1)[1]
            assert f'id="{anchor}"' in dest.read_text(), f"Missing tool anchor {link}"
    if page.startswith("mcp/reference/"):
        blocks = re.split(r"^## ([a-z][a-z0-9_]+)\n", text, flags=re.M)
        for name, body in zip(blocks[1::2], blocks[2::2]):
            assert name not in documented, f"Duplicate tool {name}"
            documented.add(name)
            schema = json.loads(re.search(r"```json\n(.*?)\n```", body, re.S)[1])
            expected = next(t["inputSchema"] for t in catalog if t["name"] == name)
            assert schema == expected, f"Schema mismatch: {name}"
assert documented == names, f"Tool coverage differs: {names ^ documented}"

# Check the examples readers copy, not only the maintenance artifact.
examples = json.loads((root / "maintenance/examples.json").read_text())
blocks = re.findall(r"\*\*Tool:\*\* `([^`]+)`.*?```json\n(.*?)\n```", (root / "mcp/examples.mdx").read_text(), re.S)
assert len(blocks) == len(examples)
for (name, arguments), example in zip(blocks, examples):
    assert name == example["tool"] and json.loads(arguments) == example["args"], f"Example drift: {name}"
failed_activity = next(e for e in examples if e["title"] == "Find failed tool activity")
assert failed_activity["args"]["payload"]["status"] == "failed"

assert config["name"] == "Superlaunch"
assert config["colors"]["primary"] == "#E8A33D"
assert config["background"]["color"]["dark"] == "#0B0E11"
assert config["appearance"] == {"default": "dark", "strict": True}
assert all("mintlify.com" not in str(config.get(k, {})) for k in ("navbar", "footer"))
print(f"Validated {len(pages)} pages, {len(documented)} tools, schemas, links, and brand settings")
