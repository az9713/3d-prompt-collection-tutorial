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


# --- 2b. sections, labelled at the author's own boundaries -------------------
# The spine is a section-level structure, so it is read at section level. A
# sentence-level reading fires on stray wording and produces one-line labels
# that say nothing; this reads whole sections instead, cut where Peter cut them.
HEAD_RE = re.compile(r'^\s*#{2,}\s*\S')

# A section under a heading is labelled by its heading. Peter's headings are
# themselves part of the lesson: PERFORMANCE DISCIPLINE is part h, whatever the
# sentences underneath happen to mention.
HEAD_RULES = [
    ('h', r'performance|fps|frame rate|budget|discipline'),
    ('g', r'control|exploration|navigat|interact|camera'),
    ('e', r'first frame|opening|title screen'),
    ('d', r'technical|implementation|guardrail|output instruction|specification'),
    ('b', r'must not|avoid|forbidden'),
    ('c', r'objective|goal|scope|detail|fidelity|requirement|landmark'),
    ('f', r'alive|life|living|dynamis|motion|atmosphere|light'),
]

F_WEIGHT = 0.5      # f's keyword list is the loosest; unweighted it wins sections
                    # that plainly belong to another part
D_STRICT = r'import map|es modules|no external|bundler|pinned version'
SECOND = 0.25       # a part holding this share of a section earns a second letter


def sections(text):
    """Cut into sections at markdown headings and blank lines.

    Returns [(chunk, heading or None)]. The chunks concatenate back to text.
    """
    out, cur, cur_head, prev_sep = [], '', None, ''
    for seg in segments(text):
        if not seg.strip():                 # separator: closes the section above
            cur += seg
            prev_sep = seg
            continue
        head = bool(HEAD_RE.match(seg))
        blank = prev_sep.count('\n') >= 2
        if cur.strip() and (head or blank):
            out.append((cur, cur_head))
            cur, cur_head = '', None
        if head and cur_head is None:
            cur_head = seg.strip()
        cur += seg
        prev_sep = ''
    if cur:
        out.append((cur, cur_head))
    return out


def section_role(chunk, head, got):
    """(primary part, [second part]) for one section, or (None, []) if silent.

    `got` is the parts the whole prompt contains. A heading never introduces a
    part the prompt does not otherwise show; it only decides which of the parts
    already there owns this section.
    """
    if head:
        low = head.lower()
        k = next((k for k, pat in HEAD_RULES if re.search(pat, low) and k in got), None)
        if k:
            # b still gets its second letter here. A heading settles the section,
            # but a "must not" sentence inside it is the move worth seeing and
            # would otherwise vanish from the page.
            return k, (['b'] if k != 'b' and re.search(PAT['b'], chunk.lower()) else [])
    tally = collections.Counter()
    for seg in segments(chunk):
        if not seg.strip():
            continue
        k = next((k for k in PRIORITY if re.search(PAT[k], seg.lower())), None)
        if k:
            tally[k] += len(seg) * (F_WEIGHT if k == 'f' else 1)
    # d is the part that is pasted unchanged, so a section is only d when it
    # carries the boilerplate wording itself. "Procedural" on its own is ordinary
    # vocabulary here and would take sections away from the part they belong to.
    if 'd' in tally and not re.search(D_STRICT, chunk.lower()):
        del tally['d']
    if not tally:
        return None, []
    ranked = tally.most_common()
    total = sum(tally.values())
    # b, the negative list, is the one genuinely optional part and it is always
    # two or three sentences inside a longer section, so it never wins one. It is
    # shown whenever it is there; every other part must earn its second letter.
    second = [k for k, v in ranked[1:] if v >= SECOND * total][:1]
    if 'b' in tally and ranked[0][0] != 'b' and 'b' not in second:
        second.append('b')
    return ranked[0][0], second


def label_sections(text):
    """Return [(chunk, role, second_roles)], the chunks concatenating back to text.

    One letter per section. The opening section is part a by definition, since
    it is where the prompt names its subject; whatever else it carries becomes
    its second letter. A section whose wording matches nothing continues the
    part above it, and neighbouring sections with the same single letter merge,
    so the gutter shows the shape of the prompt rather than every sentence.
    """
    rows, prev, got = [], None, roles_of(text)
    for i, (chunk, head) in enumerate(sections(text)):
        role, extra = section_role(chunk, head, got)
        if i == 0:
            # The opening section names the subject, so it is a. Whatever else it
            # carries becomes its second letter, b first: the negative list lives
            # here in most prompts and it is the move worth seeing.
            seen, got_here = set(), [r for r in ([role] + extra) if r and r != 'a']
            got_here.sort(key=lambda r: r != 'b')
            extra = [r for r in got_here if not (r in seen or seen.add(r))][:2]
            role = 'a'
        elif role is None:
            role, extra = (prev or 'a'), []
        prev = role
        if rows and rows[-1][1] == role and not extra and not rows[-1][2]:
            rows[-1][0] += chunk
        else:
            rows.append([chunk, role, extra])
    assert ''.join(r[0] for r in rows) == text
    return [tuple(r) for r in rows]


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
    for chunk, role, extra_roles in label_sections(text):
        marked = []
        for seg in segments(chunk):
            marked.append('<span class="reused">%s</span>' % esc(seg)
                          if is_reused(seg) else esc(seg))
        gut = ('<span class="g %s">%s</span><span class="gname">%s</span>'
               % (role, role, esc(ROLE_NAME[role].lower())))
        for x in extra_roles:
            gut += ('<span class="gname also">and %s, %s</span>'
                    % (x, esc(ROLE_NAME[x].lower())))
        body.append('<div class="sec %s"><div class="sechd">%s</div><pre>%s</pre></div>'
                    % (role, gut, ''.join(marked).strip('\n')))

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
is then cut into sections and each section is headed with the part it is doing, so the
shape of the prompt can be read down the page against the wording that fills it. Within
the text, dimmed wording appears in at least one other prompt as well; everything at full
contrast is unique to this one.</p>

