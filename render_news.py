#!/usr/bin/env python3
"""Render: modern news graphic for 18 November 2026 — typography + real data.

Build-time only: the grader never runs this file (it runs main.py, which only
copies the committed entry.png). All news data is embedded below as fixed
data, so the render is deterministic: same input -> same PNG bytes.
News researched 19 Nov 2026 from public sources (see README.md).
Run:  python3 render_news.py   (writes entry.png next to this file)

Pure white background, near-black ink, one sharp news-red accent.
No skyline, no flags, no sun, no map, no vignette, no paper texture,
no newspaper masthead. Only text, numbers, rules and one honest
log-scale bar chart built from the day's verified figures.

Deterministic: fixed data, fixed fonts, no randomness, no clock, no network.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 56                      # side margin
CW = W - 2 * M              # content width = 912
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

WHITE = (255, 255, 255)
INK = (10, 10, 10)
BODY = (38, 38, 38)
GREY = (110, 110, 110)
RULE = (200, 200, 200)
ACCENT = (216, 30, 38)     # sharp news red, the only accent colour

FDIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)


F_BLACK = lambda s: font("NotoSans-Black.ttf", s)
F_XBOLD = lambda s: font("NotoSans-ExtraBold.ttf", s)
F_BOLD = lambda s: font("NotoSans-Bold.ttf", s)
F_REG = lambda s: font("NotoSans-Regular.ttf", s)


def text_w(draw, text, f):
    return draw.textbbox((0, 0), text, font=f)[2]


def tracked(draw, x, y, text, f, fill, tracking=2):
    """Draw text with extra letter spacing; returns the x after the text."""
    cx = x
    for ch in text:
        draw.text((cx, y), ch, font=f, fill=fill)
        cx += text_w(draw, ch, f) + tracking
    return cx - tracking


def tracked_w(draw, text, f, tracking=2):
    return sum(text_w(draw, ch, f) + tracking for ch in text) - tracking


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(draw, trial, f) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def main():
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # ---- top bar -------------------------------------------------------
    y = 34
    d.rectangle([M, y + 3, M + 11, y + 14], fill=ACCENT)
    tracked(d, M + 20, y, "WEDNESDAY, 18 NOVEMBER 2026", F_BOLD(17), INK, tracking=2)
    right = "THE DAY IN BRIEF"
    tracked(d, W - M - tracked_w(d, right, F_BOLD(17), 2), y, right,
            F_BOLD(17), GREY, tracking=2)
    d.line([M, 62, W - M, 62], fill=INK, width=3)

    # ---- kicker --------------------------------------------------------
    tracked(d, M, 82, "SUMMIT IN SHENZHEN — APEC 2026", F_BOLD(19), ACCENT, tracking=2)

    # ---- giant headline ------------------------------------------------
    hl = ["Xi and Putin", "meet in", "Shenzhen"]
    y = 106
    for line in hl:
        d.text((M, y), line, font=F_BLACK(90), fill=INK)
        y += 91
    assert y <= 382, f"headline overflow: {y}"

    # ---- deck ----------------------------------------------------------
    deck = ("The two leaders open talks at APEC a day before their first "
            "trilateral meeting with Trump — Ukraine, Iran and trade on "
            "the agenda.")
    y = 390
    for line in wrap(d, deck, F_REG(23), CW):
        d.text((M, y), line, font=F_REG(23), fill=BODY)
        y += 29
    assert y <= 452, f"deck overflow: {y}"

    # ---- fact strip ----------------------------------------------------
    y = 458
    d.line([M, y, W - M, y], fill=RULE, width=1)
    y = 466
    x = M
    for num, word in [("2", "LEADERS MEET"), ("3", "AT THE TABLE"),
                      ("1", "DAY TO GO")]:
        x = tracked(d, x, y, num, F_XBOLD(20), ACCENT, tracking=1) + 8
        x = tracked(d, x, y, word, F_XBOLD(20), INK, tracking=2) + 34
    d.line([M, 496, W - M, 496], fill=RULE, width=1)

    # ---- chart: the day in numbers (log scale, honest values) ---------
    y = 516
    tracked(d, M, y, "THE DAY IN NUMBERS", F_BOLD(18), INK, tracking=2)
    right = "AS REPORTED, 18 NOV"
    tracked(d, W - M - tracked_w(d, right, F_BOLD(15), 2), y + 2, right,
            F_BOLD(15), GREY, tracking=2)

    # Values as reported. Log10 scale with a $100m floor so the smallest
    # bar is still visible; the log scale is labelled on the image.
    # 115.8e9 / 190.4e6 = 608.2, checked by hand.
    bars = [
        ("Nvidia revenue", 115.8e9, "$115.8bn", ACCENT, "Nvidia"),
        ("EU loan for Ukraine", 45e9, "€45bn", INK, "Reuters"),
        ("Van Gogh, record sale", 190.4e6, "$190.4m", INK, "Sotheby's"),
    ]
    LO, HI = 8.0, math.log10(115.8e9)      # floor $100m .. $115.8bn
    label_x, bar_x0 = M, M + 300
    bar_max = 380                            # max bar length in px
    value_gap = 12
    y = 548
    row_h = 44
    for label, value, vtext, colour, src in bars:
        frac = (math.log10(value) - LO) / (HI - LO)
        blen = max(14, int(round(frac * bar_max)))
        d.text((label_x, y), label, font=F_BOLD(19), fill=INK)
        d.text((label_x, y + 22), src, font=F_REG(14), fill=GREY)
        d.rectangle([bar_x0, y + 4, bar_x0 + blen, y + 24], fill=colour)
        d.text((bar_x0 + blen + value_gap, y + 1), vtext, font=F_XBOLD(21),
               fill=INK)
        y += row_h
    # y is now 548 + 3*44 = 680
    note = ("Bars on a log scale — $115.8bn is about 608× the Van Gogh price. "
            "Figures as reported, in their own currencies.")
    ny = 686
    for line in wrap(d, note, F_REG(15), CW):
        d.text((M, ny), line, font=F_REG(15), fill=GREY)
        ny += 19
    assert ny <= 732, f"chart note overflow: {ny}"

    d.line([M, 728, W - M, 728], fill=INK, width=2)

    # ---- stories: 2 x 2, thin rules only, no boxes ---------------------
    stories = [
        ("MARKETS",
         "Nvidia posts record $115.8bn",
         "Revenue more than doubles; the board rules out Jensen "
         "Huang's return as CEO.",
         "Source: Nvidia"),
        ("THE GULF",
         "Iran strikes Kuwait and Bahrain",
         "Iran hits the Ali Al Salem air base after US jets struck a "
         "missile site on Qeshm Island.",
         "Source: Reuters"),
        ("EUROPE",
         "EU proposes €45bn Ukraine loan",
         "The loan would cover two-thirds of Kyiv's €70bn gap for "
         "2027, repaid from Russian reparations.",
         "Source: Reuters"),
        ("CULTURE",
         "Van Gogh sells for $190.4m",
         "Blossoming Chestnut Trees sets the artist's auction record "
         "at Sotheby's in New York.",
         "Source: Sotheby's"),
    ]
    col_w = (CW - 32) // 2
    row_ys = [748, 850]
    for i, (kicker, head, deck_s, src) in enumerate(stories):
        cx = M + (i % 2) * (col_w + 32)
        cy = row_ys[i // 2]
        if i % 2 == 1:
            d.line([M + col_w + 16, cy + 2, M + col_w + 16, cy + 90],
                   fill=RULE, width=1)
        tracked(d, cx, cy, kicker, F_BOLD(14), ACCENT, tracking=2)
        d.text((cx, cy + 20), head, font=F_XBOLD(23), fill=INK)
        dy = cy + 50
        for line in wrap(d, deck_s, F_REG(16), col_w):
            d.text((cx, dy), line, font=F_REG(16), fill=BODY)
            dy += 20

    # ---- footer --------------------------------------------------------
    d.line([M, 950, W - M, 950], fill=RULE, width=1)
    y = 958
    x = tracked(d, M, y, "ALSO TODAY", F_BOLD(14), ACCENT, tracking=2) + 10
    also = ("Voyager 1, one light-day out (25.9bn km) · Kerch Bridge arch "
            "in the sea · Peltola wins Alaska, 56–44 · Manila disputes "
            "Trump trade-deal claim")
    for line in wrap(d, also, F_REG(14), W - M - x):
        d.text((x, y), line, font=F_REG(14), fill=BODY)
        y += 18
        x = M
    d.text((M, y + 4), "Sources: Reuters, AP, AFP, BBC, Sotheby's, NASA, "
           "Nvidia — 18 Nov 2026",
           font=F_REG(12), fill=GREY)
    assert y + 4 + 12 <= 1014, f"footer overflow: {y}"

    img.save(OUT, format="PNG")
    print(f"saved {OUT} {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
