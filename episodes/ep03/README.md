# Episode 3 results: Spec Kit After the MVP

One change (saving an already-saved link returns 200 with the existing bookmark instead of 409),
made from tag `ep03-start` by three spec persistence models, two runs each, plus labelled arms.

- `metrics.md`: per-run time, agent tokens, tests, analyze and converge results, and how each was measured.
- `drift-score.md`: the blind drift test (5 questions, answered from each branch's `specs/` only).
- `drift-answers/<code>.md`: every evaluator's raw answers; `drift-codes.txt` maps codes to branches.
- `evaluator-prompt.md`: the evaluator prompt used for every code.
- `race-check.md`, `race_http.py`: the save-while-deleted probe and its output on every branch.

Branches: `ep03/<run>` (flowback-r1/r2, forward-r3/r4, living-r1/r2, shortcut-r1; arms forward-r1/r2 without
analyze; flowback-r2-authority and living-r2-authority with the one-line fix). Each step is tagged
`ep03-<run>-<step>`. Captures are in `episodes/ep03/capture/<run>/` on each branch.
