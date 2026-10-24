# Ep3 metrics: one change, three spec models (S3, 2026-10-24; v2 after review)

Change request: saving a link that is already bookmarked returns the existing bookmark with 200 OK instead of 409 Conflict. Starting point for every run: tag `ep03-start` (= main c997fe2, Ep2 converged, 98 tests passing).

All runs: Claude Opus 5.5 build-runner agent, same change request, own git worktree and own test database. Each approach's rules come from Spec Kit's evolving-specs guide (docs/guides/evolving-specs.md at tag v1.2.2), written into the runner's instructions.

**How things were measured**
- Wall-clock: first to last timestamp in the run's capture files (each step stamps `date -u` at start and end; the last stamp equals the last commit time). v1 of this file used the runners' own totals for two runs (forward-r1 9m26s, living-r2 13m07s); the capture rule gives 9m03s and 12m53s, used below.
- Agent tokens: the agent runtime's total for the build-runner agent. Money cost was not measured.
- Tests: runners ran 3.11, 3.12 and 3.13; the coordinator re-ran every branch on 3.12 and got the same counts.

**Correction in v2.** The guide's "Shared Feature Delivery Loop" (all three models) says "Run `/speckit.analyze` before implementation". Our first flow-forward rules (forward-r1, forward-r2) left that out, because the guide was first read through a summarizing fetch (learning L-012). Flow-forward was re-run with analyze as forward-r3 and forward-r4; those are the flow-forward results. forward-r1 and forward-r2 stay on their branches as a labelled "flow-forward, skipped analyze" arm.

## Per run

| Run | Approach | Wall-clock | Agent tokens | Tool calls | Tests (3.11/3.12/3.13) | Analyze | Converge |
|---|---|---|---|---|---|---|---|
| flowback-r1 | Flow-back, by the guide | 12m31s | 202,195 | 44 | 98 / 98 / 98 | 3 passes (C1 M1 L4 -> 0) | 2 rounds |
| flowback-r2 | Flow-back, by the guide | 9m25s | 187,004 | 42 | 98 / 98 / 98 | 2 passes (M4 L3 -> 0) | 2 rounds |
| forward-r3 | Flow-forward, by the guide | 10m18s | 233,088 | 63 | 101 / 101 / 101 | 3 passes (M3 L4 -> 1 accepted) | 1 round |
| forward-r4 | Flow-forward, by the guide | 11m19s | 239,770 | 70 | 102 / 102 / 102 | 3 passes (M5 L3 -> 1 accepted) | 2 rounds |
| living-r1 | Living spec, by the guide | 15m06s | 225,906 | 76 | 99 / 99 / 99 | 3 passes (H1 M2 L3 -> 0) | 2 rounds |
| living-r2 | Living spec, by the guide | 12m53s | 220,796 | 55 | 98 / 98 / 98 | 3 passes (M2 L4 -> 0) | 2 rounds |
| shortcut-r1 | Labelled arm: code + spec/plan/tasks only, no analyze, no converge | 2m19s | 107,302 | 16 | 97 / 97 / 97 | not run | not run |
| forward-r1 | Labelled arm: flow-forward without analyze | 9m03s | 200,299 | 47 | 103 / 103 / 103 | not run | 1 round |
| forward-r2 | Labelled arm: flow-forward without analyze | 8m34s | 194,456 | 50 | 100 / 100 / 100 | not run | 1 round |

Accepted analyze findings in flow-forward: 001 still describes the 409 rule and can't be edited (forward-r3 I3); the constitution lists clarify, which the run rules leave out (forward-r4 C1).

## Averages (n = 2 per approach)

| Approach | Avg wall-clock | Avg agent tokens | Time spread between runs |
|---|---|---|---|
| Flow-back | 10m58s | 194,600 | 3m06s |
| Flow-forward | 10m49s | 236,429 | 1m01s |
| Living spec | 14m00s | 223,351 | 2m13s |
| Shortcut (n = 1) | 2m19s | 107,302 | n.a. |
| Flow-forward without analyze (arm) | 8m49s | 197,378 | 29s |

Flow-back and flow-forward took about the same time; flow-forward used the most tokens (it writes a whole new spec folder); living spec was the slowest. The shortcut took 2m19s, about 4.7 times faster than either of the two quickest guide approaches, and about half the tokens. Adding analyze cost flow-forward about two minutes and about 39,000 tokens per run.

## Findings worth showing

1. **A bug the new rule created.** If a save of an already-saved link races a delete of that bookmark, the insert is skipped and then the lookup finds nothing. Coordinator HTTP probe (`race_http.py`, which forces the delete with an `after_rollback` hook): every guide run and both no-analyze forward runs return 201; **the shortcut returns 500**; ep03-start returned 409 (episodes/ep03/race-check.md). How each run handled it: flowback-r1, forward-r1/r2/r3/r4 and living-r1/r2 planned a retry while planning or fixing; in flowback-r2 analyze caught it (U1); in forward-r3 analyze caught that the retry had no test (C1); in forward-r4 analyze moved it into the spec as an edge case (U1). The shortcut, which skipped planning and analyze, uses `.one()` after the skipped insert.
2. **The shortcut's stale files came from its rules.** It was allowed to edit only spec.md, plan.md and tasks.md (capture shortcut-r1/02-artifacts.md:258), so its contract, quickstart, research and README still say 409. Analyze would not have flagged those files either: it reads only spec, plan, tasks and the constitution.
3. **Flow-forward leaves the old folder saying 409.** specs/001 is unchanged in every forward run; its quickstart step 2 now fails if followed, and nothing in 001 points to 002. With analyze, forward-r4 added a "Superseded statements in specs/001" table to the 002 plan, and the 002 contract says it supersedes 001's for POST /bookmarks.
4. **Living spec has no core "regenerate" path in Spec Kit 1.2.2.** The guide says core has no command that reconciles spec, plan and tasks. `setup-plan.sh` keeps an existing plan.md ("Plan already exists ... skipping template copy") and the plan instructions assume a fresh template, so the plan is revised in place. Both living runs rebuilt tasks.md with a History section; living-r1 also mapped old task numbers to new, and living-r2 reworded a done task (T008) so it no longer matched the code (analyze I3).
5. **Analyze also surfaces old debt.** Pre-existing from Ep2: offset-paging leftovers in tasks.md (flowback-r1 CRITICAL, because it breaks constitution Principle VI) and an unmarked offset line in spec.md. Pre-existing from the start: the contract's error-code enum didn't match `errors.py`.
6. **Smaller items:** `ON CONFLICT DO NOTHING` uses up an id on every re-save (allowed). The retry loops are capped (2 or 3 attempts); a link saved, deleted and saved again during every attempt still returns 500 in the guide runs too (recorded, not changed). forward-r4's first route docstring leaked an internal spec path into /openapi.json; converge caught it.

## Where the evidence lives

- Captures: branch `claude/ep03-<run>` (folder `episodes/ep03/capture/<run>/`), one file per step; per-step tags `ep03-<run>-<step>`.
- Results, blind-test answers, race probe: branch `claude/ep03-results`, folder `episodes/ep03/` (this file, drift-score.md, drift-answers/, race-check.md, race_http.py).
