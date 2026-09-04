# HANDOFF — resume point for 3d-prompt-collection

**Read this first each new session, then `~/.claude/CLAUDE.md` for standing conventions.**
This file is the live "what to do next". There is no repo-level `CLAUDE.md` here.

Last updated: 2026-09-04.

## Current state

Run `git log -1 --oneline` for the current commit. Everything below is pushed.

`prompts.json` (63 prompts, 297,893 bytes) is unmodified upstream content from
`https://github.com/petergpt/3d-prompt-collection` and must stay that way.

Three files exist here that do not exist upstream:

- **`prompt-templates.html`** — about 637 KB, the deliverable. A meta-pattern analysis of
  the 63 prompts in six tabs: the pattern, the 63 deltas, the six families (sub-tabs A–F),
  blocks and word bank, write one, the source. Single file, no dependencies, dark mode.
  Deep links work: any anchor activates the tab and sub-tab holding it, opens the
  `<details>` if it is one, and jumps there instantly.
- **`build_deltas.py`** — regenerates the delta tab between the `<!-- DELTAS:BEGIN -->` and
  `<!-- DELTAS:END -->` markers. Idempotent. Run `python build_deltas.py` from the repo
  root after any change to `prompts.json`. Its CSS lives in the page's `<style>` block,
  outside the markers, so the two must be edited together.
- **`README.md`** — a 10 KB front page for the analysis. It was Peter's 307 KB index with
  all 63 prompts inline, which hid this repo's contribution; that index was deleted, not
  moved. Every count the README quotes is copied from the HTML, so the two move together.

Published. Remote `tutorial` = `az9713/3d-prompt-collection-tutorial`, public, and local
`main` tracks `tutorial/main`. `origin` still points at `petergpt/3d-prompt-collection`
and is never pushed to. GitHub Pages serves the repo root:
`https://az9713.github.io/3d-prompt-collection-tutorial/prompt-templates.html`.

`.gitignore` keeps `.ignore/cc*_3d_prompts.txt` untracked. Those are raw Git Bash session
dumps and must not be committed.

## Next task

None outstanding. Loose ends, if anyone wants them:

1. `.ignore/prompt-templates.html` is a tracked older copy of the root file. Duplicate
   weight, nothing links to it. Delete it if Simon agrees.
2. A hand-written one-line "what makes this one different" per prompt, on top of the
   mechanical delta header. Offered and not taken; it is 63 lines of editorial.

The page is 637 KB because all 63 prompt texts are embedded. That was deliberate and is
not a problem to fix: it keeps the file working from disk with no dependency on Peter's
repo.

## Numbers the generator produces, and how they were checked

`build_deltas.py` measures everything from `prompts.json`. Its output agrees with the
figures the document already carried, which is the check that it is segmenting correctly:
import-map standard 14, strict-code 8 (7 verbatim plus prompt 6, which reworded it as spec
bullets and is labelled *reworded*), ambition bar 7, no-front-end 37, closing line 16.
If a future edit makes any of those disagree, the segmenter broke — not the document.

Families come out A 27, B 5, C 14, D 4, E 6, F 7. The document names 42; the other 21 are
family A by one rule (five or more markdown headers and 5,900+ chars) and are marked
*by rule*. That rule never contradicts a doc-named family.

Spine parts present, out of 63: a 63, b 31, c 47, d 55, e 53, f 61, g 63, h 59. This is a
keyword rule, so it is the document's own inference and is labelled as such in the delta
tab. Never restate it as the source's own labelling.

**Two counts for part b coexist on purpose.** The pattern tab says 26, counting the formal
"must not be A, B, C or D" list. The delta tab says 31, because its rule also catches
prompts 6, 10, 12, 17 and 58, which forbid a shortcut in passing rather than in a list.
Both tabs and the README say so. Do not "fix" either number to match the other.

## How the annotation works, and its two guarantees

