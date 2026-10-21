-- Runs once, the first time the Postgres container starts with an empty volume.
-- Creates a separate database for the test suite.
CREATE DATABASE bookmarks_test OWNER bookmarks;
