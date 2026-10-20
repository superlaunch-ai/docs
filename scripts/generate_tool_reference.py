"""Generate exact tool references and the tool index from the reviewed catalog."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def type_label(schema):
    if 'enum' in schema:
        return ', '.join(str(value) for value in schema['enum'])
    if 'const' in schema:
        return str(schema['const'])
    if 'anyOf' in schema:
        return ' or '.join(dict.fromkeys(type_label(item) for item in schema['anyOf']))
    value = schema.get('format', schema.get('type', 'object'))
    return ' or '.join(value) if isinstance(value, list) else value


def render_tool(tool):
    name = tool['name']
    schema = tool['inputSchema']
    access = '`mcp:read`' if tool['annotations']['readOnlyHint'] else '`mcp:read` and `mcp:write`'
    description = re.sub(r'\s+', ' ', tool.get('description', '')).strip().replace('``', '`')
    lines = [f'<span id="{name.replace("_", "-")}" />', '', f'## {name}', '', description, '', f'**Access:** {access}. Workspace and target permissions also apply.', '']
    properties = schema.get('properties', {})
    if properties:
        lines += ['| Parameter | Type | Required / default |', '| --- | --- | --- |']
        for key, value in properties.items():
            required = 'Required' if key in schema.get('required', []) else '`' + json.dumps(value.get('default')) + '`'
            lines.append(f'| `{key}` | {type_label(value)} | {required} |')
        lines += ['', 'Keep the argument nesting shown in the schema. Expand it for nested fields, allowed values, and limits.', '']
    else:
        lines += ['**Arguments:** none.', '']
    lines += ['<Accordion title="Full input schema">', '', '```json', json.dumps(schema, indent=2, ensure_ascii=False), '```', '', '</Accordion>', '']
    return '\n'.join(lines)


def outputs():
    catalog = json.loads((ROOT / 'maintenance/tool-catalog.json').read_text())
    tools = {tool['name']: tool for tool in catalog}
    groups = json.loads((ROOT / 'maintenance/tool-groups.json').read_text())
    names = [name for group in groups.values() for name in group]
    assert len(names) == len(set(names)) and set(names) == set(tools), 'Tool groups must cover the current catalog exactly once'
    result = {}
    rows = []
    for page, names in groups.items():
        source = (ROOT / (page + '.mdx')).read_text()
        metadata = source.split('---', 2)[1]
        if page.endswith('/actions'):
            metadata = metadata.replace('Upload media, create Meta objects, duplicate setups, and change delivery status.', 'Upload media, create or update Meta objects, duplicate setups, and change delivery status.')
        title = json.loads(re.search(r'^title:\s*(.+)$', metadata, re.M)[1])
        intro = 'Check capabilities and current access before a write. Use the exact tool arguments below. Read results before retrying an uncertain provider operation.'
        result[page + '.mdx'] = '---' + metadata + '---\n\n' + intro + '\n\n' + '\n'.join(render_tool(tools[name]) for name in names)
        rows += ['## ' + title, '', '| Tool | Access | Purpose |', '| --- | --- | --- |']
        for name in names:
            tool = tools[name]
            access = 'Read' if tool['annotations']['readOnlyHint'] else 'Write'
            purpose = re.sub(r'\s+', ' ', tool['description']).strip().split('. ')[0].rstrip('.') + '.'
            rows.append(f'| [`{name}`](/{page}#{name.replace("_", "-")}) | {access} | {purpose.replace("|", " / ")} |')
        rows.append('')
    result['mcp/tools.mdx'] = f'''---
title: "MCP tool index"
description: "Find all {len(tools)} documented MCP tools by task, access requirement, and exact input schema."
---

This reference covers {len(tools)} tools from the reviewed deployed MCP source. Your access, client settings, and enabled features determine which tools you can use. See the [capability overview](/reference/capabilities) for product workflows.

Use an MCP client with [OAuth authorization](/mcp/authentication). Read tools require `mcp:read`. Write tools also require `mcp:write` and the relevant workspace and target permissions. Preserve argument nesting such as `payload`, `request`, `data`, `family`, and `content`.

Read the [argument examples](/mcp/examples) and [IDs and retries](/concepts/ids-and-versions) before writes. The schemas define supported inputs; live provider eligibility still requires capability checks and validation.

''' + '\n'.join(rows)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--output-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    result = outputs()
    for name, text in result.items():
        path = args.output_dir / name
        if args.check:
            normalize = lambda value: '\n'.join(line.strip() for line in value.splitlines() if line.strip())
            assert normalize(path.read_text()) == normalize(text), f'Stale tool reference: {name}'
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
    print(f'Checked {len(result)} generated tool reference pages' if args.check else f'Generated {len(result)} tool reference pages')


if __name__ == '__main__':
    main()