Every block of prompt text in the delta tab carries a letter saying which of the eight
parts it serves. A block takes the first part its own wording matches, in the priority
order d, b, h, e, g, c, f, so one block shows one letter. A block matching nothing
inherits the part above it and is drawn hollow. Counts: 935 direct, 433 inherited,
2 second letters.

Two assertions run at build time and must keep passing:

1. Every prompt reconstructs byte-for-byte from its annotated blocks. The annotation never
   reorders or edits the source text.
2. The set of parts in the gutter equals the set in the eight-cell strip, for all 63.
   A part can be present in a prompt yet lose every segment to a higher-priority part; a
   second pass reassigns it, and where even that would erase the part already there, the
   block carries a second smaller letter. That case occurs exactly twice.

Check both after any change to the segmenter:

```
python build_deltas.py --check
```

## Known accuracy corrections already applied — do not "re-fix" them

These were wrong at first and are now right. A session re-deriving them from memory rather
than from `prompts.json` may reintroduce the errors:

- The strict-code import block has **8** uses (prompts 6, 24, 25, 26, 35, 36, 37, 38), and
  belongs to family F plus prompt 6 — not to family B.
- The "Absolute ambition bar" paragraph has **7** uses: prompts 16, 18, **43**, 60, 61, 62,
  63. Prompt 43 sits outside family E and carries it anyway.
- Hex colour codes appear in **one** prompt only (17), not across family B.
- All four family D prompts (31, 39, 40, 41) end on exactly **four** adjectives. Prompt 41
  specifies "a smooth follow camera", not a chase camera.
- Family F (prompts 24, 25, 26, 35–38) is a real family the upstream README does not name.
  It was found by grepping for the strict-code import block and the `>=55 FPS` target.

## Where to read things

- `prompt-templates.html` — the deliverable. Tab 1 holds the spine and every count; tab 2
  the 63 deltas; tab 3 the six families and the six worked examples; tab 4 the blocks and
  word bank; tab 5 the 22-step procedure and 14-item checklist.
- `prompts.json` — the source of truth for every number. Re-scan it rather than trusting a
  recalled figure.
- `README.md` — this repo's front page. It summarises the analysis; it is no longer the
  upstream prompt index.
- Peter's README upstream — every prompt in full, with `#prompt-NN` anchors.

## Open question already put to Simon, still unanswered

`prompt-templates.html` uses em dashes and `·` separators throughout. These render
correctly in a browser but appear as `?` in a Windows terminal. Simon was asked whether to
swap them for plain ASCII and has not answered. Nothing is blocked by this.

## Session-transient scratch (regenerate; the durable record is the committed HTML)

Everything below lived in the scratchpad and is gone after a clear. Only rebuild it for
another large structural rewrite; for ordinary edits, edit `prompt-templates.html`
directly.

The rule that made both rewrites safe: **never retype a `<pre>` block.** Stash them, build
the new shell around placeholders, substitute them back, and assert byte-equality before
writing over the real file. That assertion is the point of the exercise; do not skip it.

1. `split.py` — regex every `<pre>…</pre>` out of the page into a list, replacing each with
   `{{PREn}}`, then cut the remaining text at its `<h2 id=…>` and `fam-head` markers into
   named parts. Saves `parts.json`.
2. `assemble.py` — builds the new page from those parts (tab bar, panels, sub-panels, the
   spine card, the delta markers, the CSS and the JS), then substitutes every `{{PREn}}`
   back and asserts each original block is present verbatim and every anchor id appears
   exactly once.
3. `original_backup.html` — a copy of the pre-rewrite page, used only to verify the 18
   code blocks survived. Keep one whenever restructuring.

## How to work here

- Verify counts against `prompts.json` with a scan. Never quote a figure from memory.
- Commit only when Simon asks. He does not use pull requests.
- All generated HTML is dark mode, per `~/.claude/CLAUDE.md`.
- Prose over bullets in explanatory text; keep procedures, tables and checklists as lists.
- After any edit to `build_deltas.py`, rerun it and rerun both assertions above.
