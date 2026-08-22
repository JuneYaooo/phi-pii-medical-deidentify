#!/usr/bin/env python3
"""Validate the standalone Agent Skill layout without external dependencies."""

from __future__ import annotations

import re
import sys
from pathlib import Path


SKILL_NAME = "phi-pii-medical-deidentify"
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "SKILL.md",
    "README.md",
    "README.en.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "agents/openai.yaml",
    "scripts/deidentify.py",
    "scripts/detector.py",
    "scripts/evaluate_labeled_set.py",
    "scripts/pipeline.py",
    "scripts/policy.py",
    "references/redaction-policy.md",
    "references/labeled-validation.md",
    "tests/test_standalone.py",
)


def validate() -> list[str]:
    errors: list[str] = []
    if ROOT.name != SKILL_NAME:
        errors.append(f"folder must be named {SKILL_NAME!r}, got {ROOT.name!r}")

    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    skill_path = ROOT / "SKILL.md"
    if skill_path.is_file():
        text = skill_path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(?P<header>.*?)\n---(?:\n|\Z)", text, re.DOTALL)
        if match is None:
            errors.append("SKILL.md must start with YAML frontmatter")
        else:
            fields = {}
            for line in match.group("header").splitlines():
                if ":" not in line:
                    errors.append(f"invalid frontmatter line: {line!r}")
                    continue
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
            if set(fields) != {"name", "description"}:
                errors.append("SKILL.md frontmatter must contain only name and description")
            if fields.get("name") != SKILL_NAME:
                errors.append(f"SKILL.md name must be {SKILL_NAME!r}")
            if not fields.get("description"):
                errors.append("SKILL.md description must not be empty")

    metadata_path = ROOT / "agents" / "openai.yaml"
    if metadata_path.is_file():
        metadata = metadata_path.read_text(encoding="utf-8")
        if f"${SKILL_NAME}" not in metadata:
            errors.append("agents/openai.yaml default_prompt must mention the Skill name")

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Skill is valid: {ROOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
