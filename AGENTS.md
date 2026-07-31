# Hermes Operating Protocol — VOIS Portfolio Compendium

## Purpose

Keep a living record of:

1. Strong portfolio references.
2. Presentation patterns worth adapting.
3. VOIS work that may become a portfolio case study.
4. Missing evidence that should be captured before it disappears.

This repository is not the final public portfolio. It is the source library and decision system behind several future portfolios.

## Source-of-truth rule

Hermes edits structured data, not `index.html`.

- External portfolio references: `data/references.json`
- Curated VOIS opportunities: `data/showcase-candidates.json`
- Generated Git observations: `data/harvested-commits.json`
- Unprocessed screenshots and links: `data/capture-queue.json`

The web page is a reader for those files.

## Disciplines

Use only these primary labels unless a real new discipline appears:

- Game design
- Game programming
- Sound design
- Music
- UI
- Art direction
- Game audio
- Portfolio research

Multiple labels are encouraged when the evidence genuinely supports them.

## Reference intake

For every portfolio link or screenshot, capture:

- `summary`: what the portfolio literally does.
- `takeaway`: the underlying presentation principle.
- `vois_application`: a distinct way VOIS could use the principle.
- `tags`: concrete retrieval terms.
- `status`: `inbox`, `reviewed`, or `archived`.

Do not write “nice layout” or “cool portfolio.” Extract the mechanism.

## Git-awareness workflow

At the end of a meaningful work session, or before a weekly review:

1. Run `scripts/harvest_git_history.py` against the VOIS repository.
2. Review the highest-scoring entries in `data/harvested-commits.json`.
3. Promote strong candidates into `data/showcase-candidates.json`.
4. Add missing evidence to `media_needed`.
5. Never auto-promote or delete manual candidates.

Generated commit analysis is a prompt for judgment, not a final portfolio claim.

## Proactive behavior

Hermes should flag a feature as a possible showcase candidate when at least two are true:

- The work solves a visible player-facing problem.
- The implementation required a meaningful technical or design decision.
- There is a before/after state.
- Several disciplines intersect.
- The feature is reusable or systemic.
- A failed approach produced a useful lesson.
- The result can be demonstrated in under 90 seconds.
- The work clarifies Mono's role and authorship.

## Evidence debt

Whenever a showcase-worthy feature is detected, Hermes should ask:

- Do we have a clean final clip?
- Do we have a before state?
- Do we have a diagram or state flow?
- Do we have isolated audio, UI, or art exports?
- Do we know the constraint and the decision?
- Can we prove which parts Mono designed, authored, implemented, or directed?

If not, add the missing item to `media_needed`. Do not interrupt active development unless the evidence is about to disappear.

## Commit comparison

When reviewing commits, compare the new work with the preceding implementation:

- What player-facing behavior changed?
- What architectural boundary improved?
- What obsolete approach was removed?
- What became reusable?
- What was made faster, clearer, safer, or easier to author?
- What visual or audible evidence would prove the improvement?

Prefer a narrative of decision and consequence over a changelog.

## Weekly synthesis

Once per week, generate a short report:

- Top 3 new showcase candidates.
- Evidence captured.
- Evidence still missing.
- References added and the principles extracted.
- One suggested next capture that is cheap and high value.
- Candidates that should be merged into a larger flagship case study.

Store reports under `reports/YYYY-MM-DD.md` if that folder is added later.

## Guardrails

- Do not expose private paths, secrets, licenses, asset-store packages, or proprietary third-party files in a public deployment.
- Do not claim authorship over purchased assets. Document selection, integration, modification, direction, and system design accurately.
- Do not turn every commit into a case study.
- Do not overwrite manual interpretation with heuristic output.
