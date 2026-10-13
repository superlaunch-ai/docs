"""Generate the public short index from navigation and page frontmatter."""
import json
import re
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
config = json.loads((root / 'docs.json').read_text())
lines = ['# Superlaunch', '', '> ' + config['description'], '']
for group in config['navigation']['pages']:
    lines.extend(['## ' + group['group'], ''])
    for page in group['pages']:
        content = (root / (page + '.mdx')).read_text()
        frontmatter = content.split('---', 2)[1]
        def field(name):
            value = re.search(r'^' + name + r':\s*(.+)$', frontmatter, re.M)[1]
            return json.loads(value) if value.startswith('"') else value
        lines.append(f'- [{field("title")}](https://docs.superlaunch.pro/{page}.md): {field("description")}')
    lines.append('')
lines.extend(['## Text and workspace access', '',
    '- [Full documentation](https://docs.superlaunch.pro/llms-full.txt): Combined text of the published documentation.',
    '- [Product MCP](https://mcp.superlaunch.pro/mcp): OAuth-protected access to authorized workspace data and operations.', ''])
result = '\n'.join(lines)
path = root / 'llms.txt'
if '--check' in sys.argv:
    assert path.read_text() == result, 'Run python3 scripts/generate_llms.py to refresh the index'
else:
    path.write_text(result)
print('Documentation index matches all 41 navigation pages')
