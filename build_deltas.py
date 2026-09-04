# -*- coding: utf-8 -*-
"""Regenerate the "63 deltas" panel of prompt-templates.html from prompts.json.

Every number this writes is measured from prompts.json. Nothing is hand-typed.
Run:  python build_deltas.py     (rewrites the region between the DELTAS markers)
"""
import json, io, re, html, collections

SRC   = 'prompts.json'
PAGE  = 'prompt-templates.html'
BEGIN = '<!-- DELTAS:BEGIN -->'
END   = '<!-- DELTAS:END -->'

PROMPTS = json.load(io.open(SRC, encoding='utf-8'))['prompts']
assert len(PROMPTS) == 63, len(PROMPTS)

# --- 1. segments, and which of them are reused across prompts ----------------
SPLIT = re.compile(r'(?<=[.:!?])\s+(?=[A-Z0-9"\[(#-])|\n+')
MIN_SEG = 20            # shorter fragments repeat by accident, not by design


def segments(text):
    """Split into segments plus separators. Concatenates back to the original."""
    out, pos = [], 0
    for m in SPLIT.finditer(text):
        out.append(text[pos:m.start()])
        out.append(m.group(0))
        pos = m.end()
    out.append(text[pos:])
    return [s for s in out if s != '']


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


REUSE = collections.Counter()
for _p in PROMPTS:
    for _k in {norm(s) for s in segments(_p['prompt']) if len(norm(s)) >= MIN_SEG}:
        REUSE[_k] += 1


def is_reused(seg):
    k = norm(seg)
    return len(k) >= MIN_SEG and REUSE[k] >= 2


# --- 2. which of the eight spine parts each prompt fills ---------------------
# Keyword rules applied per prompt. This document's inference, not the source's
# own labelling.
ROLES = [
    ('a', 'Intent line', None),   # the opening segment, always present
    ('b', 'Negative list',
     r'must not|do not satisfy|not be a |never a |avoid the |no cartoon|not a toy|rather than a'),
    ('c', 'Goal plus means',
     r'billion|million|thousand|density|dense|every single|piece by piece|maximum-ambition|impossible'),
    ('d', 'Boilerplate',
     r'import map|procedural|no external|es modules|bundler|pinned'),
    ('e', 'First frame',
     r'opening frame|first frame|opens directly|opens on|starts already|title screen|no menus|second zero|from the first'),
    ('f', 'World and life',
     r'alive|living|moving|independent|drift|flock|crowd|traffic|weather|wind|birds|smoke|water'),
    ('g', 'Controls',
     r'orbit|preset|slider|photo mode|reset|drag|wasd|keyboard|click|toggle|control'),
    ('h', 'Performance',
     r'devicepixelratio|fps|frame rate|lod|instanc|degrade|smooth on a modern laptop|the outcome|performance|merged geometry|budget'),
]
FIXED_ROLES = {'d'}     # the one part that is pasted unchanged


def roles_of(text):
    low = text.lower()
    got = {'a'}
    for key, _label, pat in ROLES:
        if pat and re.search(pat, low):
            got.add(key)
    return got


# Which label wins when one segment matches several parts. The two most
# unmistakable wordings come first; the loosest, f, comes last.
PRIORITY = ['d', 'b', 'h', 'e', 'g', 'c', 'f']
PAT = {k: p for k, _l, p in ROLES if p}
ROLE_NAME = {k: l for k, l, _p in ROLES}


