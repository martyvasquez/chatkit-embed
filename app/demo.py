from fastapi.responses import HTMLResponse

DEMO_APP_ID = "app_demo"
DEMO_CLIENT_SECRET = "demo_client_secret"

DEMO_OPTIONS = {
    "theme": {
        "colorScheme": "dark",
        "radius": "pill",
    },
    "composer": {
        "placeholder": "Ask me anything about ChatKit Embed Host...",
    },
    "startScreen": {
        "greeting": "👋 Hi! Welcome to the ChatKit Embed demo.",
        "prompts": [
            {"title": "What is ChatKit Embed Host?", "description": "Overview of this POC."},
            {"title": "How does domain locking work?", "description": "Security basics."},
        ],
    },
}

DEMO_HTML = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>ChatKit Embed Demo</title>
  </head>
  <body style="font-family: sans-serif; margin: 60px;">
    <h1>ChatKit Embed Demo</h1>
    <p>This page hard codes <code>data-app-id="{app_id}"</code> to show the widget without touching the admin UI.</p>
    <script src="/static/embed.js" data-app-id="{app_id}" async></script>
  </body>
</html>
"""


def get_demo_options(app_id: str):
    if app_id != DEMO_APP_ID:
        return None
    return DEMO_OPTIONS


def get_demo_client_secret(app_id: str):
    if app_id != DEMO_APP_ID:
        return None
    return DEMO_CLIENT_SECRET


def demo_page():
    return HTMLResponse(DEMO_HTML.format(app_id=DEMO_APP_ID))
