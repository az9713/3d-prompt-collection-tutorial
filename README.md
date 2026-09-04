# 3D Prompt Templates

Peter Gostev's [3d-prompt-collection](https://github.com/petergpt/3d-prompt-collection)
publishes 63 prompts that make a language model build a large, live 3D scene in Three.js.
This repository does not add prompts to that collection. It takes the collection apart and
asks a different question: what is the shared machine underneath all 63, and what changes
from one prompt to the next?

The answer is one document.

**Read it here: <https://az9713.github.io/3d-prompt-collection-tutorial/prompt-templates.html>**

It is a single self-contained HTML file. It names the parts every prompt is built from,
sorts the 63 into six families by length and packaging, extracts five text blocks you can
paste unchanged, and ends with a 22-step procedure and a 14-item pre-flight checklist for
writing a 64th prompt of your own. Six worked examples, written for this document and not
present in the source collection, show each family filled in.

## What the analysis found

The 63 prompts were not written 63 separate times. Whole sentences repeat, character for
character, across many of them, and identical text cannot be coincidence. The instruction
that loads the Three.js library appears in three fixed wordings, used 14, 12 and 8 times.
The paragraph beginning "Absolute ambition bar" appears 7 times with nothing changed.
Fifteen or more of the longer prompts end on the same two-sentence shape.

Below the level of exact sentences the same ideas recur. 62 of the 63 name Three.js. 58
ask for instancing. 50 carry an import-map instruction, 48 demand that everything be
procedural, and 48 clamp `devicePixelRatio`. 44 list camera presets, 42 restrict the
interface to something compact, 39 require the scene to be visibly alive, and 37 forbid a
title screen. Each count is a failure being blocked, not a stylistic preference.

Two devices do most of the work.

The first is that the writer never asks for a spectacular result without naming, in the
same breath, the engineering that pays for it. Density is always paired with instancing.
Fine detail is always paired with level of detail. Ambition is always paired with a laptop
frame rate. This closes an escape route: a model told only "make it dense" can draw a
hundred objects and call it dense, or draw a million and freeze the browser. Told both
halves at once, it has to find the third answer.

The second is the degrade order, and it is the sharpest sentence in the collection. Every
renderer eventually gives something up to keep running, and left alone it gives up whatever
is cheapest to remove, which is usually the thing the prompt was about. So 33 of the 63
prompts name the sacrifice order explicitly. Prompt 1 puts it this way: the quality selector
degrades far-window variation, traffic density and reflections *before ever degrading*
island completeness or landmark silhouettes. If you copy one sentence out of the whole
analysis, copy that one.

## The shared spine

All six families are built from the same eight parts, in the same order. Only length and
packaging change. A 532-character arcade prompt and a 12,527-character flagship prompt do
the same eight jobs; the short one does several of them in a single clause.

| # | Part | Job |
|---|---|---|
| a | Intent line | Verb first. Names the subject, the scale, the light and the moment. |
| b | Negative list | Four named shortcuts. "This must not be A, B, C or D." |
| c | Goal plus means | An impossible density, then the technique that pays for it. |
| d | Technical boilerplate | Import map. Procedural. No external files. |
| e | First frame | What fills the screen at second zero. No menus. |
| f | World and life | Named landmarks. Four or five independent moving systems. |
| g | Controls | Presets, three compact controls, photo mode, reset. |
| h | Performance and outcome | Detail tiers, degrade order, laptop target, one payoff sentence. |

## The six families

Choose a family by how long you want the prompt to be, not by what the subject is. Any
subject fits any family. Manhattan appears as a 6,719-character flagship in prompt 1 and as
a 699-character arcade game in prompt 31. Giza appears three times over: as a specification
in prompt 17, as a dense four-paragraph prompt in prompt 16, and as an arcade game in
prompt 40.

| Family | Length | Shape | Example prompts |
|---|---|---|---|
| A - Flagship | 6,000-12,500 | Full section headers, every part present. | 1, 5, 45, 50, 51 |
| B - Spec | 1,200-4,900 | An engineering work order. Objective, then specifications. | 2, 6, 17, 19, 27 |
| C - Single idea | 2,600-3,500 | One sentence carries the scene. Four short sections support it. | 20-23, 28-30, 53-59 |
| D - Arcade | 532-699 | Five sentences. Pure fill-in. | 31, 39, 40, 41 |
| E - Ambition bar | 2,700-3,300 | Four dense paragraphs, no headers. | 16, 18, 60-63 |
| F - Landmark card | 1,476-2,330 | Terse topic headers. Strict-code block. Named frame-rate target. | 24, 25, 26, 35-38 |

Family F is a real family that the source README does not name. It was found by grepping
for a strict-code import block and a stated 55 FPS target. Membership is a matter of form,
not of blocks used: prompt 43 sits in family A by its body and still carries the family E
ambition-bar paragraph. That paragraph travels well, and adding it to any family raises the
floor.

## Blocks you can paste unchanged

| Block | Uses |
|---|---|
| Import map, standard wording | 14 |
| Import map, strict-code wording | 8 (prompts 6, 24, 25, 26, 35, 36, 37, 38) |
| The ambition bar paragraph | 7 (prompts 16, 18, 43, 60, 61, 62, 63) |
| The no-front-end clause | 37 prompts carry a version |
| The closing line | 15 or more |

A word bank in the document supplies the parts that do change: ambition adjectives for the
opening slot, the negative list drawn from 26 prompts, controls from the 42 that restrict
them, camera presets from the 44 that list them, and performance wording from the 58, 39
and 33 that demand it.

## Files

| File | What it is |
|---|---|
| `prompt-templates.html` | The analysis. Eight sections, six families, six worked examples, the procedure and the checklist. Single file, no dependencies, dark mode. |
| `prompts.json` | The 63 source prompts, unmodified, as they arrived from the original repository. |

## Source

The 63 prompts analysed here are Peter Gostev's, from
<https://github.com/petergpt/3d-prompt-collection>. `prompts.json` in this repository is his
file, unchanged. His README lists every prompt in full with `#prompt-NN` anchors, so any
prompt number cited in the analysis can be read there. The analysis, the families, the
templates and the worked examples are this repository's contribution.
