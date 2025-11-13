from openai import OpenAI
from openai._exceptions import OpenAIError

from .config import get_settings


class ChatKitError(RuntimeError):
    pass


def create_chatkit_session(api_key: str, workflow_id: str) -> str:
    settings = get_settings()
    client_kwargs = {"api_key": api_key}
    if settings.openai_api_base:
        client_kwargs["base_url"] = str(settings.openai_api_base)
    client = OpenAI(**client_kwargs)
    try:
        response = client.chatkit.sessions.create(workflow_id=workflow_id)
    except OpenAIError as exc:
        raise ChatKitError("OpenAI ChatKit session creation failed.") from exc
    client_secret = getattr(response, "client_secret", None)
    if not client_secret:
        raise ChatKitError("OpenAI response did not include a client secret.")
    return client_secret