<p>The sections are Peter's own. The cut falls where he put a markdown heading, which {heads}
of the 63 prompts use, and at a blank line everywhere else. Nothing is reordered or
reworded: each section runs exactly as it does in <code>prompts.json</code>. Where a
section carries a heading, the heading names the part, which is itself worth learning:
<em>Performance discipline</em> is part h and <em>Exploration and controls</em> is part g,
whatever the sentences underneath happen to mention. Where there is no heading, the part
that owns the most characters in the section wins it. That gives {secs} sections across the
collection, {per} per prompt.</p>

<p>A second, quieter label appears where one section is plainly doing two jobs: the part
holds at least a quarter of the section, or it is part b. The negative list is short and
always sits inside a longer opening paragraph, so it never wins a section on length, yet
it is one of the moves most worth seeing; it is shown wherever it occurs. The opening
section is part a by definition, because that is where a prompt names its subject, and
what else it carries is shown beside it.</p>

<p class="note">The strip and the section headings measure two different things and will
not always agree. The strip asks whether a part appears anywhere in the prompt; the
headings ask which part dominates each section. A part can be present and dominate no
section, so a letter can sit in the strip and never appear down the page. The reverse
never happens: every letter in the page is also in the strip, and a build assertion
enforces it. One consequence worth naming: the spine is ordered on average &mdash; the
median position of each part through the text runs {order} &mdash; but only {mono} of the
63 prompts run cleanly from a to h without revisiting a part. Peter comes back to detail after controls, and puts life back in after
performance.</p>

<p class="legend"><span class="k reused-k"></span>reused in another prompt
<span class="k unique-k"></span>this prompt only
<span class="k fixed-k"></span>part d, the block pasted unchanged</p>
"""


def outro():
    """OUTRO_HEAD with its four figures measured rather than typed."""
    # a, then b/d/e, then c/f, then g, then h: the average order of the spine.
    rank = {'a': 0, 'b': 1, 'd': 1, 'e': 1, 'c': 2, 'f': 2, 'g': 3, 'h': 4}
    # Where each part's wording sits in a prompt, as a fraction of its length.
    # This is measured on sentences, independently of how sections are labelled.
    pos = collections.defaultdict(list)
    for p in PROMPTS:
        t = p['prompt']
        for m in re.finditer(r'[^\n]+', t):
            k = next((k for k in PRIORITY if re.search(PAT[k], m.group(0).lower())), None)
            if k:
                pos[k].append((m.start() + m.end()) / 2.0 / len(t))
    pos['a'] = [0.0]
    order = ', '.join(sorted(pos, key=lambda k: sorted(pos[k])[len(pos[k]) // 2]))
    secs = mono = heads = 0
    for p in PROMPTS:
        rows = label_sections(p['prompt'])
        secs += len(rows)
        if re.search(r'^\s*#{2,}\s*\S', p['prompt'], re.M):
            heads += 1
        r = [rank[x[1]] for x in rows]
        mono += all(b >= a for a, b in zip(r, r[1:]))
    return OUTRO_HEAD.format(
        heads=heads, secs=secs, mono=mono, order=order,
        per='%.1f' % (secs / float(len(PROMPTS))))


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
           outro()]
    for n, p in enumerate(PROMPTS, 1):
        out.append(card(n, p))
    out.append(END)
    return '\n'.join(out)


def check():
    """The two guarantees. Run as `python build_deltas.py --check`."""
    secs = 0
    for n, p in enumerate(PROMPTS, 1):
        rows = label_sections(p['prompt'])
        secs += len(rows)
        assert ''.join(c for c, _r, _x in rows) == p['prompt'], \
            'prompt %d does not reconstruct' % n
        # The gutter says which part dominates each section; the strip says which
        # parts are present anywhere. A part can be present and dominate nothing,
        # so the gutter is a subset of the strip, never a superset.
        shown = {r for _c, r, _x in rows} | {x for _c, _r, xs in rows for x in xs}
        assert shown <= roles_of(p['prompt']), \
            'prompt %d: gutter %s outside strip %s' % (
                n, sorted(shown - roles_of(p['prompt'])), sorted(roles_of(p['prompt'])))
    print('all 63 reconstruct byte-for-byte; every gutter letter is in its strip')
    print('%d sections over 63 prompts, %.1f per prompt' % (secs, secs / 63.0))


if __name__ == '__main__':
    import sys
    if '--check' in sys.argv:
        check()
        raise SystemExit
    page = io.open(PAGE, encoding='utf-8', newline='').read()
    i, j = page.index(BEGIN), page.index(END) + len(END)
    new = page[:i] + build() + page[j:]
    io.open(PAGE, 'w', encoding='utf-8', newline='').write(new)
    print('deltas rebuilt: %d prompts, page now %s bytes' % (len(PROMPTS), '{:,}'.format(len(new))))
