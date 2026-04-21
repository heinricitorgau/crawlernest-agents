from __future__ import annotations

import sys
from pathlib import Path


def summarize_failure_kind(content: str) -> list[str]:
    lowered = content.lower()
    hints: list[str] = []

    if "modulenotfounderror" in lowered or "importerror" in lowered:
        hints.append("import/path issue")
    if "ran 0 tests" in lowered or "start directory is not importable" in lowered:
        hints.append("test discovery issue")
    if "assert" in lowered or "!=" in lowered or "expected" in lowered:
        hints.append("data/output mismatch")
    if "keyerror" in lowered or "valueerror" in lowered or "typeerror" in lowered:
        hints.append("logic bug")
    if "permission denied" in lowered or "no such file or directory" in lowered:
        hints.append("environment/config mismatch")

    if not hints:
        hints.append("unknown from log alone")

    return hints


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python3 scripts/generate-debug-prompt.py <log_path> <output_path>")
        return 1

    log_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not log_path.exists():
        print(f"Log file not found: {log_path}")
        return 1

    content = log_path.read_text(encoding="utf-8", errors="replace")
    hints = summarize_failure_kind(content)
    hint_lines = "\n".join(f"- {hint}" for hint in hints)

    prompt = f"""# Debug Prompt
Use the `crawlernest-debug-reliability-engineer` role.

Task:
Analyze this failed test run.

Goals:
1. Identify the observed behavior
2. Infer the likely reproduction path
3. Find the root cause
4. Suggest the minimal safe fix
5. State whether the failure is likely due to:
{hint_lines}

Constraints:
- Do not guess without citing evidence from the log
- Prefer the smallest grounded explanation first

## Test Output
```text
{content}
```
"""

    output_path.write_text(prompt, encoding="utf-8")
    print(f"Wrote debug prompt to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
