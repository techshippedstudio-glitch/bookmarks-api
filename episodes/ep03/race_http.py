"""Save a link while its existing bookmark is deleted mid-save; print the HTTP status (real Postgres)."""
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker
from bookmarks_api.config import sqlalchemy_url
from bookmarks_api.db import get_session
from bookmarks_api.main import create_app

engine = create_engine(sqlalchemy_url(os.environ["TEST_DATABASE_URL"]))
with engine.begin() as c:
    c.execute(text("TRUNCATE bookmarks RESTART IDENTITY"))
factory = sessionmaker(bind=engine, expire_on_commit=False)
app = create_app()
def override():
    s = factory()
    try:
        yield s
    finally:
        s.close()
app.dependency_overrides[get_session] = override
client = TestClient(app, raise_server_exceptions=False)

first = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
print("save new link      ->", first.status_code)
again = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "Old"})
print("save it again      ->", again.status_code)
fired = []
def delete_mid_save(_s):
    if not fired:
        fired.append(1)
        with engine.begin() as c:
            c.execute(text("DELETE FROM bookmarks"))
event.listen(Session, "after_rollback", delete_mid_save)
r = client.post("/bookmarks", json={"url": "https://example.com/gone", "title": "New"})
event.remove(Session, "after_rollback", delete_mid_save)
print("save while deleted ->", r.status_code, r.json().get("error", {}).get("code", "") if r.status_code >= 400 else "")
