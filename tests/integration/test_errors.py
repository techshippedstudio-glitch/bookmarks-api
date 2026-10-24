"""Cross-cutting checks: one error envelope everywhere (SC-005) and a complete OpenAPI contract
(Constitution I)."""

import pytest
from fastapi.testclient import TestClient


def assert_envelope(response, status: int, code: str) -> None:
    assert response.status_code == status
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message", "details"}
    assert body["error"]["code"] == code
    assert isinstance(body["error"]["message"], str) and body["error"]["message"]


def test_validation_error_envelope(client: TestClient) -> None:
    response = client.post("/bookmarks", json={"url": "ftp://x", "title": ""})

    assert_envelope(response, 422, "validation_error")
    fields = {detail["field"] for detail in response.json()["error"]["details"]}
    assert fields == {"url", "title"}


def test_not_found_error_envelope(client: TestClient) -> None:
    assert_envelope(client.delete("/bookmarks/12345"), 404, "not_found")


def test_unknown_route_uses_the_envelope(client: TestClient) -> None:
    assert_envelope(client.get("/nothing-here"), 404, "not_found")


def test_wrong_method_uses_the_envelope(client: TestClient) -> None:
    assert_envelope(client.put("/bookmarks"), 405, "method_not_allowed")


def test_malformed_json_uses_the_envelope(client: TestClient) -> None:
    response = client.post(
        "/bookmarks", content="{not json", headers={"Content-Type": "application/json"}
    )

    assert_envelope(response, 422, "validation_error")


def test_unexpected_errors_hide_internals(client: TestClient, monkeypatch) -> None:
    from bookmarks_api import repository

    def broken(*_args, **_kwargs):
        raise RuntimeError("SELECT secret FROM somewhere")

    monkeypatch.setattr(repository, "list_bookmarks", broken)
    response = client.get("/bookmarks")

    assert_envelope(response, 500, "internal_error")
    assert "secret" not in response.text


@pytest.mark.parametrize(
    ("path", "method"),
    [("/bookmarks", "post"), ("/bookmarks", "get"), ("/bookmarks/{bookmark_id}", "delete")],
)
def test_openapi_documents_every_operation(client: TestClient, path: str, method: str) -> None:
    spec = client.get("/openapi.json").json()
    operation = spec["paths"][path][method]

    assert operation["summary"]
    error_codes = {"post": {"422"}, "get": {"422"}, "delete": {"404", "422"}}[method]
    for code in error_codes:
        schema = operation["responses"][code]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("/ErrorResponse")
    if method == "post":
        assert operation["requestBody"]["content"]["application/json"]["schema"]["$ref"].endswith(
            "/BookmarkCreate"
        )
        for code in ("200", "201"):
            success = operation["responses"][code]["content"]["application/json"]["schema"]
            assert success["$ref"].endswith("/Bookmark")
        assert "409" not in operation["responses"]
    if method == "get":
        success = operation["responses"]["200"]["content"]["application/json"]["schema"]
        assert success["$ref"].endswith("/BookmarkPage")
