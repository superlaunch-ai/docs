"""Generate the public index and full documentation from checked page source."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = 'https://docs.superlaunch.pro'


def field(frontmatter, name):
    value = re.search(r'^' + name + r':\s*(.+)$', frontmatter, re.M)[1]
    return json.loads(value) if value.startswith('"') else value


def markdown(body):
    # Preserve code examples and schemas byte-for-byte when removing UI wrappers.
    parts = re.split(r'(```[\s\S]*?```)', body)
    for index in range(0, len(parts), 2):
        text = parts[index]
        text = re.sub(r'<span id="[^"]+"\s*/>', '', text)
        text = re.sub(r'</?(?:CardGroup|Accordion)\b[^>]*>', '', text)
        text = re.sub(
            r'<Card\b(?P<attrs>[^>]*)>(?P<body>.*?)</Card>',
            lambda match: '- [' + re.search(r'title="([^"]+)"', match['attrs'])[1]
            + '](' + re.search(r'href="([^"]+)"', match['attrs'])[1]
            + '): ' + match['body'].strip(), text, flags=re.S,
        )
        text = re.sub(r'\]\((/[^)]+)\)', lambda match: '](' + BASE_URL + match[1] + ')', text)
        parts[index] = text
    return ''.join(parts).strip()


def outputs():
    config = json.loads((ROOT / 'docs.json').read_text())
    index = ['# Superlaunch', '', '> ' + config['description'], '']
    full = ['# Superlaunch', '', '> Full public documentation and exact MCP input schemas.', '']
    count = 0
    for group in config['navigation']['pages']:
        index.extend(['## ' + group['group'], ''])
        for page in group['pages']:
            source = (ROOT / (page + '.mdx')).read_text()
            _, frontmatter, body = source.split('---', 2)
            if re.search(r'^(?:noindex|hidden):\s*true\s*$', frontmatter, re.M):
                continue
            title = field(frontmatter, 'title')
            description = field(frontmatter, 'description')
            index.append(f'- [{title}]({BASE_URL}/{page}.md): {description}')
            full.extend(['# ' + title, '', f'Source: {BASE_URL}/{page}', '', description, '', markdown(body), ''])
            count += 1
        index.append('')
    index.extend(['## Text and workspace access', '',
        f'- [Full documentation]({BASE_URL}/llms-full.txt): Combined text of the published documentation.',
        '- [Product MCP](https://mcp.superlaunch.pro/mcp): OAuth-protected access to authorized workspace data and operations.', ''])
    return {'llms.txt': '\n'.join(index), 'llms-full.txt': '\n'.join(full)}, count


if __name__ == '__main__':
    generated, page_count = outputs()
    for name, text in generated.items():
        path = ROOT / name
        if '--check' in sys.argv:
            assert path.read_text() == text, f'Run python3 scripts/generate_llms.py to refresh {name}'
        else:
            path.write_text(text)
    print(f'Documentation index and full text match all {page_count} public navigation pages')
