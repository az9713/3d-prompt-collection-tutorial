# HANDOFF — resume point for 3d-prompt-collection

**Read this first each new session, then `~/.claude/CLAUDE.md` for standing conventions.**
This file is the live "what to do next". There is no repo-level `CLAUDE.md` here.

Last updated: 2026-09-04.

## Current state (as of local HEAD `63add03`)

The repo is a clone of `https://github.com/petergpt/3d-prompt-collection`. It arrived
with two files, `prompts.json` (63 prompts, 297,893 bytes) and `README.md`. Neither
has been modified.

One new file was added and finished this session:

- **`prompt-templates.html`** — 83,060 bytes, complete. A meta-pattern analysis of the
  63 prompts, rewritten as plain-English prose, with six fill-in templates and six
  worked examples. Dark mode, single file, no external dependencies. It links back to
  the source repo, to `prompts.json` and to the raw file; all three URLs returned 200
  when checked.
  - `ed5909b` — first version, bullet-heavy.
  - `794b60a` — rewritten as prose. Explanatory bullets became paragraphs; data tables,
    the 22-step procedure and the 14-item checklist stayed as lists, per Simon's choice.
  - `63add03` — source links added.

Working tree is clean apart from `.ignore/cc1_3d_prompts.txt`, which is known untracked
noise and should stay untracked.

## Next task

**Decide whether to push, and where.** This is the only open item. Nothing else is
outstanding.

Local `main` is 3 commits ahead of `origin/main`. `origin` is
`petergpt/3d-prompt-collection`, which is somebody else's repository — the git identity
here is `az9713`, not `petergpt`. So a push would be writing to a third party's public
repo, and push rights have never been tested. Do not push without Simon saying so.

Three options, in the order they are likely to be wanted:

1. **Fork and push to Simon's own remote.** Keeps the work public and attributable
   without touching someone else's repo.
2. **Push to `origin` as-is.** Only if Simon confirms he has write access there.
3. **Leave it local.** The HTML works fully from disk; its outbound links resolve
   regardless of whether the page itself is ever published.

Verify any push actually landed:

```
git rev-parse --short HEAD
git ls-remote origin main | head -1     # must match
```

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
