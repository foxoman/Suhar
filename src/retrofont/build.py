"""Build every font of the RetroUI Sans project.

    python -m retrofont.build [--out dist] [--only Sans-Regular,...] [--no-vf] [--no-nerd] [--jobs N]
"""
from __future__ import annotations
import argparse, json, os, sys, time, shutil
from multiprocessing import Pool

import ufo2ft
from fontTools.ttLib import TTFont
from fontTools.designspaceLib import DesignSpaceDocument, AxisDescriptor, SourceDescriptor, InstanceDescriptor

from . import model, latin, latin_ext, arabic, terminal, symbols, greek_cyrillic, more_scripts      # noqa: F401 (registration order matters)
from . import engine as E, kern as K
from .model import Style, GlyphOut, build_glyphs, REG, MONO_W, ASCENT, DESCENT
from .ufo import make_ufo
from .features import make_features
from . import nerd

WEIGHTS = [(400, 'Regular'), (500, 'Medium'), (600, 'SemiBold'), (700, 'Bold')]
FAMILIES = {'Sans': 'Suhar', 'Mono': 'Suhar Mono', 'Cond': 'Suhar Condensed', 'Naskh': 'Suhar Naskh', 'NaskhD': 'Suhar Naskh Display',
            'Sahafa': 'Suhar Sahafa', 'SahafaH': 'Suhar Sahafa Headline', 'SahafaC': 'Suhar Sahafa Caption'}
EXTRA_WEIGHTS = [(300, 'Light'), (800, 'ExtraBold')]          # static only
BLACK = (900, 'Black')                                        # Suhar only
COND_WIDTH = 0.75


def mkstyle(fam, wght, italic, opsz=0.0, compat=False, grade=0.0):
    if fam == 'Cond':
        st = Style('Sans', wght, italic, opsz, compat, width=COND_WIDTH)
        st.spacef = 0.86
        return st
    if fam in ('Sahafa', 'SahafaH', 'SahafaC'):
        from . import sahafa
        return sahafa.style(wght, 'headline' if fam == 'SahafaH' else 'text', italic, compat, -1.0 if fam == 'SahafaC' else opsz, grade)
    if fam in ('Naskh', 'NaskhD'):
        st = Style('Sans', wght, italic, opsz, compat).set_naskh()
        st.display = fam == 'NaskhD'
        return st
    return Style(fam, wght, italic, opsz, compat)


def static_styles():
    for fam in FAMILIES:
        ws = WEIGHTS if fam in ('Naskh', 'NaskhD', 'Sahafa', 'SahafaH', 'SahafaC') else [EXTRA_WEIGHTS[0]] + WEIGHTS + [EXTRA_WEIGHTS[1]]
        if fam == 'Sans':
            ws = ws + [BLACK]
        for wght, wn in ws:
            for italic in ((False,) if fam == 'NaskhD' else (False, True)):
                yield fam, wght, wn, italic


def notdef(st):
    w = MONO_W if st.mono else 560
    t = 2 * st.hb
    outer = [(60, 0, True), (w - 60, 0, True), (w - 60, 700, True), (60, 700, True)]
    inner = [(60 + t, t, True), (60 + t, 700 - t, True), (w - 60 - t, 700 - t, True), (w - 60 - t, t, True)]
    return GlyphOut('.notdef', [], [outer, inner], w)


def smallcap_kerning(kerning, groups, gl):
    """small capitals take the kerning of their capitals, scaled to their size"""
    from .latin import SMALLCAPS
    byc = {u: n for n, d in REG.items() for u in (d.uni or [])}
    cap2sc = {}
    for low, sc in SMALLCAPS.items():
        uni = REG[low].uni if low in REG else []
        if uni and sc in gl and len(chr(uni[0]).upper()) == 1:
            cap = byc.get(ord(chr(uni[0]).upper()))
            if cap:
                cap2sc[cap] = sc

    def side(key, pre):
        if key.startswith(pre):
            mem = [cap2sc[m] for m in groups.get(key, []) if m in cap2sc]
            if not mem:
                return None
            name = pre + 'sc.' + key[len(pre):]
            groups[name] = mem
            return name
        return cap2sc.get(key)
    add = {}
    for (a, b), v in kerning.items():
        sa, sb = side(a, 'public.kern1.'), side(b, 'public.kern2.')
        if sa and sb:
            add[(sa, sb)] = int(round(v * 0.84))
        if sb and not a.startswith('public.kern1.sc.'):
            a_cap = a in cap2sc or (a.startswith('public.kern1.') and any(m in cap2sc for m in groups.get(a, [])))
            if a_cap:
                add[(a, sb)] = int(round(v * 0.9))          # capital followed by small capitals
    kerning.update(add)


