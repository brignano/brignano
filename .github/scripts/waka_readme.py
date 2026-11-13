"""Run waka-readme-stats with a WakaTime personal OAuth token.

WakaTime rejects plugin API keys for reading stats (403 "API Keys are only for
plugins"). The upstream action only sends the key as `?api_key=`, so this
launcher runs the action's own code and moves auth into an
`Authorization: Bearer <token>` header on every request to wakatime.com.

Usage (from the action's `sources/` directory):
    WAKATIME_ACCESS_TOKEN=waka_tok_... python3 waka_readme.py
"""

import os
import runpy
import sys

import httpx

TOKEN = os.environ.get("WAKATIME_ACCESS_TOKEN", "").strip()
if not TOKEN:
    sys.exit("Missing WAKATIME_ACCESS_TOKEN (personal OAuth token, waka_tok_...)")

# The action refuses to start without a key. It only ever reaches the query
# string, which the hook below strips, so the token never lands in a URL or log.
os.environ["INPUT_WAKATIME_API_KEY"] = "unused-see-bearer-header"


async def add_bearer(request: httpx.Request) -> None:
    if request.url.host == "wakatime.com":
        request.url = request.url.copy_remove_param("api_key")
        request.headers["Authorization"] = f"Bearer {TOKEN}"


sys.path.insert(0, os.getcwd())
from manager_download import DownloadManager  # noqa: E402

DownloadManager._client.event_hooks["request"].append(add_bearer)

runpy.run_path("main.py", run_name="__main__")
