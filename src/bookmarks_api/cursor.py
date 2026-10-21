"""Opaque next-page cursors for keyset pagination (Constitution VI).

A cursor holds the last bookmark's ``created_at`` and ``id``, JSON-encoded and then
base64url-encoded. Clients treat it as an opaque string and pass it back unchanged.
"""

import base64
import binascii
import json
from datetime import datetime

INVALID_CURSOR = "cursor is not a valid next_cursor from this API."


def encode_cursor(created_at: datetime, bookmark_id: int) -> str:
    raw = json.dumps({"t": created_at.isoformat(), "id": bookmark_id}, separators=(",", ":"))
    return base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")


def decode_cursor(cursor: str) -> tuple[datetime, int]:
    """Return the (created_at, id) position a cursor points after, or raise ValueError."""
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        data = json.loads(base64.b64decode(padded, altchars=b"-_", validate=True))
        created_at = datetime.fromisoformat(data["t"])
        bookmark_id = data["id"]
    except (binascii.Error, ValueError, KeyError, TypeError) as exc:
        raise ValueError(INVALID_CURSOR) from exc
    is_int = isinstance(bookmark_id, int) and not isinstance(bookmark_id, bool)
    valid_id = is_int and bookmark_id >= 1
    if not valid_id or created_at.tzinfo is None:
        raise ValueError(INVALID_CURSOR)
    return created_at, bookmark_id