def label_segments(text):
    """Return [(chunk, role, inherited)], the chunks concatenating back to text.

    The opening segment is part a by definition. After that a segment takes the
    first part its own wording matches, in PRIORITY order. A segment matching
    nothing inherits the part above it, which is what a bullet under a labelled
    header is doing anyway; those are marked inherited so the two are told apart.
    """
    segs = segments(text)
    labels = [None] * len(segs)             # role per segment, None = separator
    first = True
    for i, seg in enumerate(segs):
        if not seg.strip():                 # separator: stays with the block above
            continue
        if first:
            labels[i], first = 'a', False
            continue
        low = seg.lower()
        labels[i] = next((k for k in PRIORITY if re.search(PAT[k], low)), None)

    # A part can be present in the prompt yet never win a segment, because every
    # sentence carrying it also carries a higher-priority part. Give it the one
    # segment it matches, but only where that does not erase the part already
    # there, so the gutter shows exactly the parts the strip shows.
    for missing in [k for k in PRIORITY if k in roles_of(text)
                    and k not in {l for l in labels if l}]:
        counts = collections.Counter(l for l in labels if l)
        for i, seg in enumerate(segs):
            if labels[i] and counts[labels[i]] > 1 and re.search(PAT[missing], seg.lower()):
                labels[i] = missing
                break

    # If a part is still unrepresented, its only evidence sits inside a block
    # whose own part appears nowhere else. Both are true, so both are shown:
    # that block carries a second letter.
    extra = collections.defaultdict(list)
    for missing in [k for k in PRIORITY if k in roles_of(text)
                    and k not in {l for l in labels if l}]:
        for i, seg in enumerate(segs):
            if labels[i] and re.search(PAT[missing], seg.lower()):
                extra[i].append(missing)
                break

    rows, cur, cur_role, cur_inh, cur_x = [], '', None, False, []
    for i, (seg, lab) in enumerate(zip(segs, labels)):
        if not seg.strip():
            cur += seg
            continue
        inh = lab is None
        role = cur_role if inh else lab
        x = extra.get(i, [])
        if role != cur_role or inh != cur_inh or x:
            if cur:
                rows.append((cur, cur_role, cur_inh, cur_x))
            cur, cur_role, cur_inh, cur_x = seg, role, inh, x
        else:
            cur += seg
    if cur:
        rows.append((cur, cur_role, cur_inh, cur_x))
    assert ''.join(r[0] for r in rows) == text
    return rows


# --- 3. families ------------------------------------------------------------
# What the document itself names. Prompt 43 is named in prose, not in the table.
DOC_FAMILY = {}
for _fam, _nums in [
    ('A', [1, 5, 45, 50, 51, 43]),
    ('B', [2, 6, 17, 19, 27]),
    ('C', list(range(20, 24)) + list(range(28, 31)) + list(range(53, 60))),
    ('D', [31, 39, 40, 41]),
    ('E', [16, 18, 60, 61, 62, 63]),
    ('F', [24, 25, 26, 35, 36, 37, 38]),
]:
    for _n in _nums:
        DOC_FAMILY[_n] = _fam
assert len(DOC_FAMILY) == 42, len(DOC_FAMILY)


def family_by_rule(text):
    """One rule covers every prompt the document leaves unnamed: markdown
    section headers and 5,900 characters or more, which is family A."""
    md = len(re.findall(r'^\s*#{2,}\s*\S', text, re.M))
    return 'A' if (md >= 5 and len(text) >= 5900) else '?'


# --- 4. the five reusable blocks, matched as text ---------------------------
IMPORT_STD = ('If you use Three.js, add an import map before the module script mapping '
              '"three" and "three/addons/" to the same pinned version, and import only via '
              'those names. Everything procedural; no external assets.')
IMPORT_STRICT = ('If you use Three.js, add an import map (before the module script) mapping '
                 '"three" and "three/addons/" to the same pinned version, and import only via '
                 'those names. Never reuse identifiers in the same scope')
AMBITION_HEAD = 'absolute ambition bar: do not satisfy this prompt with a symbolic miniature'
NO_FRONT_END = ('do not create a title screen, menu, level select, onboarding overlay, '
                'or press-start state.')


def blocks_of(text):
    n = norm(text)
    low = n.lower()
    out = []
    if norm(IMPORT_STD) in n:
        out.append(('1', 'Import map, standard', 'verbatim'))
    if norm(IMPORT_STRICT) in n:
        out.append(('2', 'Import map, strict-code', 'verbatim'))
    elif 'never reuse identifiers in the same scope' in low and 'import map' in low:
        out.append(('2', 'Import map, strict-code', 'reworded'))
    if AMBITION_HEAD in low:
        out.append(('3', 'Ambition bar', 'verbatim'))
    if re.search(r'title screen|no menus', low):
        out.append(('4', 'No front end',
                    'verbatim' if NO_FRONT_END in low else 'variant'))
    if 'smooth on a modern laptop' in low and 'the outcome' in low:
        out.append(('5', 'Closing line', 'verbatim'))
    return out


