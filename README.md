# Superlaunch documentation

Live site: https://docs.superlaunch.pro/

This repository contains 42 customer documentation pages and reference entries for 104 MCP tools. Mintlify deploys main; content edits use the connected Admin MCP.

## Content and execution plan

1. Explain the product and guide a new workspace to its first report.
2. Document connections, permissions, IDs, versions, and retries.
3. Cover insights, rules, activity, brands, and consent-based memory.
4. Cover media intake, saved creative versions, collections, templates, launches, schedules, and recovery.
5. Document OAuth setup for ChatGPT, Claude, Codex, and remote MCP clients.
6. Publish all MCP tool names, parameters, nested schemas, and examples.
7. Provide billing help, troubleshooting, a glossary, and text exports.
8. Check copy, brand settings, links, schemas, rendering, and live deployment.

The current catalog matches deployed MCP commit `dcddb363a7cbb512b1e11ede7a2f5dffae0066a1` with `superlaunch-core==0.1.6rc58`. Product instructions were checked against deployed frontend commit `f280448276e0c950dbe6dc05ab53985af24bb736` on 2026-10-20. See `maintenance/tool-catalog-source.json` for the source record.

## Local validation

```sh
python3 scripts/verify_docs.py
python3 scripts/generate_llms.py --check
python3 scripts/generate_tool_reference.py --check
npx mint validate
npx mint dev
```

`maintenance/tool-catalog.json` stores the reviewed contract. The tool reference includes exact input schemas for nested fields and constraints. Refresh the snapshot and prose together when contracts change. `maintenance/examples.json` records the reviewed argument examples.

The copy follows Google's developer style guide and Diataxis. `AGENTS.md` records the editing and brand rules.

## Text exports

The short index comes from navigation and page metadata through `scripts/generate_llms.py`. CI rejects stale generated content. The same script generates the full-text export from the public navigation pages. Mintlify serves both custom files and provides page Markdown:
- https://docs.superlaunch.pro/llms.txt
- https://docs.superlaunch.pro/llms-full.txt
- Page Markdown, such as https://docs.superlaunch.pro/mcp/overview.md

Do not hand-edit exports. Regenerate the index after changing navigation or metadata. Check that exports contain the published guides and complete tool reference after deployment.

Documentation checks require `python3 -m pip install -r requirements-checks.txt`. Run `python3 -m unittest discover -s tests -v` to check schema validation of copied tool examples.
