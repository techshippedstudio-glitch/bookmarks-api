# Bookmarks API, built with GitHub Spec Kit

Companion repo for the **Tech Shipped** video *GitHub Spec Kit Tutorial: From Spec to Working API* (part of the **Spec to Ship** series).

Video: _link coming soon_

A small REST API where you can save a link with a title and optional tags, list bookmarks newest first, filter by tag, and delete a bookmark, with no duplicate URLs. It is built with FastAPI and PostgreSQL, but none of the application code was written by hand: it was driven by a constitution and a spec through the Spec Kit flow.

## Jump in at any stage

Every step of the video is a git tag, so you can check out the exact state at that point.

| Tag | What the repo contains | Video |
| --- | --- | --- |
| `ep01-start` | This starter: README, Postgres setup, helper script | 2:40 |
| `ep01-init` | After `specify init`: Spec Kit templates and Claude Code skills | 3:15 |
| `ep01-constitution` | Project constitution in `.specify/memory/constitution.md` | 4:00 |
| `ep01-spec` | Feature spec in `specs/` | 6:00 |
| `ep01-clarify` | Spec updated with clarification answers | 8:00 |
| `ep01-plan` | Plan and design documents, including the data model | 9:30 |
| `ep01-tasks` | Ordered task list in `tasks.md` | 11:30 |
| `ep01-implement` | Working API and tests | 13:00 |
| `ep01-converged` | Final state after `/speckit-converge` reports Converged | 15:00 |

```bash
git checkout ep01-plan      # for example
git checkout main           # back to the latest
```

## Prerequisites

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Docker (for Postgres)
- A supported AI coding agent. The video uses Claude Code; see the [integration list](https://github.github.io/spec-kit/reference/integrations.html) for others.
- Spec Kit 1.2.2 (the version used in the video)

## Follow along

1. Clone this repo and start Postgres:

   ```bash
   git clone https://github.com/<owner>/bookmarks-api.git
   cd bookmarks-api
   git checkout ep01-start
   docker compose up -d
   cp .env.example .env
   ```

2. Install Spec Kit and turn the repo into a Spec Kit project:

   ```bash
   uv tool install specify-cli --from git+https://github.com/github/spec-kit.git@v1.2.2
   specify version
   specify init --here --force --integration claude
   ```

   Using a different agent? Replace `claude` with its integration key, for example `copilot` or `cursor-agent`.

3. Open your coding agent in this folder and run each step, reviewing the result before moving on. Claude Code invokes Spec Kit as skills with a hyphen (`/speckit-specify`); the Spec Kit docs write the same commands with a dot (`/speckit.specify`).

   ```text
   /speckit-constitution Every endpoint has typed request and response models. Tests run against a real database, not mocks. All errors return one consistent JSON shape. Keep dependencies minimal. Every feature ships with tests.

   /speckit-specify Build a bookmarks API. A user can save a link with a title and optional tags, list their bookmarks newest first, filter by tag, and delete a bookmark. Saving the same URL twice must not create a duplicate.

   /speckit-clarify

   /speckit-plan Use FastAPI with Pydantic models and PostgreSQL. Use SQLAlchemy with Alembic migrations. Postgres runs from the existing docker-compose.yml, with separate databases for development and tests (see .env.example). Expose a REST API with OpenAPI docs.

   /speckit-tasks

   /speckit-analyze

   /speckit-implement Implement only the Setup and Foundational phases. Stop before the user stories.

   /speckit-implement

   /speckit-converge
   ```

   Repeat `/speckit-implement` and `/speckit-converge` until converge reports **Converged**.

Your agent's output will differ from the video: coding agents don't produce identical results on every run. That's expected. The spec is the source of truth, so review each artifact against it.

## Run the finished API

From `ep01-implement` onward the repo contains a working API:

```bash
docker compose up -d                                   # Postgres
uv sync                                                # install dependencies
uv run alembic upgrade head                            # create the schema
uv run uvicorn bookmarks_api.main:app --reload         # http://127.0.0.1:8000/docs
uv run pytest                                          # tests, against the bookmarks_test database
```

| Endpoint | What it does |
| --- | --- |
| `POST /bookmarks` | Save `{"url", "title", "tags"}`; 201 for a new link, 200 with the existing bookmark (unchanged) if the link is already saved |
| `GET /bookmarks?tag=&limit=&cursor=` | List newest first, 20 per page by default, optional tag filter; pass `next_cursor` from one page as `cursor` to get the next |
| `DELETE /bookmarks/{id}` | Delete a bookmark |

Every error has the same shape: `{"error": {"code", "message", "details"}}`.

## Postgres

`docker-compose.yml` starts Postgres 18 with two databases:

| Database | Purpose | URL |
| --- | --- | --- |
| `bookmarks` | Running the API locally | `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks` |
| `bookmarks_test` | The test suite | `postgresql://bookmarks:bookmarks@localhost:5432/bookmarks_test` |

The credentials are for local development only. To reset all data: `docker compose down -v && docker compose up -d`.

## Links

- [GitHub Spec Kit](https://github.com/github/spec-kit)
- [Spec Kit SDD command reference](https://github.github.io/spec-kit/reference/agentic-sdd.html)

## License

MIT. See [LICENSE](LICENSE).