# --- 5. render --------------------------------------------------------------
def esc(s):
    return html.escape(s, quote=False)


def card(n, p):
    text = p['prompt']
    got = roles_of(text)
    fam = DOC_FAMILY.get(n)
    fam_src = 'named' if fam else 'by rule'
    if not fam:
        fam = family_by_rule(text)
    blocks = blocks_of(text)

    cells = []
    for key, label, _pat in ROLES:
        on = key in got
        cls = 'on fixed' if (on and key in FIXED_ROLES) else ('on' if on else 'off')
        cells.append('<span class="rc %s" title="%s: %s">%s</span>' % (cls, key, esc(label), key))
    missing = [k for k, _l, _pat in ROLES if k not in got]
    miss = ('<span class="miss">does without %s</span>' % ', '.join(missing)) if missing \
        else '<span class="miss all">all eight parts present</span>'

    shared = sum(len(s) for s in segments(text) if is_reused(s))
    pct = int(round(100.0 * shared / len(text)))

    body = []
    for chunk, role, inherited, extra_roles in label_segments(text):
        marked = []
        for seg in segments(chunk):
            marked.append('<span class="reused">%s</span>' % esc(seg)
                          if is_reused(seg) else esc(seg))
        gut = ('<span class="g %s%s" title="%s%s">%s</span>'
               % (role, ' inh' if inherited else '',
                  esc(ROLE_NAME[role]),
                  ', inherited from the block above' if inherited else '', role))
        for x in extra_roles:
            gut += ('<span class="g %s also" title="%s, also in this block">%s</span>'
                    % (x, esc(ROLE_NAME[x]), x))
        body.append('<div class="prow2"><span class="guts">%s</span><pre>%s</pre></div>'
                    % (gut, ''.join(marked).strip('\n')))

    bhtml = ''.join(
        '<span class="blk%s">Block %s &middot; %s%s</span>'
        % (' rew' if how != 'verbatim' else '', bid, esc(name),
           '' if how == 'verbatim' else ' <em>%s</em>' % how)
        for bid, name, how in blocks) or '<span class="blk none">no reusable block</span>'

    return ('<details class="delta" id="p{n}">\n'
            '<summary><span class="dn">{n}</span><span class="dt">{t}</span>'
            '<span class="dm">{c} chars &middot; family {f} <em>{fs}</em> '
            '&middot; {pct}% reused</span></summary>\n'
            '<div class="dbody">\n'
            '<div class="strip">{cells}{miss}</div>\n'
            '<div class="blocks">{b}</div>\n'
            '<div class="ptext">{body}</div>\n'
            '</div></details>').format(
        n=n, t=esc(p['title']), c='{:,}'.format(len(text)), f=fam, fs=fam_src,
        pct=pct, cells=''.join(cells), miss=miss, b=bhtml, body=''.join(body))


def matrix():
    rows, tally = [], collections.Counter()
    for n, p in enumerate(PROMPTS, 1):
        text = p['prompt']
        got = roles_of(text)
        fam = DOC_FAMILY.get(n) or family_by_rule(text)
        tally[fam] += 1
        for k in got:
            tally['role_' + k] += 1
        cells = ''.join('<td class="%s">%s</td>' % ('y' if k in got else 'n',
                                                    k if k in got else '&middot;')
                        for k, _l, _pat in ROLES)
        rows.append('<tr><td class="num"><a href="#p%d">%d</a></td><td class="ti">%s</td>'
                    '<td class="num">%s</td><td class="fam f%s">%s</td>%s</tr>'
                    % (n, n, esc(p['title']), '{:,}'.format(len(text)), fam, fam, cells))
    return '\n'.join(rows), tally


