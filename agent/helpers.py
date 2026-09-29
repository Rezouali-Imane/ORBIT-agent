import re
from typing import Any


def compact_specialist_result(text: str, max_chars: int = 700) -> str:
    if len(text) <= max_chars:
        return text
    return (
        text[:450]
        + "\n\n[Middle of specialist output omitted for context size.]\n\n"
        + text[-200:]
    )


def normalize_external_content(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(
            f"{key}: {normalize_external_content(item)}"
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return "\n".join(normalize_external_content(item) for item in value)
    return str(value)


def protect_external_content(text: Any) -> str:
    """Remove common prompt-injection lines before external text reaches a model."""
    text = normalize_external_content(text)
    lines = []
    injection_pattern = re.compile(
        r"^\s*(ignore|disregard|forget)\b.*\b(previous|earlier|system|developer|all)\b.*\b(instruction|prompt)s?\b|"
        r"^\s*(reply|respond|answer)\s+only\b",
        re.IGNORECASE,
    )
    for line in text.splitlines():
        if not injection_pattern.search(line):
            lines.append(line)
    return "\n".join(lines)
