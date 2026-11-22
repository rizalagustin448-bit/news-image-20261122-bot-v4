"""News22 v4 - Six big pictures, clean layout.

One-day newspaper front page, 1024x1024, stdlib only.
Masthead + 12 panels (3x4). Headlines enlarged ~17%, decks trimmed
to 6-8 words, high-contrast dark pictorial scenes.
"""
import math
import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

NAVY = (10, 31, 68)
NAVY_D = (8, 24, 52)
GOLD = (232, 184, 75)
RED = (192, 57, 43)
WHITE = (255, 255, 255)
PAPER = (247, 244, 236)
GREY = (74, 90, 106)
INK = (16, 24, 36)

# 5x7 bitmap font, uppercase + digits + punctuation.
FONT = {
    "A": (" ### ", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "B": ("#### ", "#   #", "#   #", "#### ", "#   #", "#   #", "#### "),
    "C": (" ####", "#    ", "#    ", "#    ", "#    ", "#    ", " ####"),
    "D": ("#### ", "#   #", "#   #", "#   #", "#   #", "#   #", "#### "),
    "E": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#####"),
    "F": ("#####", "#    ", "#    ", "#### ", "#    ", "#    ", "#    "),
    "G": (" ####", "#    ", "#    ", "# ###", "#   #", "#   #", " ### "),
    "H": ("#   #", "#   #", "#   #", "#####", "#   #", "#   #", "#   #"),
    "I": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "#####"),
    "J": ("  ###", "   # ", "   # ", "   # ", "   # ", "#  # ", " ##  "),
    "K": ("#   #", "#  # ", "# #  ", "##   ", "# #  ", "#  # ", "#   #"),
    "L": ("#    ", "#    ", "#    ", "#    ", "#    ", "#    ", "#####"),
    "M": ("#   #", "## ##", "# # #", "# # #", "#   #", "#   #", "#   #"),
    "N": ("#   #", "##  #", "# # #", "#  ##", "#   #", "#   #", "#   #"),
    "O": (" ### ", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "P": ("#### ", "#   #", "#   #", "#### ", "#    ", "#    ", "#    "),
    "Q": (" ### ", "#   #", "#   #", "#   #", "# # #", "#  # ", " ## #"),
    "R": ("#### ", "#   #", "#   #", "#### ", "# #  ", "#  # ", "#   #"),
    "S": (" ####", "#    ", "#    ", " ### ", "    #", "    #", "#### "),
    "T": ("#####", "  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "  #  "),
    "U": ("#   #", "#   #", "#   #", "#   #", "#   #", "#   #", " ### "),
    "V": ("#   #", "#   #", "#   #", "#   #", "#   #", " # # ", "  #  "),
    "W": ("#   #", "#   #", "#   #", "# # #", "# # #", "## ##", "#   #"),
    "X": ("#   #", "#   #", " # # ", "  #  ", " # # ", "#   #", "#   #"),
    "Y": ("#   #", "#   #", " # # ", "  #  ", "  #  ", "  #  ", "  #  "),
    "Z": ("#####", "    #", "   # ", "  #  ", " #   ", "#    ", "#####"),
    "0": (" ### ", "#  ##", "# # #", "##  #", "#   #", "#   #", " ### "),
    "1": ("  #  ", " ##  ", "  #  ", "  #  ", "  #  ", "  #  ", " ### "),
    "2": (" ### ", "#   #", "    #", "   # ", "  #  ", " #   ", "#####"),
    "3": ("#### ", "    #", "    #", " ### ", "    #", "    #", "#### "),
    "4": ("   # ", "  ## ", " # # ", "#  # ", "#####", "   # ", "   # "),
    "5": ("#####", "#    ", "#### ", "    #", "    #", "#   #", " ### "),
    "6": (" ### ", "#    ", "#    ", "#### ", "#   #", "#   #", " ### "),
    "7": ("#####", "    #", "   # ", "  #  ", "  #  ", " #   ", " #   "),
    "8": (" ### ", "#   #", "#   #", " ### ", "#   #", "#   #", " ### "),
    "9": (" ### ", "#   #", "#   #", " ####", "    #", "    #", " ### "),
    " ": ("     ", "     ", "     ", "     ", "     ", "     ", "     "),
    ".": ("     ", "     ", "     ", "     ", "     ", " ##  ", " ##  "),
    ",": ("     ", "     ", "     ", "     ", " ##  ", " ##  ", " #   "),
    ":": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", "     "),
    ";": ("     ", " ##  ", " ##  ", "     ", " ##  ", " ##  ", " #   "),
    "-": ("     ", "     ", "     ", "#####", "     ", "     ", "     "),
    "'": ("  #  ", "  #  ", " #   ", "     ", "     ", "     ", "     "),
    "/": ("    #", "    #", "   # ", "  #  ", " #   ", "#    ", "#    "),
    "%": ("##  #", "## # ", "   # ", "  #  ", " #   ", "# # #", "#  ##"),
    "&": (" ### ", "#   #", "#   #", " #   ", "# # #", "#  # ", " ## #"),
    "$": ("  #  ", " ####", "# #  ", " ### ", "  # #", "#### ", "  #  "),
    "(": ("   # ", "  #  ", " #   ", " #   ", " #   ", "  #  ", "   # "),
    ")": (" #   ", "  #  ", "   # ", "   # ", "   # ", "  #  ", " #   "),
    "!": ("  #  ", "  #  ", "  #  ", "  #  ", "  #  ", "     ", "  #  "),
    "?": (" ### ", "#   #", "    #", "   # ", "  #  ", "     ", "  #  "),
}


class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = int(x), int(y)
        x1, y1 = int(x + w), int(y + h)
        for yy in range(max(0, y0), min(self.h, y1)):
            for xx in range(max(0, x0), min(self.w, x1)):
                self.set(xx, yy, c)

    def hline(self, x, y, n, c):
        for xx in range(int(x), int(x + n)):
            self.set(xx, int(y), c)

    def line(self, x0, y0, x1, y1, c, w=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.rect(x0, y0, w, w, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.hline(cx - dx, cy + dy, 2 * dx + 1, c)

    def triangle(self, p1, p2, p3, c):
        pts = sorted([p1, p2, p3], key=lambda p: p[1])
        (x1, y1), (x2, y2), (x3, y3) = pts

        def interp(y, xa, ya, xb, yb):
            if yb == ya:
                return xa
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y1, y3 + 1):
            if y < y2:
                xa = interp(y, x1, y1, x2, y2)
                xb = interp(y, x1, y1, x3, y3)
            else:
                xa = interp(y, x2, y2, x3, y3)
                xb = interp(y, x1, y1, x3, y3)
            if xa > xb:
                xa, xb = xb, xa
            self.hline(int(xa), y, int(xb) - int(xa) + 1, c)


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_char(cv, ch, x, y, scale, color, bold=False):
    g = FONT.get(ch, FONT[" "])
    for fy, row in enumerate(g):
        for fx, bit in enumerate(row):
            if bit == "#":
                cv.rect(x + fx * scale, y + fy * scale, scale, scale, color)
                if bold:
                    cv.rect(x + fx * scale + max(1.0, scale * 0.22),
                            y + fy * scale, scale * 0.8, scale, color)


def draw_text(cv, s, x, y, scale, color, bold=False):
    cx = x
    for ch in s:
        draw_char(cv, ch, cx, y, scale, color, bold)
        cx += 6 * scale


def draw_center(cv, s, cx, y, scale, color, bold=False):
    draw_text(cv, s, cx - text_w(s, scale) / 2, y, scale, color, bold)


def wrap(text, scale, maxw):
    lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if text_w(t, scale) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


# ---------------- pictorial scenes (dark bg, bright objects) ----------------

def scene_cop31(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (14, 46, 44))
    cv.circle(sx + 262, sy + 22, 16, GOLD)          # sun
    cv.triangle((sx + 10, sy + 74), (sx + 80, sy + 74), (sx + 45, sy + 30),
                (34, 110, 72))                      # hills
    cv.triangle((sx + 90, sy + 74), (sx + 170, sy + 74), (sx + 130, sy + 22),
                (22, 88, 58))
    cv.rect(sx + 200, sy + 40, 4, 34, WHITE)        # flag poles
    cv.rect(sx + 204, sy + 40, 26, 10, RED)
    cv.rect(sx + 200, sy + 54, 4, 20, WHITE)
    cv.rect(sx + 204, sy + 54, 26, 10, (41, 128, 185))
    cv.circle(sx + 40, sy + 18, 5, WHITE)
    cv.circle(sx + 58, sy + 14, 4, WHITE)


def scene_mexico(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (52, 30, 16))
    cv.circle(sx + 40, sy + 20, 14, (240, 140, 60))  # sun
    cv.triangle((sx + 90, sy + 74), (sx + 306, sy + 74), (sx + 200, sy + 28),
                (90, 52, 30))                        # mountains
    cv.rect(sx + 130, sy + 28, 12, 46, (46, 160, 90))  # cactus
    cv.rect(sx + 118, sy + 40, 12, 8, (46, 160, 90))
    cv.rect(sx + 142, sy + 34, 12, 8, (46, 160, 90))
    cv.rect(sx + 250, sy + 44, 8, 30, (46, 160, 90))
    cv.circle(sx + 260, sy + 12, 2, WHITE)
    cv.circle(sx + 285, sy + 20, 2, WHITE)
    cv.circle(sx + 220, sy + 10, 2, WHITE)


def scene_gulf(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (10, 30, 54))
    cv.circle(sx + 270, sy + 16, 12, (240, 230, 200))  # moon
    cv.rect(sx + 30, sy + 38, 170, 14, (200, 210, 220))  # tanker hull
    cv.rect(sx + 30, sy + 30, 40, 8, (200, 210, 220))
    cv.rect(sx + 70, sy + 18, 90, 12, RED)
    cv.rect(sx + 160, sy + 22, 40, 8, GOLD)
    cv.rect(sx + 200, sy + 30, 8, 8, WHITE)
    for wx in (sx + 20, sx + 120, sx + 220):
        cv.line(wx, sy + 60, wx + 22, sy + 60, WHITE, 2)
        cv.line(wx + 30, sy + 68, wx + 52, sy + 68, WHITE, 2)


def scene_ukraine(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (14, 34, 64))
    cv.circle(sx + 36, sy + 18, 12, GOLD)            # sun
    cv.circle(sx + 150, sy + 34, 16, WHITE)          # dove body
    cv.triangle((sx + 166, sy + 30), (sx + 190, sy + 36), (sx + 166, sy + 40),
                GOLD)                                # beak
    cv.triangle((sx + 138, sy + 24), (sx + 158, sy + 10), (sx + 162, sy + 30),
                WHITE)                               # wing
    cv.line(sx + 210, sy + 58, sx + 280, sy + 40, (46, 160, 90), 3)
    cv.circle(sx + 240, sy + 50, 4, (46, 160, 90))
    cv.circle(sx + 262, sy + 44, 4, (46, 160, 90))
    cv.circle(sx + 120, sy + 12, 2, WHITE)
    cv.circle(sx + 220, sy + 14, 2, WHITE)


def scene_baltic(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (12, 28, 44))
    cv.rect(sx + 60, sy + 40, 150, 12, (150, 160, 175))  # ship hull
    cv.rect(sx + 150, sy + 22, 50, 18, (200, 210, 220))  # bridge
    cv.rect(sx + 60, sy + 30, 10, 10, (150, 160, 175))
    cv.circle(sx + 250, sy + 22, 6, (220, 230, 240))     # drone body
    cv.circle(sx + 238, sy + 14, 4, WHITE)
    cv.circle(sx + 262, sy + 14, 4, WHITE)
    cv.line(sx + 238, sy + 18, sx + 250, sy + 20, WHITE, 1)
    cv.line(sx + 250, sy + 20, sx + 262, sy + 18, WHITE, 1)
    for wx in (sx + 20, sx + 110, sx + 210):
        cv.line(wx, sy + 62, wx + 26, sy + 62, (120, 180, 220), 2)


def scene_markets(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (24, 18, 28))
    for bx, bh in ((sx + 12, 40), (sx + 44, 54), (sx + 76, 34)):
        cv.rect(bx, sy + 74 - bh, 24, bh, (52, 58, 72))   # towers
    for wy in range(sy + 30, sy + 70, 8):
        for wx in (sx + 16, sx + 48, sx + 80):
            cv.rect(wx, wy, 4, 4, GOLD)
    pts = [(sx + 120, sy + 16), (sx + 160, sy + 26), (sx + 200, sy + 22),
           (sx + 240, sy + 44), (sx + 280, sy + 58)]
    for a, b in zip(pts, pts[1:]):
        cv.line(a[0], a[1], b[0], b[1], RED, 3)
    cv.triangle((sx + 268, sy + 52), (sx + 292, sy + 52), (sx + 280, sy + 68),
                RED)                                      # down arrow


def scene_peru(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (30, 26, 22))
    cv.triangle((sx + 10, sy + 74), (sx + 130, sy + 74), (sx + 70, sy + 14),
                (120, 120, 130))                         # mountain
    cv.triangle((sx + 56, sy + 28), (sx + 84, sy + 28), (sx + 70, sy + 14),
                WHITE)                                  # snow cap
    cv.triangle((sx + 120, sy + 74), (sx + 250, sy + 74), (sx + 185, sy + 26),
                (90, 90, 100))
    cv.triangle((sx + 172, sy + 38), (sx + 198, sy + 38), (sx + 185, sy + 26),
                WHITE)
    cv.line(sx + 260, sy + 20, sx + 280, sy + 30, GOLD, 2)
    cv.line(sx + 280, sy + 30, sx + 262, sy + 40, GOLD, 2)
    cv.line(sx + 262, sy + 40, sx + 282, sy + 50, GOLD, 2)


def scene_football(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (10, 44, 26))
    cv.rect(sx + 8, sy + 8, 290, 58, (16, 70, 40))
    cv.line(sx + 153, sy + 8, sx + 153, sy + 66, WHITE, 2)
    cv.circle(sx + 153, sy + 37, 10, WHITE)
    cv.rect(sx + 8, sy + 22, 34, 30, (16, 70, 40))
    cv.line(sx + 8, sy + 22, sx + 42, sy + 22, WHITE, 2)
    cv.line(sx + 8, sy + 52, sx + 42, sy + 52, WHITE, 2)
    cv.line(sx + 42, sy + 22, sx + 42, sy + 52, WHITE, 2)
    cv.circle(sx + 240, sy + 44, 12, WHITE)             # ball
    cv.circle(sx + 240, sy + 44, 4, INK)
    cv.circle(sx + 232, sy + 38, 2, INK)
    cv.circle(sx + 248, sy + 38, 2, INK)
    cv.circle(sx + 240, sy + 52, 2, INK)


def scene_gta(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (40, 16, 48))
    cv.circle(sx + 153, sy + 34, 22, (255, 110, 60))     # sunset
    cv.circle(sx + 153, sy + 34, 14, (255, 190, 80))
    for bx, bh in ((sx + 10, 34), (sx + 42, 46), (sx + 74, 28),
                   (sx + 230, 40), (sx + 262, 50)):
        cv.rect(bx, sy + 74 - bh, 26, bh, (24, 10, 34))  # skyline
    for wy in range(sy + 40, sy + 70, 8):
        for wx in (sx + 16, sx + 48, sx + 80, sx + 236, sx + 268):
            cv.rect(wx, wy, 4, 4, (255, 200, 90))
    cv.line(sx + 210, sy + 60, sx + 210, sy + 74, (46, 160, 90), 3)
    cv.line(sx + 210, sy + 60, sx + 196, sy + 48, (46, 160, 90), 2)
    cv.line(sx + 210, sy + 60, sx + 226, sy + 50, (46, 160, 90), 2)


def scene_brazil(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (16, 36, 30))
    cv.rect(sx + 90, sy + 18, 120, 56, (220, 225, 230))  # hospital
    for wy in (sy + 26, sy + 42, sy + 58):
        for wx in (sx + 100, sx + 122, sx + 144, sx + 166, sx + 188):
            cv.rect(wx, wy, 10, 8, (60, 90, 120))
    cv.rect(sx + 140, sy + 26, 20, 8, RED)              # cross
    cv.rect(sx + 146, sy + 20, 8, 20, RED)
    cv.rect(sx + 236, sy + 30, 4, 44, WHITE)            # flag pole
    cv.rect(sx + 240, sy + 30, 30, 12, (0, 150, 90))
    cv.rect(sx + 240, sy + 42, 30, 4, GOLD)


def scene_un(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (12, 32, 58))
    cv.circle(sx + 153, sy + 36, 24, (90, 150, 220))     # globe
    cv.circle(sx + 153, sy + 36, 24, (40, 90, 160))
    cv.line(sx + 153, sy + 12, sx + 153, sy + 60, (180, 210, 240), 2)
    cv.line(sx + 129, sy + 36, sx + 177, sy + 36, (180, 210, 240), 2)
    cv.circle(sx + 153, sy + 36, 18, (180, 210, 240))
    cv.line(sx + 60, sy + 58, sx + 110, sy + 44, (46, 160, 90), 3)
    cv.line(sx + 246, sy + 58, sx + 196, sy + 44, (46, 160, 90), 3)
    cv.circle(sx + 88, sy + 52, 4, (46, 160, 90))
    cv.circle(sx + 218, sy + 52, 4, (46, 160, 90))
    cv.circle(sx + 40, sy + 16, 2, GOLD)
    cv.circle(sx + 270, sy + 16, 2, GOLD)


def scene_nigeria(cv, sx, sy):
    cv.rect(sx, sy, 306, 74, (14, 30, 42))
    cv.circle(sx + 268, sy + 16, 12, (240, 230, 200))    # moon
    cv.rect(sx + 60, sy + 40, 150, 12, (180, 120, 60))   # boat hull
    cv.triangle((sx + 60, sy + 40), (sx + 210, sy + 40), (sx + 135, sy + 52),
                (180, 120, 60))
    cv.rect(sx + 120, sy + 16, 4, 24, WHITE)             # mast
    cv.triangle((sx + 124, sy + 16), (sx + 124, sy + 40), (sx + 160, sy + 40),
                WHITE)                                  # sail
    for wx in (sx + 20, sx + 110, sx + 220):
        cv.line(wx, sy + 60, wx + 26, sy + 60, (120, 180, 220), 2)
        cv.line(wx + 40, sy + 68, wx + 66, sy + 68, (120, 180, 220), 2)


# kicker, (headline line1, line2), deck (6-8 words), accent, scene
STORIES = [
    ("CLIMATE - ANTALYA", ("COP31 TALKS", "IN OVERTIME"),
     "2ND DAY PAST DEADLINE; FOSSIL FUEL TEXT DIVIDES", (0, 150, 136),
     scene_cop31),
    ("MEXICO - SINALOA", ("CARTEL BOSS", "CAPTURED"),
     "EL CHAPO ISIDRO HELD; 11 KILLED", (230, 126, 34), scene_mexico),
    ("GULF - HORMUZ", ("IRAN STRIKES", "IN THE GULF"),
     "BAHRAIN SITE HIT; 2 TANKERS STRUCK OFF OMAN", RED, scene_gulf),
    ("UKRAINE - KYIV", ("PEACE TALKS", "BEFORE XMAS"),
     "ZELENSKY AGREES TO TALKS; GUARANTEES NOT ON PAPER", (41, 128, 185),
     scene_ukraine),
    ("BALTIC - FINLAND", ("DRONES HIT", "RUSSIAN SHIP"),
     "CARGO SHIP SPARTA II DRIFTS TO FINNISH WATERS", (90, 110, 140),
     scene_baltic),
    ("MARKETS - NEW YORK", ("STOCKS SLIDE", "INTO RED"),
     "AI SELL-OFF PUSHES DOW, S&P INTO CORRECTION", (178, 34, 34),
     scene_markets),
    ("PERU - ANDES", ("6.9 QUAKE", "SHAKES PERU"),
     "FELT IN LIMA; NO DAMAGE REPORTED, USGS SAYS", (139, 90, 43),
     scene_peru),
    ("FOOTBALL - ENGLAND", ("LEEDS ROUT", "CHELSEA 4-1"),
     "ARSENAL HELD 2-2 AT NEWCASTLE; ROMA WIN 5-1", (39, 174, 96),
     scene_football),
    ("GAMES - GTA VI", ("GTA VI MAKES", "$3.79 BILLION"),
     "BIGGEST LAUNCH EVER IN 24 HOURS, TAKE-TWO SAYS", (233, 30, 99),
     scene_gta),
    ("BRAZIL - BRASILIA", ("BOLSONARO", "IN HOSPITAL"),
     "EX-PRESIDENT IN INTENSIVE CARE; BOWEL OBSTRUCTION", (22, 160, 90),
     scene_brazil),
    ("UN - GENEVA", ("KILLER ROBOT", "PACT PATH SET"),
     "STATES AGREE 2 YEARS OF AUTONOMOUS WEAPONS TALKS", (0, 90, 160),
     scene_un),
    ("NIGERIA - BAYELSA", ("BOAT SINKS", "24 DEAD"),
     "MOURNERS ON WAY TO FUNERAL, NEMA SAYS", (210, 140, 20),
     scene_nigeria),
]


def build():
    cv = Canvas(W, H)
    cv.rect(0, 0, W, H, PAPER)

    # Masthead: navy band, white title, gold date.
    cv.rect(0, 0, W, 110, NAVY)
    draw_center(cv, "THE WORLD IN ONE DAY", W // 2, 10, 5, WHITE, bold=True)
    draw_center(cv, "SUNDAY, 22 NOVEMBER 2026", W // 2, 54, 4, GOLD,
                bold=True)
    cv.rect(0, 112, W, 4, RED)
    cv.rect(0, 118, W, 4, GOLD)

    # Grid: 3 cols x 4 rows, panels 330x210.
    for idx, (kicker, head, deck, accent, scene) in enumerate(STORIES):
        col, row = idx % 3, idx // 3
        x0 = 10 + col * 337
        y0 = 126 + row * 216
        cv.rect(x0, y0, 330, 210, WHITE)
        cv.rect(x0, y0, 330, 6, accent)
        draw_text(cv, kicker, x0 + 12, y0 + 13, 2, accent, bold=True)
        scene(cv, x0 + 12, y0 + 32)
        # Headlines enlarged ~17% (scale 3.5), navy bold, 2 lines.
        draw_text(cv, head[0], x0 + 12, y0 + 112, 3.6, NAVY, bold=True)
        draw_text(cv, head[1], x0 + 12, y0 + 138, 3.6, NAVY, bold=True)
        # Deck: one short sentence, max 2 lines, grey.
        for li, ln in enumerate(wrap(deck, 2, 306)):
            draw_text(cv, ln, x0 + 12, y0 + 170 + li * 15, 2, GREY)

    # Footer.
    draw_center(cv, "SOURCES: BBC | AP | REUTERS | TAKE-TWO | USGS",
                W // 2, 996, 2, GREY)
    return cv


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, data):
        out = struct.pack(">I", len(data)) + t + data
        return out + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out.mkdir(parents=True, exist_ok=True)
    data = png_bytes(build())
    (out / "entry.png").write_bytes(data)


if __name__ == "__main__":
    main()
