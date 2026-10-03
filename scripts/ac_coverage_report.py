"""Ask Claude to map each AC id in specs/app_spec.md to the tests that cover it.

The agent is read-only: it may use Read, Glob and Grep, and Bash, Write, Edit
and NotebookEdit are disallowed.

Usage (from the repo root):
    python scripts/ac_coverage_report.py
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

REPO_ROOT = Path(__file__).resolve().parents[1]

PROMPT = """\
1. Read specs/app_spec.md. Take every AC id (AC-01 to AC-10) from its traceability table, with the short criterion text from that table.
2. For each AC id, search backend/tests, frontend/src and e2e for test names that contain the id. Use Grep for the id, then Read the matching file if you need to confirm the test name.
3. Print one line per AC id in this form:
   AC-XX | criterion | test names found (file::test_name) | NONE if no test was found
Do not edit any file. Report only test names you found in the files; do not invent any.
"""


async def main() -> None:
    options = ClaudeAgentOptions(
        cwd=str(REPO_ROOT),
        allowed_tools=["Read", "Glob", "Grep"],
        disallowed_tools=["Bash", "Write", "Edit", "NotebookEdit"],
    )
    async for message in query(prompt=PROMPT, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())
