# Ep3 blind drift test (S3d, 2026-10-24; v2 after review)

**v2:** flow-forward results are now forward-r3 and forward-r4, run with the guide's analyze step (see metrics.md correction). The first two flow-forward runs (forward-r1, forward-r2, no analyze) are kept as a labelled arm. Raw evaluator answers for every code are in drift-answers/<code>.md; the code map is drift-codes.txt.

**Question:** after the change, can someone who reads only the specs (no code, no history) tell what the API does now, and which document to trust?

**Method:**
- Each branch's `specs/` folder was exported with `git archive` into a folder named with a neutral code. The evaluator never saw run names, code, tests or expected answers.
- One fresh evaluator agent per branch, all using the same prompt and the same 5 questions, which were fixed before any run (brief).
- The evaluator had to quote file:line for every answer and report contradictions.
- The coordinator scored each answer against the code's actual behavior (ground truth, verified in each branch's routes, repository and passing tests).
- Scale: correct / stale (states old behavior) / conflicted (finds both, can't tell which is current) / not answerable.

**Questions:**
1. What happens when I save a link I have already bookmarked? What status code comes back?
2. When I save a duplicate, is the existing bookmark's title or tags changed?
3. How does the API decide two links are the same link?
4. Which document is the current, authoritative description of save behavior?
5. How does the list endpoint page through results?

## Results

| Run (code) | Approach | Q1 status code | Q2 unchanged | Q3 normalization | Q4 which doc to trust | Q5 paging | Correct |
|---|---|---|---|---|---|---|---|
| forward-r3 (m3) | Flow-forward | correct | correct | correct | **correct (high)** | correct | **5 / 5** |
| forward-r4 (n4) | Flow-forward | correct | correct | correct | **correct (high)** | correct | **5 / 5** |
| flowback-r1 (a1) | Flow-back | correct | correct | correct | conflicted (low) | correct | 4 / 5 |
| flowback-r2 (f2) | Flow-back | correct | correct | correct | conflicted (low) | correct | 4 / 5 |
| living-r1 (c1) | Living spec | correct | correct | correct | conflicted (low) | correct | 4 / 5 |
| living-r2 (g2) | Living spec | correct | correct | correct | conflicted (low) | correct | 4 / 5 |
| shortcut-r1 (d1) | Labelled arm | **conflicted** | correct | correct | not answerable | correct | 3 / 5 |
| forward-r1 (b1) | Arm: flow-forward, no analyze | correct | correct | correct | correct (high) | correct | 5 / 5 |
| forward-r2 (e2) | Arm: flow-forward, no analyze | correct | correct | correct | correct (high) | correct | 5 / 5 |

Every approach got the same score in both of its runs. Adding analyze did not change flow-forward's drift score (5/5 with and without it).

## What the evaluators said (short quotes)

- **Flow-forward:** the new folder states its own authority. 002's spec says it "Supersedes: the duplicate rule in FR-004 of specs/001-bookmarks-api", and forward-r4's spec says "where the two specs disagree about saving an already-bookmarked link, this spec wins". All four flow-forward evaluators named specs/002 as the source of truth with high confidence. Caveat: no single file covers all save behavior, and 001 still says 409 in full.
- **Flow-back and living spec:** the current rule is right in every file, and old lines are struck through or marked superseded. But no file says which document wins, so each evaluator inferred spec.md FR-004 and labelled that low confidence ("that is my inference, not a statement in the files").
- **Shortcut:** spec and tasks say 200, while the contract, quickstart and research still say 409 `duplicate_url`, and the contract lists no 200 for a save. Those files were outside what its rules let it edit (capture shortcut-r1/02-artifacts.md:258). The core question can't be answered from the specs.

## Reading the result honestly

- All six guide runs describe the current behavior correctly. The difference is only Q4: whether the documents say which one to trust. Flow-forward wins that because a new folder has to explain how it relates to the old one; the other two models edit in place and never need to.
- Spec Kit's docs predict the Q4 gap for flow-back: "future contributors may not know which artifact to trust" (spec-persistence.md l.87-89 at v1.2.2).
- Q4 is a fixable gap, not a property of the model. Tested (below): one sentence in spec.md flipped both flow-back and living spec to 5/5. Spec Kit's own page says the choice of model is "a team convention" best written in the constitution; this is the practical form of that advice.
- Flow-forward's 5/5 depends on the reader starting at 002. A reader who opens 001 gets the old 409 rule, and its quickstart fails. The test didn't measure that path.
- n = 2 per guide approach (plus 2 for the no-analyze forward arm) and 1 for the shortcut. This is a demonstration on one small API, not a benchmark.

## Fix test: one source-of-truth line (labelled arm, owner OK 2026-10-24)

The same flowback-r2 and living-r2 branches, plus one committed line after **Status** in spec.md:

> **Source of truth**: This spec.md is the authoritative description of this feature's behavior. plan.md, research.md, data-model.md, contracts/ and tasks.md are derived from it; where any of them disagrees with this file, this file wins.

New neutral codes, a fresh evaluator each time, the same prompt and questions.

| Branch | Before (Q4) | After (Q4) | Total before -> after |
|---|---|---|---|
| claude/ep03-flowback-r2-authority | conflicted (low) | correct (high): "spec.md. It says it wins over every other file." | 4/5 -> 5/5 |
| claude/ep03-living-r2-authority | conflicted (low) | correct (high), with the caveat that "Status: Draft" weakens it "somewhat" | 4/5 -> 5/5 |

Two side effects the evaluators raised:
- Once spec.md wins, its own vague wording becomes binding: it says "trailing slash" (singular), while the derived docs remove all trailing slashes, so the authoritative document doesn't settle `/docs//`.
- "Status: Draft" next to "authoritative" reads oddly. The line works best when the spec is also marked current.

n = 1 per arm.

Evaluator agents: 101,521 to 119,027 tokens each, 39 to 54 s.
