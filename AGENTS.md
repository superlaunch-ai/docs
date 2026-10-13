# Superlaunch documentation

Publish to https://docs.superlaunch.pro/ through Mintlify. Use the Admin MCP for pages, navigation, and configuration. Supporting files can use a Git branch and pull request.

## Audience and structure

Write for marketers, workspace owners, and developers connecting AI clients. Keep setup tutorials, task guides, explanations, and tool reference separate. Link between them when readers need another kind of help.

The sections cover setup and product concepts; workspace connections and permissions; insights, rules, activity, brands, and memory; the Launcher journey; MCP connection and workflows; the complete tool reference; billing and troubleshooting.

## Voice and copy

Use direct, calm, helpful English. Address the reader as you. Use active voice, sentence-case headings, exact UI labels in bold, and code formatting for identifiers. Start guides with the task and prerequisites, then give steps and a verification result.

Remove filler and marketing claims. Avoid leverage, unlock, seamless, powerful, game-changing, delve, simply, easily, in today's landscape, and in conclusion. Avoid artificial contrasts, rhetorical questions, exclamation points, em dashes, and product praise. Describe behavior, constraints, and recovery steps. Apply the Stop Slop rules before shipping.

Editorial references:
- https://developers.google.com/style/tone
- https://developers.google.com/style/highlights
- https://diataxis.fr/start-here/

## Product truth

Use current source and official client documentation. Do not invent features, prices, limits, permissions, or tool fields. Keep workspace UUIDs separate from provider IDs and Launcher version IDs. Distinguish preview, acceptance, completion, dry-run mode, and partial failure.

A request UUID does not prove idempotent behavior. Private facts require consent for persistence. Public docs must contain no credentials, customer data, private upload URLs, or internal operational instructions.

The product MCP endpoint is https://mcp.superlaunch.pro/mcp. Documentation exports do not authorize workspace access.

## Brand

Preserve the existing arrow mark and lowercase wordmark. Use accent #E8A33D, page #0B0E11, Space Grotesk headings, and Inter body text. Keep the dark application theme.

## Verification and publishing

Run `python3 scripts/verify_docs.py` and `npx mint validate` before merging. Update the stored tool catalog and reference together. Validate examples against tool input schemas.

Mintlify deploys main. Verify live links, tool anchors, schema accordions, search, and desktop/mobile rendering. Run `python3 scripts/generate_llms.py` after editing navigation or page metadata. The generated short index has a CI freshness check. Mintlify generates /llms-full.txt and page Markdown; verify them after publishing. Do not hand-edit text exports.

All manual commits use Bogdan Piven <bogdanpiven@gmail.com>.