def glyph_set(st, kern_from=None):
    gl = build_glyphs(st)
    gl['.notdef'] = notdef(st)
    kerning, groups = {}, {}
    if not st.mono:
        src = kern_from if kern_from is not None else gl
        comps = {n: d.comp[0] for n, d in REG.items() if d.comp and d.comp[0] != 'accentbase' and n in gl}
        kerning, groups = K.compute(src, comps)
        smallcap_kerning(kerning, groups, gl)
        try:
            kerning.update(K.arabic_tails(gl))      # Arabic is upright-measured in its own style
            kerning.update(K.arabic_word_space(gl))
            kerning.update(K.hebrew(gl))
        except ImportError:
            pass
    return gl, kerning, groups


def make(st: Style, family_key: str):
    """-> ufo for one static style"""
    upright = None
    if st.italic and not st.mono:      # kerning is measured on the upright shapes
        up = Style(st.family, st.wght, False, st.opsz, st.compat, width=st.width)
        if getattr(st, 'sahafa', None):
            from . import sahafa
            up = sahafa.style(st.wght, st.sahafa, False, st.compat, st.opsz, getattr(st, 'grade', 0.0))
        if getattr(st, 'naskh', False):
            up.set_naskh()
            up.display = getattr(st, 'display', False)
        upright = build_glyphs(up)
    gl, kerning, groups = glyph_set(st, upright)
    ufo = make_ufo(st, gl, FAMILIES[family_key], make_features(gl, display=getattr(st, 'display', False), naskh=getattr(st, 'naskh', False)), kerning, groups)
    return ufo, gl


def set_overlap_flags(font):
    if 'glyf' not in font:
        return
    from fontTools.ttLib.tables import _g_l_y_f as G
    for name in font.getGlyphOrder():
        g = font['glyf'][name]
        if g.isComposite():
            g.components[0].flags |= 0x400          # OVERLAP_COMPOUND
        elif g.numberOfContours > 0:
            g.flags[0] |= G.flagOverlapSimple


def autohint(src, dst):
    from ttfautohint import ttfautohint
    ttfautohint(in_file=src, out_file=dst, default_script='latn', fallback_script='none',
                hinting_range_min=6, hinting_range_max=48, hinting_limit=160,
                no_info=True, windows_compatibility=False, symbol=False, verbose=False)


CELL_RANGES = [(0x2500, 0x259F), (0x2800, 0x28FF), (0xE0A0, 0xE0BF), (0x1FB00, 0x1FBFF)]


def strip_cell_hints(path):
    """Box drawing, blocks, Braille and Powerline must all be rasterised the same way so that they
    meet exactly; the auto-hinter snaps only some of them, so their instructions are removed."""
    from fontTools.ttLib.tables.ttProgram import Program
    f = TTFont(path)
    glyf = f['glyf']
    n = 0
    for cp, gn in f.getBestCmap().items():
        if any(lo <= cp <= hi for lo, hi in CELL_RANGES):
            g = glyf[gn]
            if hasattr(g, 'program') and g.program.getBytecode():
                g.program = Program()
                g.program.fromBytecode(b'')
                n += 1
    f.save(path)
    return n


def otf_autohint(path):
    """otfautohint; a glyph that crashes the hinter is left unhinted and reported"""
    import subprocess, re
    excluded = []
    for _ in range(6):
        cmd = ['otfautohint', path] + (['-x', ','.join(excluded)] if excluded else [])
        r = subprocess.run(cmd, capture_output=True, timeout=900)
        if r.returncode == 0 and b'ERROR' not in r.stderr + r.stdout:
            break
        v = subprocess.run(['otfautohint', '-v', '-p', '1', path, '-o', path + '.tmp'] + (['-x', ','.join(excluded)] if excluded else []),
                           capture_output=True, timeout=1800)
        if os.path.exists(path + '.tmp'):
            os.remove(path + '.tmp')
        m = re.findall(r'\(([^)]+)\)[^\n]*Begin hinting', (v.stdout + v.stderr).decode(errors='replace'))
        if not m or m[-1] in excluded:
            r.returncode = r.returncode or 1
            break
        excluded.append(m[-1])
    r.excluded = excluded
    return r