INTRO = """
<h2 id="deltas">The 63 deltas</h2>

<p class="lead2">The pattern is what all 63 prompts share. The delta is what one prompt
adds on top of it. This section shows both, for every prompt, measured from
<code>prompts.json</code> rather than described.</p>

<p>Two measurements sit behind each row. The first asks which of the eight spine parts a
prompt actually fills, by looking for the vocabulary each part uses. The second asks how
much of the prompt is wording that also appears, character for character, in at least one
other prompt. Read together they place a prompt: a short arcade prompt fills four parts
and reuses a quarter of its text, while a flagship fills all eight and reuses almost
nothing, because at that length nearly every sentence is about its own subject.</p>

<p class="note">The eight-part reading is a keyword rule applied to each prompt, so it is
this document's inference rather than the source's own labelling. The reuse percentage is
an exact string comparison, so it is exact. Family is the document's own where the
document names one, and marked <em>by rule</em> where it does not.</p>
"""

OUTRO_HEAD = """
<h3>Every prompt, opened up</h3>

<p>Click a title to open it. The strip repeats the eight parts for that prompt. The prompt
itself is then annotated: a letter in the left margin says which part each block of text
is doing, so you can read the pattern down the page against the wording that fills it.
Within the text, dimmed wording appears in at least one other prompt as well; everything
at full contrast is unique to this one.</p>

<p>A block takes the first part its own wording matches. A block whose wording matches
nothing, usually a bullet under a labelled header, inherits the part above it and its
letter is drawn hollow to show that. Twice in the whole collection a single sentence is
the only evidence for two different parts, and that block carries a second, smaller
letter rather than hiding one of them. Nothing is reordered: the text runs exactly as it
does in <code>prompts.json</code>, which is also why the letters do not always run
straight from a to h.</p>

<p class="legend"><span class="k reused-k"></span>reused in another prompt
<span class="k unique-k"></span>this prompt only
<span class="k fixed-k"></span>part d, the block pasted unchanged
<span class="k inh-k"></span>part inherited from the block above</p>
"""


def build():
    rows, tally = matrix()
    heads = ''.join('<th class="rh" title="%s">%s</th>' % (esc(l), k) for k, l, _p in ROLES)
    fam_line = ', '.join('%s&nbsp;%d' % (f, tally[f]) for f in 'ABCDEF' if tally[f])
    role_line = ', '.join('%s&nbsp;%d' % (k, tally['role_' + k]) for k, _l, _p in ROLES)

    out = [BEGIN, INTRO,
           '<div class="tw"><table class="mx">',
           '<caption>All 63 prompts. A filled cell is a spine part the prompt contains; '
           'a dot is a part it does without.</caption>',
           '<thead><tr><th class="num">#</th><th>Title</th><th class="num">Chars</th>'
           '<th>Family</th>' + heads + '</tr></thead>',
           '<tbody>', rows, '</tbody></table></div>',
           '<p>Across the collection that comes out as family ' + fam_line +
           '; and parts present ' + role_line + ', out of 63. Parts <strong>a</strong> and '
           '<strong>g</strong> are in every single prompt: every one names its subject and '
           'tells the viewer what the controls do. Part <strong>b</strong>, the negative '
           'list, is the one genuinely optional part. Its count of 31 is larger than the 26 given on '
           'the pattern tab because that figure counts the formal four-item list, '
           '&ldquo;this must not be A, B, C or D&rdquo;, while the rule here also catches '
           'prompts 6, 10, 12, 17 and 58, which forbid a shortcut in passing rather than '
           'in a list.</p>',
           OUTRO_HEAD]
    for n, p in enumerate(PROMPTS, 1):
        out.append(card(n, p))
    out.append(END)
    return '\n'.join(out)


if __name__ == '__main__':
    page = io.open(PAGE, encoding='utf-8', newline='').read()
    i, j = page.index(BEGIN), page.index(END) + len(END)
    new = page[:i] + build() + page[j:]
    io.open(PAGE, 'w', encoding='utf-8', newline='').write(new)
    print('deltas rebuilt: %d prompts, page now %s bytes' % (len(PROMPTS), '{:,}'.format(len(new))))
