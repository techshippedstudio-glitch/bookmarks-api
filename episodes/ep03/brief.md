<!-- Copy of the episode brief as saved in the project on 2026-10-24T09:45:20.992014Z (before the first run started at 2026-10-24T11:41Z). The blind-test questions are in 'Proof plan'. -->

# Episode 3 brief: Spec Kit After the MVP: 3 Ways Specs Evolve

Status: briefed (build not started). Series: After the MVP (#1). Format: F2 (Receipts: head-to-head of
three approaches on the same task). Target: 12-16 min. Audience: SDD/agentic coding practitioners.
Gates: G1: 2026-10-24, title approved; change request confirmed 2026-10-24 (duplicate save returns 200) | G2: | G3:

## Viewer question

"How do I keep specs true after the first version?" Evidence: most-liked request on Den Delimarsky's
Spec Kit guide is moving past the MVP (137 likes); "specs slowly become obsolete" and "we finally
invented waterfall" (869 likes) in critique threads. Search: "spec driven development" about 93k/month
(+20%) per the brief's 2026-10-24 vidIQ pull (the landscape report shows 87.7k, +9.7%; the fact-checker
settles which to quote), "spec kit" about 32k (+12%); "spec kit existing project" and "living spec" under
750. So package with "Spec Kit" and the problem, and teach the model names inside.

## Stands alone (becomes "the setup" chapter, 30-45 s)

We have a small bookmarks API: you save a link, you list your links. It was built with GitHub Spec Kit,
which keeps a written spec, a plan and a task list next to the code. Today one rule changes: saving a link
you already saved used to be rejected with an error; now it should just return the bookmark you already
have. The question is what happens to the written spec when the code changes.

## Source topic

https://github.github.com/spec-kit/concepts/spec-persistence.html - three models for what happens to
spec.md / plan.md / tasks.md when requirements change. The page says the choice is a team convention,
not a CLI setting, and names no default.

- Flow-back: edit any artifact or code, reconcile manually. Fast; risk: silent divergence.
- Flow-forward: finished feature folders are immutable; changes get a new feature folder. Audit trail;
  risk: fragmented context.
- Living spec: update spec.md first, regenerate plan/tasks. Consistency; risk: lost rationale.

## Proof plan

- Starting point: tag `ep03-start` = `ep02-converged`. Postgres per HANDOFF.
- Change request (confirmed by the owner 2026-10-24): saving a link that is already bookmarked returns the existing
  bookmark with 200 instead of 409 (changes FR-004, the contract, code and tests).
- Runs: 7, each by a fresh build-runner agent: `flowback` r1-r2, `forward` r1-r2, `living` r1-r2, and
  `shortcut` r1 (owner decision 2026-10-24). Run in rounds so every approach faces the same conditions:
  round 1 = flowback-r1, forward-r1, living-r1, shortcut-r1; round 2 = flowback-r2, forward-r2,
  living-r2. Branches `claude/ep03-<slug>-r<run>`; the owner pushes them as `ep03/<slug>-r<run>` with tags
  `ep03-<slug>-r<run>-<step>`.
- How a run "runs a command": read `.claude/skills/speckit-<command>/SKILL.md` and carry out its
  instructions exactly, with the change request as the arguments. Where a command would ask the user a
  question, answer only from the change request and record the question and answer in the capture.
- Approach rules (from Spec Kit's docs/guides/evolving-specs.md and concepts/spec-persistence; the
  build-runner follows these even when another way seems better):
  - flowback (by the guide, 2 runs): the change starts where the need shows up, here as a code fix with
    tests. Then record the change in the artifact closest to the work, update every artifact that now
    conflicts (spec.md, plan.md, tasks.md, contracts), run `/speckit-analyze` on `specs/001-bookmarks-api`
    (set `SPECIFY_FEATURE_DIRECTORY`), resolve its findings, then run `/speckit-converge`.
  - shortcut (1 run, labelled "flow-back, skipping the guide's checks"): change the code and tests first,
    the way a quick fix happens, then update spec.md, plan.md and tasks.md by hand in one pass. No analyze,
    no converge. This shows how drift creeps in when the guide's steps are skipped; the video must say the
    guide includes an analyze step.
  - forward (2 runs): treat `specs/001-bookmarks-api` as finished and immutable; never edit it. Run
    `/speckit-specify` (it creates the next numbered folder), `/speckit-plan`, `/speckit-tasks`,
    `/speckit-implement`, then `/speckit-converge`, repeating implement and converge until converged. Link
    the new folder to 001 in its spec, as the guide advises.
  - living (2 runs): set `SPECIFY_FEATURE_DIRECTORY=specs/001-bookmarks-api`; edit `spec.md` first (a
    manual edit, which the guide allows instead of `/speckit-clarify`); rerun `/speckit-plan` and
    `/speckit-tasks`; run `/speckit-analyze`; run `/speckit-implement`; then `/speckit-converge`, repeating
    implement and converge until converged. Preserve any rationale from the old plan that still matters.
- Measurements per run: model, wall-clock per step, tokens and cost (or "not measured" and why), files
  changed, tests (Python 3.11-3.13), analyze and converge results.
- Blind drift test (fixed now, before any run): a fresh evaluator reads only that branch's `specs/` folder
  and answers:
  1. What happens when I save a link I have already bookmarked? What status code comes back?
  2. When I save a duplicate, is the existing bookmark's title or tags changed?
  3. How does the API decide two links are the same link?
  4. Which document is the current, authoritative description of save behavior?
  5. How does the list endpoint page through results? (control question: should not change)
  The coordinator scores each answer against the code's real behavior into `episodes/ep03/drift-score.md`.
- Boring-result risk: all three by-the-guide approaches end up consistent. That is a real result (the
  guide works) and the shortcut run shows the contrast; we report whatever happens.

## Packaging

- Titles: "Spec Kit After the MVP: 3 Ways Specs Evolve" (approved); alternates for Test & Compare: "Spec
  Kit After the MVP: Keep Specs True", "Your Specs Will Rot. 3 Ways to Stop It".
- Hook (confirm after the build): "Same change, three ways. One left our specs lying. Here's the one we're
  keeping."
- Chapters (draft): the drift problem; the setup; the three models; flowback run; forward run; living spec
  run; results side by side; the drift test; how to choose; what we picked.
- Full-motion scenes: cold open, three-models diagram, drift test (answers flip to stale), results table,
  decision flowchart. Code and terminal sections in the PIL renderer.
- Thumbnail concept: three spec files, two cracked, one intact. Short: "specs rot: the 20-second test".

## Review

- Spec Kit SME review (sources only: persistence and related concept pages, installed 1.2.2 command
  instructions, changelog, GitHub issues and discussions) before G2. Must not imply the docs recommend a
  model.

## Open decisions for the owner

1. ~~Confirm the change request~~ Confirmed 2026-10-24.
2. End by picking one model for this repo (leaning living spec plus a decision log, if the numbers
   support it)?
