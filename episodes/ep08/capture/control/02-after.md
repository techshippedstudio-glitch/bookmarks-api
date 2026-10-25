# 02-after (control run)

Captured: 2026-10-25T12:18:16Z

## `git branch -a`

```
* (HEAD detached at ep08-start)
  main
  remotes/origin/HEAD -> origin/main
  remotes/origin/claude/ep08-baseline
  remotes/origin/claude/ep08-git
  remotes/origin/main
[exit 0]
```

## `git rev-parse --abbrev-ref HEAD`

```
HEAD
[exit 0]
```

## `git status --short`

```
?? specs/002-bookmark-title-search/
[exit 0]
```

## `git status --short --ignored`

```
?? specs/002-bookmark-title-search/
!! .specify/feature.json
[exit 0]
```

## `cat .specify/feature.json`

```
{
  "feature_directory": "specs/002-bookmark-title-search"
}
[exit 0]
```

## `ls specs`

```
001-bookmarks-api
002-bookmark-title-search
[exit 0]
```

