import json
import re
from typing import Any, Dict, List

import json5


class OptionsParseError(ValueError):
    pass


IMPORT_RE = re.compile(r"^\s*import[^\n]*$", re.MULTILINE)
DECL_RE = re.compile(r"^\s*(export\s+)?(const|let|var)\s+[\w$]+\s*[:=].*$", re.MULTILINE)


def extract_object_literal(raw: str) -> str:
    if not raw:
        raise OptionsParseError("ChatKit options input is empty.")

    text = IMPORT_RE.sub("", raw)
    text = DECL_RE.sub("", text)

    start = text.find("{")
    if start == -1:
        raise OptionsParseError("Could not locate object literal in provided options.")

    depth = 0
    for idx in range(start, len(text)):
        char = text[idx]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : idx + 1]

    raise OptionsParseError("Unbalanced braces while parsing options.")


def parse_options(raw: str) -> Dict[str, Any]:
    literal = extract_object_literal(raw)
    try:
        data = json5.loads(literal)
    except json5.JSON5DecodeError as exc:
        raise OptionsParseError(f"Invalid ChatKit options: {exc}") from exc

    data.pop("api", None)
    if "composer" not in data and "startScreen" not in data:
        raise OptionsParseError("Options must include composer or startScreen.")
    return data


def serialize_options(raw: str) -> str:
    data = parse_options(raw)
    return json.dumps(data, separators=(",", ":"), ensure_ascii=False)


def parse_allowed_domains(raw: str) -> List[str]:
    raw = raw or ""
    domains = [item.strip().lower() for item in raw.split(",") if item.strip()]
    return domains
