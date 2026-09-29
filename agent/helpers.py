def compact_specialist_result(text: str, max_chars: int = 1000) -> str:
    if len(text) <= max_chars:
        return text
    return (
        text[:650]
        + "\n\n[Middle of specialist output omitted for context size.]\n\n"
        + text[-300:]
    )
