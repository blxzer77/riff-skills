"""Link previews and status lookups for the chat service."""

from urllib.parse import quote

STATUS_SERVICE = "https://status.internal.example.com"


def fetch_preview(http, payload):
    """Fetch a page the user pasted so the client can render a preview card."""
    url = payload["url"]
    response = http.get(url, timeout=3)
    return {"title": response.title, "status": response.status_code}


def fetch_status(http, payload):
    """Look up the delivery status of one of the user's own messages."""
    message_id = quote(payload["message_id"], safe="")
    response = http.get(f"{STATUS_SERVICE}/messages/{message_id}", timeout=3)
    return {"state": response.json()["state"]}
