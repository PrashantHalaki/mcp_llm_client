def strip_markdown_code_block(text: str) -> str:
    text = text.strip()
    if text.startswith("```json"):
        text = text[len("```json"):].strip()
    if text.startswith("```"):
        text = text[len("```"):].strip()
    if text.endswith("```"):
        text = text[:text.rfind("```")].strip()
    return text
