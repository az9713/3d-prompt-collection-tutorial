# HANDOFF — resume point for 3d-prompt-collection

**Read this first each new session, then `~/.claude/CLAUDE.md` for standing conventions.**
This file is the live "what to do next". There is no repo-level `CLAUDE.md` here.

Last updated: 2026-09-04.

## Current state (as of local HEAD `f8fd6b5`)

The prompts came from `https://github.com/petergpt/3d-prompt-collection`. `prompts.json`
(63 prompts, 297,893 bytes) is unmodified upstream content and should stay that way.

Two things exist here that do not exist upstream:

- **`prompt-templates.html`** - 84,203 bytes, complete. The meta-pattern analysis of the 63
  prompts: eight-part spine, six families, five paste-unchanged blocks, a word bank, a
  22-step procedure, a 14-item checklist, six worked examples. Dark mode, single file, no
  dependencies. Commits `ed5909b` (first version), `794b60a` (prose rewrite), `63add03`
  (source links).
- **`README.md`** - rewritten at `f8fd6b5`. It was Peter's 307 KB index with all 63 prompts
  inline, which hid this repo's contribution. It is now a 6.7 KB front page for the
  analysis. The old index was deleted, not moved; `prompts.json` and Peter's README carry
  the prompts.

Published and pushed. Remote `tutorial` = `az9713/3d-prompt-collection-tutorial`, public.
`origin` still points at `petergpt/3d-prompt-collection` and is never pushed to. Local
`main` tracks `tutorial/main`. GitHub Pages serves the repo root, so the deliverable
renders at
`https://az9713.github.io/3d-prompt-collection-tutorial/prompt-templates.html` (verified
200, 83,060 bytes).

`.gitignore` keeps `.ignore/cc*_3d_prompts.txt` untracked. Those are raw Git Bash session
dumps and must not be committed.

## Next task

None outstanding. Two loose ends if anyone wants them:

1. `.ignore/prompt-templates.html` is a tracked older copy of the root file. It is
   duplicate weight and nothing links to it. Delete it if Simon agrees.
2. The README quotes counts taken from the HTML. If the HTML's numbers ever change,
   the README must change with it. Re-scan `prompts.json`; never quote from memory.

## Open question already put to Simon, still unanswered

`prompt-templates.html` uses em dashes and `·` separators throughout. These render
correctly in a browser but appear as `?` in a Windows terminal. Simon was asked whether
to swap them for plain ASCII and has not answered. Nothing is blocked by this.

## Known accuracy corrections already applied — do not "re-fix" them

Three claims in the document were wrong at first and are now correct. If a future
session re-derives them from memory rather than from `prompts.json`, it may reintroduce
the errors:

- The strict-code import block has **8** uses (prompts 6, 24, 25, 26, 35, 36, 37, 38),
  and belongs to family F plus prompt 6 — not to family B.
- The "Absolute ambition bar" paragraph has **7** uses: prompts 16, 18, **43**, 60, 61,
  62, 63. Prompt 43 sits outside family E and carries it anyway.
- Hex colour codes appear in **one** prompt only (17), not across family B.
- All four family D prompts (31, 39, 40, 41) end on exactly **four** adjectives.
  Prompt 41 specifies "a smooth follow camera", not a chase camera.

Family F (prompts 24, 25, 26, 35–38) is a real family that the README does not name.
It was found by grepping for the strict-code import block and the `>=55 FPS` target.

## Where to read things

- `prompt-templates.html` — the deliverable. Section 2 holds every count; section 4
  the six families; sections 5–10 the templates and examples.
- `prompts.json` — the source of truth for every number. Re-scan it rather than
  trusting a recalled figure.
- `README.md` — the upstream index. Groups the 63 prompts by subject, not by form.

## Session-transient scratch (regenerate; the durable record is the committed HTML)

The prose rewrite used a three-step pattern so the 18 template and worked-example
blocks survived byte-identical instead of being retyped. Both scratch files are gone.
Rebuild the pattern if another large rewrite of this page is needed:

1. Extract every `<pre>` body from `prompt-templates.html` into `.pre_blocks.json`,
   keyed by index, recording whether each carried `class="wrapped"`.
2. Write a new shell HTML to the scratchpad with `{{PRE0}}`…`{{PRE17}}` placeholders
   where the code blocks belong.
3. Substitute the saved bodies back in, then assert every block matches its original
   byte for byte before writing over the real file.

Step 3's assertion is the point of the whole exercise. Do not skip it.

## How to work here

- Verify counts against `prompts.json` with a scan. Never quote a figure from memory.
- Commit only when Simon asks. He does not use pull requests.
- All generated HTML is dark mode, per `~/.claude/CLAUDE.md`.
- Prose over bullets in explanatory text; keep procedures and checklists as lists.
