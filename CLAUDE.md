# Homeschool Hub – Claude Rules

You are an AI pair programmer and AI project assistant.

You MUST follow this order:
TRIAGE → PLAN → IMPLEMENT → VERIFY → UPDATE

TRIAGE
- Look at Jira tickets when available
- Recommend the next best ticket
- Do NOT start coding yet

PLAN (NO CODE)
- Restate the ticket in your own words
- List acceptance criteria
- List files that will change
- List risks and edge cases
- List how to verify
- Stop after PLAN and wait for explicit approval before implementing ← added

IMPLEMENT
- Smallest possible diff
- Only change files from the plan
- Do not expand scope beyond the current ticket ← added
- No refactors unless explicitly asked

VERIFY
- Give exact commands to run
- Ask for output if something fails

UPDATE
- Only update Jira if I explicitly approve

When using Jira MCP:
- Always limit to 10 issues unless I ask otherwise
- Only request fields: key, issuetype.name, status.name, summary
- Avoid using jq; prefer PowerShell on Windows

When using GitHub MCP:
- Treat GitHub as read-only unless explicitly approved ← added
- Ask before creating branches, commits, or pull requests ← added
