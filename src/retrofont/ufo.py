"""GlyphOut dict -> ufoLib2 Font."""
from __future__ import annotations
import ufoLib2
from fontTools.pens.pointPen import SegmentToPointPen
from fontTools.pens.roundingPen import RoundingPen

from . import engine as E
from .model import (UPM, CAP, XH, DESC, ASCENT, DESCENT, ITALIC_DEG, Style)

VERSION = (2, 4)
WIN_ASCENT, WIN_DESCENT = 1200, 440
DESIGNER = 'Sultan Al Isaiee (Foxoman)'
DESIGNER_URL = 'https://www.foxoman.net'
COPYRIGHT = 'Copyright 2026 The Suhar Project Authors (Sultan Al Isaiee, @foxoman, https://www.foxoman.net)'
LICENSE = ('This Font Software is licensed under the SIL Open Font License, Version 1.1. '
           'This license is available with a FAQ at: https://openfontlicense.org')
LICENSE_URL = 'https://openfontlicense.org'


def make_ufo(st: Style, glyphs: dict, family: str, features: str = '', kerning=None, groups=None,
             style_name=None) -> ufoLib2.Font:
    f = ufoLib2.Font()
    i = f.info
    sname = style_name or st.style_name
    i.familyName = family
    i.styleName = sname
    i.unitsPerEm = UPM
    i.ascender = ASCENT
    i.descender = DESCENT
    i.capHeight = CAP
    i.xHeight = getattr(st, 'xh', XH)
    i.italicAngle = -ITALIC_DEG if st.italic else 0
    i.versionMajor, i.versionMinor = VERSION[0], VERSION[1] * 100
    i.copyright = COPYRIGHT
    i.openTypeNameDesigner = DESIGNER
    i.openTypeNameDesignerURL = DESIGNER_URL
    i.openTypeNameManufacturer = DESIGNER
    i.openTypeNameManufacturerURL = DESIGNER_URL
    i.openTypeNameLicense = LICENSE
    i.openTypeNameLicenseURL = LICENSE_URL
    i.openTypeNameDescription = ('Suhar: an original typeface for Latin and Arabic, named after the port city of Suhar (Sohar), Oman. '
                                 'Drawn as parametric stroke skeletons for screens, signage and print.')
    i.openTypeOS2VendorID = 'FOXO'
    i.openTypeNameSampleText = 'Suhar \u0635\u064f\u062d\u0627\u0631'
    i.openTypeOS2WeightClass = st.wght
    i.openTypeOS2WidthClass = 3 if st.cond else 5
    i.openTypeOS2TypoAscender = ASCENT
    i.openTypeOS2TypoDescender = DESCENT
    i.openTypeOS2TypoLineGap = 0
    # The win metrics are the Windows clipping box.  In the proportional family they are enlarged so
    # that stacked Arabic and Vietnamese marks are not cut; line spacing still comes from the typo
    # metrics (USE_TYPO_METRICS).  Mono keeps them equal to the cell.
    i.openTypeOS2WinAscent = ASCENT if st.mono else WIN_ASCENT
    i.openTypeOS2WinDescent = -DESCENT if st.mono else WIN_DESCENT
    i.openTypeHheaAscender = ASCENT
    i.openTypeHheaDescender = DESCENT
    i.openTypeHheaLineGap = 0
    i.openTypeOS2Type = []          # installable embedding
    sel = [7]                        # USE_TYPO_METRICS
    i.openTypeOS2Selection = sel
    i.openTypeOS2StrikeoutPosition = 264
    i.openTypeOS2StrikeoutSize = round(2 * st.hb)
    i.postscriptUnderlinePosition = -112
    i.postscriptUnderlineThickness = round(2 * st.hb)
    i.postscriptIsFixedPitch = st.mono
    i.postscriptBlueValues = [-10, 0, getattr(st, 'xh', XH), getattr(st, 'xh', XH) + 10, CAP, CAP + 10]
    i.postscriptOtherBlues = [DESC - 10, DESC]
    i.postscriptStemSnapH = [round(2 * st.hb)]
    i.postscriptStemSnapV = [round(2 * st.a)]
    if st.mono:
        i.openTypeOS2Panose = [2, 11, max(3, min(9, 5 + round(st.t * 3))), 9, 2, 2, 2, 2, 2, 4]
    else:
        i.openTypeOS2Panose = [2, 11, max(3, min(9, 5 + round(st.t * 3))), 6 if st.cond else 4, 2, 2, 2, 2, 2, 4]
    # style linking (R/I/B/BI groups per weight pair)
    from .model import WEIGHT_NAMES
    w = WEIGHT_NAMES[st.wght]
    if st.wght in (400, 700):
        i.styleMapFamilyName = family
        i.styleMapStyleName = {(400, False): 'regular', (400, True): 'italic',
                               (700, False): 'bold', (700, True): 'bold italic'}[(st.wght, st.italic)]
    else:
        i.styleMapFamilyName = f'{family} {w}'
        i.styleMapStyleName = 'italic' if st.italic else 'regular'
    i.openTypeNamePreferredFamilyName = family
    i.openTypeNamePreferredSubfamilyName = sname
    i.postscriptFontName = family.replace(' ', '') + '-' + sname.replace(' ', '')
    i.postscriptFullName = f'{family} {sname}'

    order = ['.notdef'] + [n for n in glyphs if n != '.notdef']
    cats = {}
    for name in order:
        if name not in glyphs:
            continue
        go = glyphs[name]
        g = f.newGlyph(name)
        g.width = round(go.advance)
        g.unicodes = list(go.uni)
        if go.contours:
            pen = g.getPen() if st.compat else RoundingPen(g.getPen())   # masters stay unrounded until conversion
            E.draw(go.contours, pen)
        for base, dx, dy in go.components:
            g.getPen().addComponent(base, (1, 0, 0, 1, dx, dy))
        for an, (x, y) in go.anchors.items():
            g.appendAnchor({'name': an, 'x': round(x), 'y': round(y)})
        if go.cat in ('mark', 'ligature', 'base'):
            cats[name] = go.cat
    f.lib['public.glyphOrder'] = [n for n in order if n in glyphs]
    f.lib['public.openTypeCategories'] = cats
    if features:
        f.features.text = features
    if kerning:
        f.kerning.update(kerning)
    if groups:
        f.groups.update(groups)
    return f
