"""User Story 4 - Delete a bookmark (spec.md, scenarios 1 to 3)."""

from fastapi.testclient import TestClient


def save(client: TestClient, url: str, tags: list[str] | None = None) -> int:
    response = client.post("/bookmarks", json={"url": url, "title": "T", "tags": tags or []})
    assert response.status_code == 201
    return response.json()["id"]


def test_deleted_bookmark_disappears_from_list_and_filter(client: TestClient, row_count) -> None:
    bookmark_id = save(client, "https://example.com/a", ["python"])
    keep = save(client, "https://example.com/b", ["python"])

    response = client.delete(f"/bookmarks/{bookmark_id}")

    assert response.status_code == 204
    assert response.content == b""
    assert [i["id"] for i in client.get("/bookmarks").json()["items"]] == [keep]
    assert [i["id"] for i in client.get("/bookmarks", params={"tag": "python"}).json()["items"]] == [keep]
    assert row_count() == 1


def test_deleting_unknown_bookmark_returns_not_found(client: TestClient) -> None:
    response = client.delete("/bookmarks/999")

    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert "999" in error["message"]


def test_deleting_twice_returns_not_found_the_second_time(client: TestClient) -> None:
    bookmark_id = save(client, "https://example.com/a")

    assert client.delete(f"/bookmarks/{bookmark_id}").status_code == 204
    assert client.delete(f"/bookmarks/{bookmark_id}").status_code == 404


def test_link_can_be_saved_again_after_delete(client: TestClient) -> None:
    first = save(client, "https://example.com/a")
    client.delete(f"/bookmarks/{first}")

    response = client.post("/bookmarks", json={"url": "https://EXAMPLE.com/a/", "title": "Again"})

    assert response.status_code == 201
    assert response.json()["id"] != first


def test_non_numeric_id_is_a_validation_error(client: TestClient) -> None:
    response = client.delete("/bookmarks/abc")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
