"""OpenType layout source (GSUB).  GPOS kern/mark/mkmk and GDEF are written by
ufo2ft from the UFO kerning, anchors and glyph categories."""
from . import arabic as A


def make_features(glyphs: dict, display: bool = False, naskh: bool = False, sahafa: bool = False) -> str:
    have = glyphs.__contains__
    out = ["languagesystem DFLT dflt;", "languagesystem latn dflt;", "languagesystem arab dflt;",
           "languagesystem arab URD;", "languagesystem arab FAR;", "languagesystem grek dflt;",
           "languagesystem cyrl dflt;", "languagesystem hebr dflt;", ""]
    subs = {'init': [], 'medi': [], 'fina': []}
    for cp, forms in sorted(A.FORMS.items()):
        base = forms.get('isol')
        for f in subs:
            if f in forms and have(forms[f]) and have(base):
                subs[f].append(f"    sub {base} by {forms[f]};")
    if have('uni0640'):
        pass
    for f in ('init', 'medi', 'fina'):
        if subs[f]:
            out += [f"feature {f} {{", "    script arab;"] + subs[f] + [f"}} {f};", ""]
    rl = []
    for (alef, form), name in sorted(A.LIGA.items()):
        if not have(name):
            continue
        lam = A.FORMS[0x644]['init' if form == 'isol' else 'medi']
        al = A.FORMS[alef]['fina']
        if have(lam) and have(al):
            rl.append(f"    sub {lam} {al} by {name};")
    if rl:
        out += ["feature rlig {", "    script arab;", "    lookupflag IgnoreMarks;"] + rl + ["} rlig;", ""]
    # the word Allah: alef + lam lam heh  (discretionary; the code point U+FDF2 is always available)
    if have('uniFDF2') and all(have(n) for n in ('uni0627', 'uni0644.init', 'uni0644.medi', 'uni0647.fina')):
        out += ["feature dlig {", "    script arab;", "    lookupflag IgnoreMarks;",
                "    sub uni0627 uni0644.init uni0644.medi uni0647.fina by uniFDF2;", "} dlig;", ""]
    if have('uni06F6.urdu') and have('uni06F7.urdu'):
        out += ["feature locl {", "    script arab;", "    language URD;",
                "    sub uni06F6 by uni06F6.urdu;", "    sub uni06F7 by uni06F7.urdu;", "} locl;", ""]
    # contextual tall teeth
    if A.TEETH['tall'] and all(have(n) for n in A.TEETH['tall']):
        out += ["@TeethInit = [" + ' '.join(A.TEETH['init']) + "];", "@TeethMedi = [" + ' '.join(A.TEETH['medi']) + "];",
                "@TeethTall = [" + ' '.join(A.TEETH['tall']) + "];",
                "feature calt {", "    script arab;", "    lookupflag IgnoreMarks;",
                "    sub [@TeethInit @TeethMedi] @TeethMedi' @TeethMedi by @TeethTall;", "} calt;", ""]
    br = [(a, b) for a, b in A.BEHR.items() if have(a) and have(b)]
    rr = [(a, b) for a, b in A.REHR.items() if have(a) and have(b)]
    if (naskh or display) and br and rr:
        tm = [(a, b) for a, b in zip(A.TEETH['medi'], A.TEETH['tall']) if have(a) and have(b)]
        tb = [n for n in A.TALL_BEFORE if have(n)]
        out += ["@BehN = [" + ' '.join(a for a, _ in br) + "];", "@BehR = [" + ' '.join(b for _, b in br) + "];",
                "@RehN = [" + ' '.join(a for a, _ in rr) + "];", "@RehR = [" + ' '.join(b for _, b in rr) + "];",
                "@TmN = [" + ' '.join(a for a, _ in tm) + "];", "@TmT = [" + ' '.join(b for _, b in tm) + "];", "@TallBefore = [" + ' '.join(tb) + "];",
                "lookup beh_r {", "    sub @BehN by @BehR;", "} beh_r;", "lookup reh_r {", "    sub @RehN by @RehR;", "} reh_r;",
                "lookup tooth_t {", "    sub @TmN by @TmT;", "} tooth_t;",
                "feature calt {", "    script arab;",
                "    lookup nb_ctx1 {", "        lookupflag IgnoreMarks;", "        sub @BehN' lookup beh_r @RehN;", "    } nb_ctx1;",
                "    lookup nb_ctx2 {", "        lookupflag IgnoreMarks;", "        sub @BehR @RehN' lookup reh_r;", "    } nb_ctx2;",
                "    lookup nb_ctx3 {", "        lookupflag IgnoreMarks;", "        sub @TmN' lookup tooth_t @TallBefore;", "    } nb_ctx3;", "} calt;", ""]
        kl = [(a, b) for a, b in A.KAFL.items() if have(a) and have(b)]
        kb = [n for n in A.KAFL_BEFORE + [A.FORMS[0x644]['medi'], A.FORMS[0x644]['fina']] + [n_ for (_a, f_), n_ in A.LIGA.items() if f_ == 'fina'] if have(n)]
        if kl and kb:                                    # kaf before alef or lam: a narrower body, so the three stems stand evenly
            out += ["@KafN = [" + ' '.join(a for a, _ in kl) + "];", "@KafL = [" + ' '.join(b for _, b in kl) + "];", "@KafBefore = [" + ' '.join(kb) + "];",
                    "lookup kaf_l {", "    sub @KafN by @KafL;", "} kaf_l;",
                    "feature calt {", "    script arab;", "    lookup nb_ctx4 {", "        lookupflag IgnoreMarks;", "        sub @KafN' lookup kaf_l @KafBefore;", "    } nb_ctx4;", "} calt;", ""]
        fq = [A.FORMS[c][f] for c in (0x641, 0x642) for f in ('init', 'medi') if have(A.FORMS[c][f])]
        ry = [(a, b) for a, b in A.RET.items() if have(a) and have(b)]
        if fq and ry and not display:                    # final yeh returns under feh and qaf (في), as it does in every Naskh hand
            out += ["feature calt {", "    script arab;", "    lookup nb_ctx5 {", "        lookupflag IgnoreMarks;"] + \
                   [f"        sub [{' '.join(fq)}] {a}' by {b};" for a, b in ry] + ["    } nb_ctx5;", "} calt;", ""]
        lm = [(a, b, l) for a, b, l in A.DLIG if l in ('lam_meem.init', 'lam_meem.medi') and have(a) and have(b) and have(l)]
        if sahafa and lm:                                # lam stands on a following meem (لمس، المجلس)
            out += ["feature calt {", "    script arab;", "    lookup nb_lig {", "        lookupflag IgnoreMarks;"] + [f"        sub {a} {b} by {l};" for a, b, l in lm] + ["    } nb_lig;", "} calt;", ""]
    ja = [(a, b) for a, b in A.JALT.items() if have(a) and have(b)]
    if ja and not have('LIG.h'):
        out += ["feature jalt {", "    script arab;"] + [f"    sub {a} by {b};" for a, b in sorted(ja)] + ["} jalt;", ""]
    rt = [(a, b) for a, b in A.RET.items() if have(a) and have(b)]
    rp = [n for n in A.RET_PREV if have(n)]
    if (naskh or display) and rt and rp:
        _t = 'calt' if display else 'ss06'           # on by default in the Display family, optional in the text Naskh
        out += ["@RetPrev = [" + ' '.join(rp) + "];", f"feature {_t} {{"]
        if not display:
            out += ['    featureNames { name "Returning yeh"; };']
        out += ["    script arab;", "    lookupflag IgnoreMarks;"] + [f"    sub @RetPrev {a}' by {b};" for a, b in rt] + [f"}} {_t};", ""]
    stt = [(a, b) for a, b in A.STACK_TOOTH.items() if have(a) and have(b)]
    stj = [(a, b) for a, b in A.STACK_JEEM.items() if have(a) and have(b)]
    if (naskh or display) and stt and stj:
        _t = 'calt' if display else 'ss07'
        out += ["@StT = [" + ' '.join(a for a, _ in stt) + "];", "@StTj = [" + ' '.join(b for _, b in stt) + "];",
                "@StJ = [" + ' '.join(a for a, _ in stj) + "];", "@StJj = [" + ' '.join(b for _, b in stj) + "];",
                "lookup stack_tooth {", "    sub @StT by @StTj;", "} stack_tooth;", "lookup stack_jeem {", "    sub @StJ by @StJj;", "} stack_jeem;",
                f"feature {_t} {{"]
        if _t == 'ss07':
            out += ['    featureNames { name "Letters standing on jeem"; };']
        out += ["    script arab;", "    lookup stack_ctx1 {", "        lookupflag IgnoreMarks;", "        sub @StT' lookup stack_tooth @StJ;", "    } stack_ctx1;",
                "    lookup stack_ctx2 {", "        lookupflag IgnoreMarks;", "        sub @StTj @StJ' lookup stack_jeem;", "    } stack_ctx2;", f"}} {_t};", ""]
    dl = [(a, b, l) for a, b, l in A.DLIG if have(a) and have(b) and have(l)]
    if dl:
        _tag = 'dlig'
        out += [f"feature {_tag} {{", "    script arab;", "    lookupflag IgnoreMarks;"] + [f"    sub {a} {b} by {l};" for a, b, l in dl] + [f"}} {_tag};", ""]
    ss = [(a, b) for a, b in list(A.SS01.items()) + [(n, n + '.ss01') for n in ('y', 'j', 'g', 'Q', 'J')] if have(a) and have(b)]
    ss += [(n, n + '.ss01') for n in glyphs if have(n + '.ss01') and (n, n + '.ss01') not in ss and not n.endswith('.ss01')]
    if ss:
        out += ["feature ss01 {", '    featureNames { name "Khanjar tails"; name 3 1 0x0401 "\\0630\\064a\\0644 \\0627\\0644\\062e\\0646\\062c\\0631"; };']
        out += [f"    sub {a} by {b};" for a, b in sorted(set(ss))] + ["} ss01;", ""]
    if have('zero.dot'):
        out += ["feature ss02 {", '    featureNames { name "Dotted zero"; };', "    sub zero by zero.dot;", "} ss02;", ""]
    if have('zero.plain'):
        out += ["feature ss03 {", '    featureNames { name "Plain zero"; };', "    sub zero by zero.plain;", "} ss03;", ""]
    from . import latin as LT
    sc = [(a, b) for a, b in LT.SMALLCAPS.items() if have(a) and have(b)]
    if sc:
        from .model import REG
        byc = {u: n for n, d in REG.items() for u in (d.uni or [])}
        up = {}
        for a, b in sc:                      # capital -> small cap, through the Unicode case pair
            uni = REG[a].uni if a in REG else []
            cp = uni[0] if uni else None
            if cp and len(chr(cp).upper()) == 1 and chr(cp).upper() != chr(cp):
                cap = byc.get(ord(chr(cp).upper()))
                if cap and have(cap):
                    up[cap] = b
        out += ["feature smcp {"] + [f"    sub {a} by {b};" for a, b in sorted(sc)] + ["} smcp;", ""]
        if up:
            out += ["feature c2sc {"] + [f"    sub {a} by {b};" for a, b in sorted(up.items())] + ["} c2sc;", ""]
    pn = [(a, b) for a, b in LT.PNUM.items() if have(a) and have(b)]
    if pn and not have('LIG.h'):
        out += ["feature pnum {"] + [f"    sub {a} by {b};" for a, b in pn] + ["} pnum;", ""]
        out += ["feature tnum {"] + [f"    sub {b} by {a};" for a, b in pn] + ["} tnum;", ""]
    on = [(a, b) for a, b in LT.ONUM.items() if have(a) and have(b)]
    if on and not have('LIG.h'):
        out += ["feature onum {"] + [f"    sub {a} by {b};" for a, b in on] + [f"    sub {LT.PNUM[a]} by {b};" for a, b in on if a in LT.PNUM] + ["} onum;", ""]
        out += ["feature lnum {"] + [f"    sub {b} by {a};" for a, b in on] + ["} lnum;", ""]
    if have('LIG.h') and A.WIDE2 and all(have(b) for b in A.WIDE2.values()):
        out += ["feature ss05 {", '    featureNames { name "Two-cell wide Arabic letters"; };'] + \
               [f"    sub {a} by {b};" for a, b in sorted(A.WIDE2.items())] + ["} ss05;", ""]
    D = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    sup = ['uni2070', 'uni00B9', 'uni00B2', 'uni00B3'] + ['uni%04X' % c for c in range(0x2074, 0x207A)]
    sub_ = ['uni%04X' % c for c in range(0x2080, 0x208A)]
    if all(have(x) for x in sup):
        for tag in ('sups', 'numr'):
            out += [f"feature {tag} {{"] + [f"    sub {a} by {b};" for a, b in zip(D, sup)] + [f"}} {tag};", ""]
    if all(have(x) for x in sub_):
        for tag in ('subs', 'sinf', 'dnom'):
            out += [f"feature {tag} {{"] + [f"    sub {a} by {b};" for a, b in zip(D, sub_)] + [f"}} {tag};", ""]
    if have('ordfeminine') and have('ordmasculine'):
        out += ["feature ordn {", "    sub [zero one two three four five six seven eight nine] a' by ordfeminine;",
                "    sub [zero one two three four five six seven eight nine] o' by ordmasculine;", "} ordn;", ""]
    ay = [(a, b) for a, b in A.AYAH_DIGITS.items() if have(a) and have(b)]
    if ay and have('uni06DD') and not have('LIG.h'):
        W = getattr(glyphs.get('uni06DD'), 'advance', 960) or 960
        if not isinstance(W, (int, float)):
            W = 960
        W = int(round(W)); dw = A.AYAH_DW
        out += ["@AyahD = [" + ' '.join(a for a, _ in ay) + "];", "@AyahS = [" + ' '.join(b for _, b in ay) + "];",
                "lookup ayah_small {", "    sub @AyahD by @AyahS;", "} ayah_small;",
                "feature rlig {", "    script arab;", "    lookup ayah_ctx {",
                "        sub uni06DD @AyahD' lookup ayah_small;", "        sub uni06DD @AyahS @AyahD' lookup ayah_small;",
                "        sub uni06DD @AyahS @AyahS @AyahD' lookup ayah_small;", "    } ayah_ctx;", "} rlig;", "",
                "feature dist {", "    # Automatic Code", "    script arab;", "    lookup ayah_pos {"]
        for n in (3, 2, 1):
            o = (W - n * dw) // 2
            out.append(f"        pos uni06DD' <0 0 {-(W - o)} 0> " + ' '.join(['@AyahS'] * n) + ";")
        out += ["    } ayah_pos;", "    lookup ayah_end {", "        ignore pos @AyahS' @AyahS;"]
        for n in (3, 2, 1):
            o = (W - n * dw) // 2
            out.append("        pos uni06DD " + ' '.join(['@AyahS'] * (n - 1)) + f" @AyahS' <0 0 {o} 0>;")
        out += ["    } ayah_end;", "} dist;", ""]
    if have('zero.slash'):
        out += ["feature zero {", "    sub zero by zero.slash;", "} zero;", ""]
    fr = [(lig, a, b) for lig, a, b in (('onequarter', 'one', 'four'), ('onehalf', 'one', 'two'), ('threequarters', 'three', 'four'),
                                        ('uni2153', 'one', 'three'), ('uni2154', 'two', 'three'), ('uni215B', 'one', 'eight'))
          if have(lig) and have(a) and have(b) and have('slash')]
    if fr:
        out += ["feature frac {"] + [f"    sub {a} slash {b} by {lig};" for lig, a, b in fr]
        if have('uni2044'):
            out += [f"    sub {a} uni2044 {b} by {lig};" for lig, a, b in fr]
        out += ["} frac;", ""]
    from .symbols import LIGATURES
    if all(have(x[3]) for x in LIGATURES):
        out += ["feature dlig {", "    script DFLT;", "    lookup codelig1 {"]
        out += [f"        sub {a}' {b} by {sp};" for a, b, sp, name, _ in LIGATURES]
        out += ["    } codelig1;", "    lookup codelig2 {"]
        out += [f"        sub {sp} {b}' by {name};" for a, b, sp, name, _ in LIGATURES]
        out += ["    } codelig2;", "    script latn;", "    lookup codelig1;", "    lookup codelig2;", "} dlig;", ""]
    return '\n'.join(out)