def woff2(path):
    f = TTFont(path)
    f.flavor = 'woff2'
    out = os.path.splitext(path)[0] + '.woff2'
    f.save(out)
    return out


def build_static(args):
    fam, wght, italic, out, do_nerd = args
    t0 = time.time()
    st = mkstyle(fam, wght, italic)
    ufo, gl = make(st, fam)
    base = ufo.info.postscriptFontName
    res = {'name': base, 'glyphs': len(gl), 'files': []}
    d_ttf = os.path.join(out, 'ttf')
    d_otf = os.path.join(out, 'otf')
    d_w = os.path.join(out, 'woff2')
    for d in (d_ttf, d_otf, d_w):
        os.makedirs(d, exist_ok=True)
    ttf = ufo2ft.compileTTF(ufo, removeOverlaps=False)
    set_overlap_flags(ttf)
    raw = os.path.join(d_ttf, base + '.unhinted.ttf')
    ttf.save(raw)
    hinted = os.path.join(d_ttf, base + '.ttf')
    try:
        autohint(raw, hinted)
        res['hinted'] = True
        strip_cell_hints(hinted)
    except Exception as e:                      # keep going unhinted, but say so
        shutil.copy(raw, hinted)
        res['hinted'] = False
        res['hint_error'] = repr(e)
    os.remove(raw)
    otf = ufo2ft.compileOTF(ufo, removeOverlaps=False, optimizeCFF=ufo2ft.CFFOptimization.SUBROUTINIZE)
    otf_path = os.path.join(d_otf, base + '.otf')
    otf.save(otf_path)
    try:                                        # PostScript hints for the CFF outlines (AFDKO otfautohint)
        import subprocess
        r = otf_autohint(otf_path)
        res['otf_hinted'] = r.returncode == 0
        res['otf_unhinted_glyphs'] = getattr(r, 'excluded', [])
        if r.returncode:
            res['otf_hint_error'] = r.stderr.decode(errors='replace')[-300:]
    except Exception as e:
        res['otf_hinted'] = False
        res['otf_hint_error'] = repr(e)
    w = woff2(hinted)
    os.replace(w, os.path.join(d_w, os.path.basename(w)))
    res['files'] += [hinted, otf_path]
    if do_nerd:
        for src in (hinted, otf_path):
            dst = nerd.patch(src, mono=st.mono)
            res['files'].append(dst)
            if dst.endswith('.ttf'):
                w = woff2(dst)
                os.replace(w, os.path.join(d_w, os.path.basename(w)))
    res['time'] = round(time.time() - t0, 1)
    return res


OPSZ_FAMS = ('Sans', 'Cond', 'Naskh', 'Sahafa', 'SahafaH')
GRAD_FAMS = ('Sahafa', 'SahafaH')


def vf_masters(fam):
    """(weight, optical size parameter, optical size in points, grade) of every master"""
    opszs = [(-1, 8), (0, 14), (1, 72)] if fam in OPSZ_FAMS else [(0, 14)]
    ms = [(w, oz, ozv, 0) for w in (400, 700) for oz, ozv in opszs]
    if fam in GRAD_FAMS:
        ms += [(w, 0, 14, g) for w in (400, 700) for g in (-1, 1)]
    return ms


def vf_axes(fam):
    return '[' + ','.join((['GRAD'] if fam in GRAD_FAMS else []) + (['opsz'] if fam in OPSZ_FAMS else []) + ['wght']) + ']'


def trap_match(fam, italic):
    """Ink traps for a variable font: (trapped glyphs of every master, names of the glyphs that can use them)."""
    trapped, trap_ok = {}, set()
    if fam in ('Sahafa', 'SahafaH'):
        # ink traps need outlines without overlaps; a glyph gets them when all its masters still match point for point
        def _norm(cs):
            out = []
            for c in cs:
                i = min((k for k, p in enumerate(c) if p[2]), key=lambda k: (round(c[k][1] / 12), c[k][0]))
                out.append(c[i:] + c[:i])
            return sorted(out, key=lambda c: (-len(c), min(p[0] for p in c)))
        ms = vf_masters(fam)
        for w, oz, ozv, g in ms:
            trapped[w, oz, g] = build_glyphs(mkstyle(fam, w, italic, oz, compat=False, grade=g))
            for gg in trapped[w, oz, g].values():
                if gg.script == 'arab' and gg.contours:
                    gg.contours = _norm(gg.contours)
        ref = trapped[400, 0, 0]
        for n, g4 in ref.items():
            if g4.script != 'arab' or not g4.contours:
                continue
            good = True
            for key, gs in trapped.items():
                g7 = gs.get(n)
                if g7 is None or len(g4.contours) != len(g7.contours) or not all(
                        len(c4) == len(c7) and all(p[2] == q[2] and abs(p[0] - q[0]) < 170 and abs(p[1] - q[1]) < 170 for p, q in zip(c4, c7))
                        for c4, c7 in zip(g4.contours, g7.contours)):
                    good = False
                    break
            if good:
                trap_ok.add(n)
    return trapped, trap_ok


