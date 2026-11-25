"""Render text with a compiled font using HarfBuzz shaping + FreeType
rasterisation (the real font binary, hinting included)."""
from __future__ import annotations
import sys
import freetype
import uharfbuzz as hb
from PIL import Image


class Renderer:
    def __init__(self, path, variations=None):
        self.path = path
        self.blob = hb.Blob.from_file_path(path)
        self.face = hb.Face(self.blob)
        self.font = hb.Font(self.face)
        self.ft = freetype.Face(path)
        self.variations = variations
        if variations:
            self.font.set_variations(variations)
            axes = self.ft.get_variation_info().axes
            self.ft.set_var_design_coords([variations.get(a.tag, a.default) for a in axes])
        self.upm = self.face.upem

    def shape(self, text, features=None, direction=None, script=None, language=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        if direction:
            buf.direction = direction
        if script:
            buf.script = script
        if language:
            buf.language = language
        hb.shape(self.font, buf, features or {})
        return buf

    def line(self, text, px, features=None, hinting=True, mono=False, **kw):
        """returns (PIL 'L' image [0=white..255=ink], advance_px)"""
        buf = self.shape(text, features, **kw)
        self.ft.set_pixel_sizes(0, px)
        if self.variations:
            axes = self.ft.get_variation_info().axes
            self.ft.set_var_design_coords([self.variations.get(a.tag, a.default) for a in axes])
        scale = px / self.upm
        flags = freetype.FT_LOAD_RENDER | (freetype.FT_LOAD_TARGET_MONO if mono else 0)
        if not hinting:
            flags |= freetype.FT_LOAD_NO_HINTING
        asc = int(round(self.ft.size.ascender / 64)) + 2
        desc = int(round(-self.ft.size.descender / 64)) + 2
        total = sum(p.x_advance for p in buf.glyph_positions) * scale
        W = int(total) + 8
        H = asc + desc
        import numpy as np
        arr = np.zeros((H, max(W, 1)), dtype=np.uint16)
        x = 2.0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            self.ft.load_glyph(info.codepoint, flags)
            bm = self.ft.glyph.bitmap
            if bm.rows and bm.width:
                data = np.array(bm.buffer, dtype=np.uint8).reshape(bm.rows, bm.pitch)
                if mono:
                    data = np.unpackbits(data, axis=1)[:, :bm.width] * 255
                else:
                    data = data[:, :bm.width]
                gx = int(round(x + pos.x_offset * scale)) + self.ft.glyph.bitmap_left
                gy = asc - self.ft.glyph.bitmap_top - int(round(pos.y_offset * scale))
                x0, y0 = max(gx, 0), max(gy, 0)
                x1, y1 = min(gx + bm.width, arr.shape[1]), min(gy + bm.rows, H)
                if x1 > x0 and y1 > y0:
                    arr[y0:y1, x0:x1] += data[y0 - gy:y1 - gy, x0 - gx:x1 - gx]
            x += pos.x_advance * scale
        img = Image.fromarray(np.minimum(arr, 255).astype(np.uint8), 'L')
        return img, total


def sheet(rows, out, bg=255, pad=8, scale=1):
    """rows: list of (Renderer, text, px, kwargs) -> stacked proof image"""
    imgs = []
    for r in rows:
        rend, text, px = r[0], r[1], r[2]
        kw = r[3] if len(r) > 3 else {}
        im, _ = rend.line(text, px, **kw)
        imgs.append(im)
    W = max(i.width for i in imgs) + 2 * pad
    H = sum(i.height for i in imgs) + pad * (len(imgs) + 1)
    page = Image.new('L', (W, H), 0)
    y = pad
    for im in imgs:
        page.paste(im, (pad, y))
        y += im.height + pad
    page = Image.eval(page, lambda v: 255 - v)
    if scale != 1:
        page = page.resize((page.width * scale, page.height * scale), Image.NEAREST)
    page.save(out)
    return out


if __name__ == '__main__':
    font, out, px = sys.argv[1], sys.argv[2], int(sys.argv[3])
    r = Renderer(font)
    sheet([(r, t, px) for t in sys.argv[4:]], out)
