#!/usr/bin/env python3
"""THE WORLD IN ONE PAGE - 26 November 2026.

A single 1024x1024 newspaper front page summing up six major world news
stories from Thursday 26 November 2026. Pure Python standard library:
hand-rolled PNG encoder, hand-rolled 5x7 bitmap font, all artwork drawn
from primitives. Deterministic: no clock, no randomness, no network.
Writes entry.png into $MAKEFUN_OUTPUT_DIR (default /output).
"""

import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 231)   # warm newsprint
INK = (20, 20, 20)        # near-black ink
RED = (158, 27, 27)       # kicker / rule red
BLUE = (29, 78, 137)      # illustration blue
GOLD = (176, 124, 18)     # illustration gold
GREY = (120, 116, 108)    # secondary text
PANEL = (255, 253, 247)   # panel paper
SKY = (214, 228, 240)     # icon-strip background
FIRE = (214, 84, 24)      # flame orange

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows; each row is a 5-bit int, bit 4 is
# the leftmost pixel. Lowercase input is upper-cased by the renderer.
# ---------------------------------------------------------------------------
FONT = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b11011, 0b10001),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "$": (0b00100, 0b01111, 0b10100, 0b01110, 0b00101, 0b11110, 0b00100),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "+": (0, 0b00100, 0b00100, 0b01110, 0b00100, 0b00100, 0),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
    "*": (0, 0b10101, 0b01110, 0b11111, 0b01110, 0b10101, 0),
    "@": (0b01110, 0b10001, 0b10111, 0b10101, 0b10110, 0b10000, 0b01110),
    "#": (0b01010, 0b01010, 0b11111, 0b01010, 0b11111, 0b01010, 0b01010),
    "_": (0, 0, 0, 0, 0, 0, 0b11111),
    "[": (0b01110, 0b01000, 0b01000, 0b01000, 0b01000, 0b01000, 0b01110),
    "]": (0b01110, 0b00010, 0b00010, 0b00010, 0b00010, 0b00010, 0b01110),
    "|": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
}

CHAR_W = 6  # advance per glyph in font units (5 pixels + 1 gap)


