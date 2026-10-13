# Superlaunch documentation

Live site: https://docs.superlaunch.pro/

This repository contains 41 customer documentation pages and reference entries for 97 MCP tools. Mintlify deploys main; content edits use the connected Admin MCP.

## Content and execution plan

1. Explain the product and guide a new workspace to its first report.
2. Document connections, permissions, IDs, versions, and retries.
3. Cover insights, rules, activity, brands, and consent-based memory.
4. Cover media intake, creative approval, collections, templates, launches, schedules, and recovery.
5. Document OAuth setup for ChatGPT, Claude, Codex, and remote MCP clients.
6. Publish all MCP tool names, parameters, nested schemas, and examples.
7. Provide billing help, troubleshooting, a glossary, and text exports.
8. Check copy, brand settings, links, schemas, rendering, and live deployment.

The initial catalog snapshot comes from MCP commit `b3b258df6a820042599e460e22f1c5cf7b5e2311`, with Core schemas from `eeb8304f734f7c14b8a7b3c83ba7e056635f79bf`. Product instructions were checked against frontend commit `fbd269b` and official client docs on 2026-10-13.

## Local validation

```sh
python3 scripts/verify_docs.py
python3 scripts/generate_llms.py --check
npx mint validate
npx mint dev
```

`maintenance/tool-catalog.json` stores the reviewed contract. The tool reference includes exact input schemas for nested fields and constraints. Refresh the snapshot and prose together when contracts change. `maintenance/examples.json` records the reviewed argument examples.

The copy follows Google's developer style guide and Diataxis. `AGENTS.md` records the editing and brand rules.

## Text exports

The short index comes from navigation and page metadata through `scripts/generate_llms.py`. CI rejects stale generated content. Mintlify generates the full-text export and page Markdown:
- https://docs.superlaunch.pro/llms.txt
- https://docs.superlaunch.pro/llms-full.txt
- Page Markdown, such as https://docs.superlaunch.pro/mcp/overview.md

Do not hand-edit exports. Regenerate the index after changing navigation or metadata. Check that exports contain the published guides and complete tool reference after deployment.