def keep_advances(gl, ref):
    """A grade changes the stroke weight, not the line: every glyph keeps the advance of the ungraded master."""
    from . import arabic as A
    shift = {}
    for n, g in gl.items():
        r = ref.get(n)
        if r is None or g.components or g.advance == r.advance:
            continue
        d = r.advance - g.advance
        inf = A.INFO.get(n, {})
        sh = 0 if inf.get('jl') else (d if inf.get('jr') else d / 2)        # joins stay where they are
        sh = round(sh)
        if sh:
            g.contours = E.shift(g.contours, sh)
            g.anchors = {k: (x + sh, y) for k, (x, y) in g.anchors.items()}
            if getattr(g, 'ink', None):
                g.ink = (g.ink[0] + sh, g.ink[1], g.ink[2] + sh, g.ink[3])
        g.advance = r.advance
        shift[n] = sh
    for n, g in gl.items():
        if g.components and n in ref:
            g.components = list(ref[n].components)
            g.advance = ref[n].advance
            g.anchors = dict(ref[n].anchors)


# ---------------------------------------------------------------------------
def build_variable(fam, italic, out, save_sources=True):
    """wght (+ opsz, + GRAD for Sahafa) variable TTF from overlapping, point-compatible masters"""
    t0 = time.time()
    family = FAMILIES[fam]
    doc = DesignSpaceDocument()
    a = AxisDescriptor()
    a.name, a.tag, a.minimum, a.default, a.maximum = 'Weight', 'wght', 400, 400, 700
    doc.addAxis(a)
    if fam in OPSZ_FAMS:
        a = AxisDescriptor()
        a.name, a.tag, a.minimum, a.default, a.maximum = 'Optical Size', 'opsz', 8, 14, 72
        doc.addAxis(a)
    if fam in GRAD_FAMS:
        a = AxisDescriptor()
        a.name, a.tag, a.minimum, a.default, a.maximum = 'Grade', 'GRAD', -50, 0, 50
        doc.addAxis(a)
    src_dir = os.path.join(out, 'sources', 'masters')
    os.makedirs(src_dir, exist_ok=True)
    it = 'Italic' if italic else ''
    trapped, trap_ok = trap_match(fam, italic)
    base = {}
    for wght, oz, ozv, grade in vf_masters(fam):
        if True:
            st = mkstyle(fam, wght, italic, oz, compat=True, grade=grade)
            up = None
            if italic and fam in ('Sans', 'Cond', 'Naskh', 'Sahafa', 'SahafaH'):
                up = build_glyphs(mkstyle(fam, wght, False, oz, compat=True, grade=grade))
            gl, kerning, groups = glyph_set(st, up)
            for n in trap_ok:
                if n in gl and not gl[n].components:
                    gl[n].contours = trapped[wght, oz, grade][n].contours
            if grade:
                keep_advances(gl, base[wght][0])
                kerning, groups = base[wght][1], base[wght][2]
            elif oz == 0:
                base[wght] = (gl, kerning, groups)
            wn = 'Regular' if wght == 400 else 'Bold'
            sname = (wn + (' ' + it if it else '')).replace('Regular Italic', 'Italic')
            ufo = make_ufo(st, gl, family, make_features(gl, display=getattr(st, 'display', False), naskh=getattr(st, 'naskh', False)), kerning, groups, style_name=sname)
            tag = f"{family.replace(' ', '')}-{wn}{it}" + (f"-opsz{ozv}" if fam in OPSZ_FAMS else '') + (f"-grade{grade}" if grade else '')
            s = SourceDescriptor()
            s.font = ufo
            s.name = tag
            s.familyName = family
            s.styleName = sname
            s.location = {'Weight': wght, **({'Optical Size': ozv} if fam in OPSZ_FAMS else {}), **({'Grade': 50 * grade} if fam in GRAD_FAMS else {})}
            if save_sources:
                p = os.path.join(src_dir, tag + '.ufoz')
                if os.path.exists(p):
                    os.remove(p)
                ufo.save(p, structure='zip')
                s.filename = os.path.relpath(p, os.path.join(out, 'sources'))
            doc.addSource(s)
    for wght, wn in WEIGHTS:
        i = InstanceDescriptor()
        sname = (wn + (' ' + it if it else '')).replace('Regular Italic', 'Italic')
        i.familyName, i.styleName = family, sname
        i.location = {'Weight': wght, **({'Optical Size': 14} if fam in OPSZ_FAMS else {}), **({'Grade': 0} if fam in GRAD_FAMS else {})}
        doc.addInstance(i)
    dropped = []
    for attempt in range(4):
        try:
            vf = ufo2ft.compileVariableTTF(doc, removeOverlaps=False, optimizeGvar=True)
            break
        except Exception as e:
            bad = list(e.args[0].keys()) if e.args and isinstance(e.args[0], dict) else []
            if not bad or attempt == 3:
                raise
            dropped += bad
            for s in doc.sources:          # glyphs whose outline structure differs between masters
                for n in bad:
                    if n in s.font:
                        del s.font[n]
                s.font.lib['public.glyphOrder'] = [n for n in s.font.lib['public.glyphOrder'] if n not in bad]
                s.font.features.text = make_features({n: 1 for n in s.font.keys()}, display=fam == 'NaskhD', naskh=fam in ('Naskh', 'NaskhD', 'Sahafa', 'SahafaH'))
    set_overlap_flags(vf)
    d = os.path.join(out, 'variable')
    os.makedirs(d, exist_ok=True)
    axes = vf_axes(fam)
    path = os.path.join(d, f"{family.replace(' ', '')}{'-Italic' if italic else ''}{axes}.ttf")
    vf.save(path)
    w = woff2(path)
    if trap_ok:
        tj = os.path.join(d, 'ink-traps.json')
        rec = json.load(open(tj)) if os.path.exists(tj) else {}
        rec[os.path.basename(path)] = len(trap_ok)
        json.dump(rec, open(tj, 'w'), indent=1, sort_keys=True)
    if save_sources:
        for s in doc.sources:
            s.font = None
        doc.write(os.path.join(out, 'sources', os.path.basename(path).replace('.ttf', '.designspace')))
    return {'name': os.path.basename(path), 'time': round(time.time() - t0, 1), 'files': [path, w], 'dropped_glyphs': dropped, 'trapped_glyphs': len(trap_ok)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='dist')
    ap.add_argument('--only', default='')
    ap.add_argument('--no-vf', action='store_true')
    ap.add_argument('--no-nerd', action='store_true')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 2)
    a = ap.parse_args(argv)
    jobs = []
    for fam, wght, wn, italic in static_styles():
        tag = f"{fam}-{wn}{'Italic' if italic else ''}"
        if a.only and tag not in a.only.split(','):
            continue
        jobs.append((fam, wght, italic, a.out, not a.no_nerd and fam not in ('Naskh', 'NaskhD', 'SahafaC')))
    report = {'static': [], 'variable': []}
    if not a.no_nerd:
        nerd.prepare()
    with Pool(a.jobs) as pool:
        for r in pool.imap_unordered(build_static, jobs):
            print('built', r['name'], r['glyphs'], 'glyphs', 'hinted' if r.get('hinted') else 'UNHINTED', r['time'], 's', flush=True)
            report['static'].append(r)
    if not a.no_vf and not a.only:
        for fam in ('Sans', 'Mono', 'Cond', 'Naskh', 'NaskhD', 'Sahafa', 'SahafaH'):
            for italic in ((False,) if fam == 'NaskhD' else (False, True)):
                try:
                    r = build_variable(fam, italic, a.out)
                    print('built', r['name'], r['time'], 's', flush=True)
                except Exception as e:
                    r = {'name': f'{fam} variable italic={italic}', 'error': repr(e)}
                    print('VARIABLE FAILED', r, flush=True)
                report['variable'].append(r)
    if not a.only:
        from . import pixel
        report['pixel'] = [os.path.basename(p) for p in pixel.main(a.out)]
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, 'build-report.json'), 'w') as f:
        json.dump(report, f, indent=1)
    return report


if __name__ == '__main__':
    main()