class Canvas:
    """A plain RGB raster with primitive drawing helpers."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(w * h * 3))
        # fill properly: bytearray above repeats only the first byte; do it right
        buf = bytearray(w * h * 3)
        for i in range(w * h):
            buf[3 * i] = bg[0]
            buf[3 * i + 1] = bg[1]
            buf[3 * i + 2] = bg[2]
        self.px = buf

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x0, x1, y, c, t=1):
        for yy in range(y, y + t):
            for xx in range(min(x0, x1), max(x0, x1) + 1):
                self.set(xx, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        for xx in range(x, x + t):
            for yy in range(min(y0, y1), max(y0, y1) + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        # midpoint circle outline
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.set(cx + sx, cy + sy, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            half = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            self.hline(cx - half, cx + half, yy, c)

    def poly(self, pts, c):
        """Scanline fill of a simple polygon (list of (x, y))."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(int(xs[k]), int(xs[k + 1]), y, c)

    # -- text -------------------------------------------------------------
    def text_width(self, s, scale):
        return len(s) * CHAR_W * scale - scale

    def draw_text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        self.rect(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += CHAR_W * scale
        return cx

    def draw_centered(self, cx, y, s, scale, c):
        w = self.text_width(s, scale)
        return self.draw_text(cx - w // 2, y, s, scale, c)

    def wrap(self, s, max_w, scale):
        """Greedy word wrap; returns list of lines."""
        words = s.upper().split()
        lines, cur = [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if self.text_width(trial, scale) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines


def write_png(path, cv):
    """Encode the canvas as a 24-bit RGB PNG (filter 0 scanlines)."""
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Pictograms, one per story. Each draws inside a box (x, y, w, h).
# ---------------------------------------------------------------------------
def icon_tariffs(cv, x, y, w, h):
    base = y + h - 26
    bars = [(0.16, 34, BLUE), (0.38, 52, BLUE), (0.60, 70, RED), (0.82, 92, RED)]
    for fx, bh, col in bars:
        bx = x + int(fx * w) - 16
        cv.rect(bx, base - bh, 32, bh, col)
        cv.rect(bx, base - bh, 32, 4, INK)
    cv.hline(x + 8, x + w - 8, base, INK, 3)
    cv.line(x + 14, base - 96, x + w - 18, base - 104, RED)
    cv.poly([(x + w - 18, base - 104), (x + w - 34, base - 110),
             (x + w - 34, base - 98)], RED)
    cv.draw_text(x + 10, y + 8, "15%  20%  25%  35%", 1, INK)


def icon_drone(cv, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2 + 4
    cv.rect(cx - 26, cy - 10, 52, 20, INK)
    cv.rect(cx - 10, cy - 6, 20, 12, RED)
    for dx, dy in ((-38, -22), (38, -22), (-38, 22), (38, 22)):
        cv.line(cx, cy, cx + dx, cy + dy, INK)
        cv.hline(cx + dx - 16, cx + dx + 16, cy + dy, INK, 3)
        cv.disc(cx + dx, cy + dy, 4, INK)
    cv.disc(cx, cy + 26, 5, RED)
    cv.line(cx, cy + 10, cx, cy + 22, RED)


def icon_missile(cv, x, y, w, h):
    cx, cy = x + w // 2, y + h // 2
    cv.poly([(cx - 12, cy + 34), (cx - 12, cy - 6), (cx, cy - 40),
             (cx + 12, cy - 6), (cx + 12, cy + 34)], BLUE)
    cv.poly([(cx - 12, cy + 12), (cx - 30, cy + 34), (cx - 12, cy + 34)], RED)
    cv.poly([(cx + 12, cy + 12), (cx + 30, cy + 34), (cx + 12, cy + 34)], RED)
    cv.circle(cx, cy - 4, 6, PAPER)
    sx = cx + 78
    for a in range(0, 360, 45):
        import math
        r = 20 if a % 90 == 0 else 10
        cv.line(sx, cy - 30,
                sx + int(r * math.cos(math.radians(a))),
                cy - 30 + int(r * math.sin(math.radians(a))), GOLD)
    cv.disc(sx, cy - 30, 4, GOLD)
    cv.poly([(cx - 8, cy + 34), (cx, cy + 52), (cx + 8, cy + 34)], FIRE)


def icon_fire(cv, x, y, w, h):
    cx = x + w // 2
    base = y + h - 22
    cv.rect(x + 14, base - 22, w - 28, 22, INK)          # tanker body
    cv.rect(x + w - 52, base - 40, 34, 18, INK)          # cab
    cv.disc(x + 44, base, 9, INK)
    cv.disc(x + w - 52, base, 9, INK)
    # flame sized to stay inside the strip: apex no higher than y + 2
    cv.poly([(cx - 22, base - 22), (cx - 28, base - 44), (cx - 10, base - 36),
             (cx, base - 54), (cx + 12, base - 38), (cx + 28, base - 46),
             (cx + 22, base - 22)], FIRE)
    cv.poly([(cx - 10, base - 22), (cx - 13, base - 36), (cx, base - 46),
             (cx + 13, base - 36), (cx + 10, base - 22)], GOLD)


def icon_ebola(cv, x, y, w, h):
    import math
    cx, cy = x + w // 2, y + h // 2
    for k in range(12):
        a = math.radians(k * 30)
        x0, y0 = cx + int(21 * math.cos(a)), cy + int(21 * math.sin(a))
        x1, y1 = cx + int(32 * math.cos(a)), cy + int(32 * math.sin(a))
        cv.line(x0, y0, x1, y1, RED)
        cv.disc(x1, y1, 3, RED)
    cv.disc(cx, cy, 21, RED)
    cv.rect(cx - 4, cy - 11, 8, 22, PAPER)
    cv.rect(cx - 11, cy - 4, 22, 8, PAPER)


def icon_bank(cv, x, y, w, h):
    # bank scaled to stay inside the strip: roof apex at y + 4, base at y + h - 8
    cx = x + w // 2
    base = y + h - 8
    roof_y = y + 4
    col_top = y + 26
    cv.poly([(cx - 66, col_top), (cx, roof_y), (cx + 66, col_top)], BLUE)
    cv.disc(cx, y + 16, 5, PAPER)
    for dx in (-50, -25, 0, 25, 50):
        cv.rect(cx + dx - 6, col_top + 2, 12, base - col_top - 4, BLUE)
    cv.rect(cx - 76, base - 4, 152, 4, INK)
    cv.rect(cx - 76, col_top - 2, 152, 4, INK)


# ---------------------------------------------------------------------------
# The six verified stories of 26 November 2026.
# ---------------------------------------------------------------------------
STORIES = [
    dict(kicker="TRADE WAR  |  WASHINGTON",
         headline="US UNVEILS SWEEPING NEW TARIFFS ON 14 TRADING PARTNERS",
         body=("President Trump announces duties of 15% to 35% on 14 economies, "
               "citing excess industrial capacity. China faces 20%, India 25% "
               "and Vietnam 35%. A public hearing is set for 25 January as "
               "partners warn of retaliation."),
         source="REUTERS", icon=icon_tariffs, lead=True),
    dict(kicker="MIDDLE EAST  |  KUWAIT",
         headline="DRONE STRIKE IN KUWAIT KILLS TWO ITALIANS",
         body=("Two Italian technicians working for Rheinmetall's Italian unit "
               "were killed in a drone attack Italy blames on Iran. Tehran "
               "denies any role as Gulf tensions rise."),
         source="REUTERS", icon=icon_drone),
    dict(kicker="UKRAINE WAR  |  KYIV",
         headline="RUSSIA HITS KYIV AND GRAIN SHIPS AT ODESA",
         body=("Ballistic missiles struck a Kyiv shopping centre, wounding "
               "seven. Two foreign grain ships carrying over 100,000 tonnes "
               "were hit near Odesa ports."),
         source="REUTERS", icon=icon_missile),
    dict(kicker="DISASTER  |  EGYPT",
         headline="CAIRO TANKER FIRE KILLS 31 ON RING ROAD",
         body=("A fuel tanker overturned and exploded on Cairo's Ring Road in "
               "Giza, killing 31 people and charring 27 vehicles. The driver "
               "was detained for speeding."),
         source="REUTERS", icon=icon_fire),
    dict(kicker="HEALTH  |  AFRICA",
         headline="EBOLA IN CONGO TOPS 12,000 CASES",
         body=("Confirmed cases reach 12,021 with 5,904 dead, the second-largest "
               "outbreak on record. Fighting in the east is hampering the "
               "response."),
         source="REUTERS", icon=icon_ebola),
    dict(kicker="EUROPE  |  ECONOMY",
         headline="SPAIN'S DE COS TO LEAD EUROPEAN CENTRAL BANK",
         body=("EU leaders agree to nominate Pablo Hernandez de Cos to succeed "
               "Christine Lagarde in February."),
         source="REUTERS / AL JAZEERA", icon=icon_bank),
]


def panel(cv, x, y, w, h, st, icon_h=84, head_scale=2, body_scale=2):
    cv.rect(x, y, w, h, PANEL)
    cv.rect(x, y, w, h, INK)  # border frame via outline below
    cv.rect(x + 2, y + 2, w - 4, h - 4, PANEL)
    cv.rect(x, y, w, icon_h, SKY)
    cv.hline(x, x + w - 1, y + icon_h, INK, 2)
    st["icon"](cv, x + 8, y + 4, w - 16, icon_h - 8)
    ty = y + icon_h + 12
    cv.draw_text(x + 14, ty, st["kicker"], 1, RED)
    ty += 18
    for line in cv.wrap(st["headline"], w - 28, head_scale):
        cv.draw_text(x + 14, ty, line, head_scale, INK)
        ty += 7 * head_scale + 5
    ty += 2
    cv.hline(x + 14, x + w - 14, ty, GREY, 1)
    ty += 10
    # never let the body run past the SOURCE line: clamp to what fits
    max_lines = max(1, (y + h - 30 - ty) // (7 * body_scale + 4))
    for line in cv.wrap(st["body"], w - 28, body_scale)[:max_lines]:
        cv.draw_text(x + 14, ty, line, body_scale, INK)
        ty += 7 * body_scale + 4
    cv.draw_text(x + 14, y + h - 22, "SOURCE: " + st["source"], 1, GREY)


def build():
    cv = Canvas(W, H, PAPER)

    # ---- masthead -------------------------------------------------------
    cv.draw_centered(W // 2, 26, "THE WORLD IN ONE PAGE", 5, INK)
    cv.hline(28, W - 28, 74, INK, 3)
    cv.hline(28, W - 28, 80, INK, 1)
    cv.draw_centered(W // 2, 92, "THURSDAY, 26 NOVEMBER 2026  |  SIX STORIES THAT DEFINED THE DAY",
                     2, INK)
    cv.hline(28, W - 28, 122, RED, 3)

    # ---- lead story -----------------------------------------------------
    lead = STORIES[0]
    lx, ly, lw, lh = 28, 136, W - 56, 252
    cv.rect(lx, ly, lw, lh, PANEL)
    cv.rect(lx + 2, ly + 2, lw - 4, lh - 4, PANEL)
    for t in range(3):
        cv.hline(lx, lx + lw - 1, ly + t, INK, 1)
        cv.hline(lx, lx + lw - 1, ly + lh - 1 - t, INK, 1)
        cv.vline(lx + t, ly, ly + lh - 1, INK, 1)
        cv.vline(lx + lw - 1 - t, ly, ly + lh - 1, INK, 1)
    tx = lx + 20
    ty = ly + 18
    cv.draw_text(tx, ty, lead["kicker"], 2, RED)
    ty += 30
    for line in cv.wrap(lead["headline"], 560, 3):
        cv.draw_text(tx, ty, line, 3, INK)
        ty += 7 * 3 + 6
    ty += 6
    cv.hline(tx, tx + 560, ty, GREY, 1)
    ty += 12
    for line in cv.wrap(lead["body"], 560, 2):
        cv.draw_text(tx, ty, line, 2, INK)
        ty += 7 * 2 + 5
    cv.draw_text(tx, ly + lh - 26, "SOURCE: " + lead["source"], 1, GREY)
    # illustration: tariff bars on the right of the lead panel
    ix, iy, iw, ih = lx + 620, ly + 14, lw - 640, lh - 28
    cv.rect(ix, iy, iw, ih, SKY)
    cv.rect(ix, iy, iw, 2, INK)
    cv.rect(ix, iy + ih - 2, iw, 2, INK)
    cv.rect(ix, iy, 2, ih, INK)
    cv.rect(ix + iw - 2, iy, 2, ih, INK)
    lead["icon"](cv, ix + 10, iy + 6, iw - 20, ih - 12)

    # ---- row 1: three stories -------------------------------------------
    rw1_y, rw1_h = 404, 268
    pw = (W - 56 - 2 * 16) // 3
    for i, st in enumerate(STORIES[1:4]):
        panel(cv, 28 + i * (pw + 16), rw1_y, pw, rw1_h, st,
              icon_h=84, head_scale=2, body_scale=1)

    # ---- row 2: two stories ---------------------------------------------
    rw2_y, rw2_h = 688, 248
    pw2 = (W - 56 - 16) // 2
    for i, st in enumerate(STORIES[4:6]):
        panel(cv, 28 + i * (pw2 + 16), rw2_y, pw2, rw2_h, st,
              icon_h=80, head_scale=2, body_scale=2)

    # ---- footer ---------------------------------------------------------
    cv.hline(28, W - 28, 952, INK, 2)
    cv.draw_centered(W // 2, 964,
                     "ALL SIX STORIES VERIFIED AGAINST REUTERS AND AL JAZEERA ON 26 NOVEMBER 2026",
                     1, GREY)
    cv.draw_centered(W // 2, 982,
                     "THE WORLD IN ONE PAGE  |  26 NOVEMBER 2026  |  ONE PAGE, SIX STORIES",
                     1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        probe = os.path.join(out_dir, ".probe")
        with open(probe, "w") as f:
            f.write("x")
        os.remove(probe)
    except OSError:
        out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                               "output")
        os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, build())
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
