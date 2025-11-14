import json

import pytest

from app.parsing import OptionsParseError, serialize_options


def test_serialize_options_strips_api_section_and_handles_json5():
    raw = """
    import type { ChatKitOptions } from "@openai/chatkit";
    const options: ChatKitOptions = {
        api: { foo: 'bar' },
        theme: { colorScheme: 'dark' },
        composer: { attachments: { enabled: false } },
    };
    """
    serialized = serialize_options(raw)
    data = json.loads(serialized)
    assert "api" not in data
    assert data["theme"]["colorScheme"] == "dark"
    assert data["composer"]["attachments"]["enabled"] is False


def test_serialize_options_requires_composer_or_start_screen():
    raw = """
    const options = {
        theme: { colorScheme: "dark" },
    };
    """
    with pytest.raises(OptionsParseError):
        serialize_options(raw)
