#!/usr/bin/env python3
"""Build the narrated gas-price video.

Stages:
  python build/build_video.py slides   # render PNG slides for review
  python build/build_video.py audio    # generate narration MP3s
  python build/build_video.py video    # encode segments and concat
  python build/build_video.py all
"""
import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "video"
AUDIO = OUT / "audio"
SLIDES = OUT / "slides"
SEGMENTS = OUT / "segments"
FRAMES = OUT / "frames"
for p in (AUDIO, SLIDES, SEGMENTS, FRAMES):
    p.mkdir(parents=True, exist_ok=True)

W, H = 1920, 1080
BG = (20, 17, 14)
SURFACE = (27, 23, 19)
INK = (238, 232, 220)
SOFT = (211, 201, 185)
MUTED = (161, 150, 138)
LINE = (51, 43, 36)
ACCENT = (201, 106, 61)
ACCENT2 = (224, 160, 90)
GREEN = (143, 174, 130)
DIESEL = (143, 166, 184)

FONTS = Path("C:/Windows/Fonts")
def F(name, size):
    return ImageFont.truetype(str(FONTS / name), size)

SERIF = "georgia.ttf"
SERIF_B = "georgiab.ttf"
SANS = "segoeui.ttf"
SANS_B = "segoeuib.ttf"

DATA = json.loads((ROOT / "data" / "chart_data.json").read_text(encoding="utf-8"))
WEEKLY_2026 = [r for r in DATA["weekly"] if r[0].startswith("2026")]

VOICE = "en-US-AndrewMultilingualNeural"

SCENES = [
    {
        "id": "01-title",
        "kind": "title",
        "narration": (
            "November 2026. Gasoline in America is getting cheaper, fast. "
            "The national average has fallen sixty-six cents in a month. "
            "But the reason is not what most people think."
        ),
    },
    {
        "id": "02-number",
        "kind": "number",
        "narration": (
            "On November 23rd, the national average for regular was three dollars "
            "sixty-four cents a gallon. That is down from four dollars "
            "twenty-nine a month ago. Fifteen percent. The deepest November decline "
            "since 2008. And still fifty-six cents higher than this time last year."
        ),
    },
    {
        "id": "03-timeline",
        "kind": "timeline",
        "narration": (
            "To understand the drop, go back to February. A U.S. Iran war closed most "
            "of the Strait of Hormuz, the passage for about a fifth of the world's oil. "
            "Crude ran to one hundred thirty-six dollars a barrel by October 8th. "
            "Gasoline hit four fifty-six in May, then set a September record of four "
            "forty-eight. Diesel hit an all-time record of six fifty-three."
        ),
    },
    {
        "id": "04-diplomacy",
        "kind": "diplomacy",
        "narration": (
            "Then the war premium cracked. On November 2nd, with midterms the next day, "
            "oil fell more than seven percent as Washington and Tehran signaled they "
            "were open to a deal. By November 6th, Brent had fallen fifteen percent on the week."
        ),
    },
    {
        "id": "05-supply",
        "kind": "supply",
        "narration": (
            "The second force was physical. The barrels came back. Gulf exports recovered "
            "faster than demand. Crude flows through Hormuz returned to eighty-two percent "
            "of pre-war levels. Global supply rose more than two million barrels a day in "
            "October. And the IEA declared the first surplus since the war began, one point "
            "seven million barrels a day in the fourth quarter."
        ),
    },
    {
        "id": "06-chart",
        "kind": "chart",
        "narration": (
            "Seasonality and the station did the rest. Refiners switched to cheaper "
            "winter-blend gasoline. Runs rebounded from their autumn low. And stations, "
            "which had lagged the October spike, began passing through cheaper crude. "
            "Gasoline futures fell to two dollars forty a gallon."
        ),
    },
    {
        "id": "07-otherside",
        "kind": "otherside",
        "narration": (
            "But cheaper is not cheap. Gasoline is still eighteen percent higher than last "
            "year. Diesel is five eighty-two, up fifty-three percent year on year, and only "
            "seventy-one cents below its record. Attacks on Hormuz shipping are at their "
            "highest level since the war began. On-land global stocks are the lowest since at least 2016."
        ),
    },
    {
        "id": "08-closer",
        "kind": "closer",
        "narration": (
            "So where does this go? The EIA sees gasoline averaging three seventy-three in "
            "2027. Goldman sees Brent at eighty-eight next year, falling to seventy-eight by "
            "December 2027. JPMorgan sees the high seventies in the first half. But the war "
            "is not over. President Trump says he does not need a deal, and could strike again. "
            "The war premium is leaving the pump. The war has not left the Gulf."
        ),
    },
]


def tracked(draw, xy, text, font, fill, spacing=2):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + spacing
    return x


def tracked_width(draw, text, font, spacing=2):
    return sum(draw.textlength(ch, font=font) + spacing for ch in text) - spacing


def wrap(draw, text, font, maxw):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(draw, xy, text, font, fill, maxw, leading):
    x, y = xy
    for line in wrap(draw, text, font, maxw):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def base(kicker_text):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((80, 46), "Familiar", font=F(SERIF, 30), fill=INK)
    tracked(d, (250, 52), "RESEARCH REPORT · NOVEMBER 2026", F(SANS, 15), MUTED, 3)
    # live badge
    label = "LIVE DATA · NOV 23, 2026"
    tw = tracked_width(d, label, F(SANS, 15), 2)
    x = W - 80 - tw
    d.ellipse((x - 22, 54, x - 12, 64), fill=GREEN)
    tracked(d, (x, 52), label, F(SANS, 15), SOFT, 2)
    d.line((80, 104, W - 80, 104), fill=LINE, width=1)
    # kicker
    tracked(d, (80, 156), kicker_text, F(SANS, 17), ACCENT2, 4)
    # footer
    d.line((80, 1002, W - 80, 1002), fill=LINE, width=1)
    d.text((80, 1020), "gas-price-drop-2026 · Familiar for Owen", font=F(SANS, 18), fill=MUTED)
    src = "Sources: AAA · EIA · IEA · Reuters · CNN · CNBC · OPEC"
    d.text((W - 80 - d.textlength(src, font=F(SANS, 18)), 1020), src, font=F(SANS, 18), fill=MUTED)
    return img, d


def save(img, name):
    img.save(SLIDES / f"{name}.png", optimize=True)
    print("slide", name)


def title_slide(scene):
    img, d = base("U.S. GASOLINE · NOVEMBER 2026")
    d.text((80, 300), "The war premium", font=F(SERIF, 152), fill=INK)
    d.text((80, 446), "leaves the pump", font=F(SERIF, 152), fill=INK)
    d.line((80, 660, 560, 660), fill=ACCENT, width=3)
    paragraph(
        d, (80, 700),
        "Why U.S. gasoline fell 66 cents in a month — and why the relief is fragile.",
        F(SERIF, 46), SOFT, 1300, 62,
    )
    tracked(d, (80, 870), "NOVEMBER 2026 · A FAMILIAR RESEARCH REPORT", F(SANS, 18), MUTED, 4)
    save(img, scene["id"])


def number_slide(scene):
    img, d = base("THE NUMBER")
    tracked(d, (80, 250), "NATIONAL AVERAGE · REGULAR", F(SANS, 18), MUTED, 3)
    d.text((80, 300), "$3.6366", font=F(SERIF, 260), fill=INK)
    d.text((84, 610), "per gallon · AAA daily survey, November 23, 2026", font=F(SANS, 30), fill=MUTED)

    x = 1210
    rows = [
        ("−65.6¢", GREEN, "vs. one month ago ($4.2926)"),
        ("+56.5¢", ACCENT, "vs. one year ago ($3.0717)"),
        ("−92.3¢", GREEN, "below the 2026 peak ($4.56)"),
    ]
    y = 300
    for big, color, cap in rows:
        d.text((x, y), big, font=F(SERIF, 92), fill=color)
        d.text((x + 4, y + 108), cap, font=F(SANS, 26), fill=MUTED)
        d.line((x, y + 170, W - 80, y + 170), fill=LINE, width=1)
        y += 220

    # small note
    d.text((80, 820), "The pump gave back 66 cents of a 92-cent peak-to-now decline.", font=F(SANS, 26), fill=SOFT)
    save(img, scene["id"])


def timeline_slide(scene):
    img, d = base("HOW WE GOT HERE")
    d.text((80, 230), "A $4.56 year", font=F(SERIF, 118), fill=INK)
    d.text((84, 370), "The war shock, the records, and the November reversal.", font=F(SERIF, 38), fill=SOFT)

    yline = 640
    d.line((120, yline, W - 120, yline), fill=LINE, width=2)
    nodes = [
        ("FEB 28", "War begins", "$2.94"),
        ("MAY 21", "2026 peak", "$4.56"),
        ("SEP 24", "Record for date", "$4.48"),
        ("OCT 8", "Brent peak", "$136"),
        ("NOV 23", "Now", "$3.64"),
    ]
    n = len(nodes)
    for i, (date, label, price) in enumerate(nodes):
        x = 160 + i * (1600 / (n - 1))
        last = i == n - 1
        d.ellipse((x - 9, yline - 9, x + 9, yline + 9), fill=ACCENT if last else INK, outline=BG, width=3)
        tw = d.textlength(date, font=F(SANS, 22))
        tracked(d, (x - tw / 2 - 10, yline - 70), date, F(SANS, 22), ACCENT2 if last else MUTED, 2)
        lw = d.textlength(label, font=F(SANS, 28))
        d.text((x - lw / 2, yline + 30), label, font=F(SANS, 28), fill=INK if last else SOFT)
        pw = d.textlength(price, font=F(SERIF, 46))
        d.text((x - pw / 2, yline + 78), price, font=F(SERIF, 46), fill=ACCENT if last else INK)

    d.line((120, 860, W - 120, 860), fill=LINE, width=1)
    d.text((120, 890), "Diesel set an all-time record of $6.5276 on September 22.", font=F(SANS, 26), fill=MUTED)
    save(img, scene["id"])


def diplomacy_slide(scene):
    img, d = base("WHY IT FELL · DIPLOMACY")
    d.text((80, 230), "The risk premium", font=F(SERIF, 104), fill=INK)
    d.text((80, 340), "cracked first", font=F(SERIF, 104), fill=INK)

    blocks = [
        (80, "−7.4%", "WTI · November 2", "Biggest daily drop since July 27"),
        (900, "−15%", "Brent · week to November 6", "Oil traders priced in peace before the war ended"),
    ]
    for x, big, cap, sub in blocks:
        d.text((x, 520), big, font=F(SERIF, 190), fill=ACCENT)
        d.text((x + 8, 735), cap, font=F(SANS, 28), fill=INK)
        paragraph(d, (x + 8, 780), sub, F(SANS, 26), MUTED, 760, 36)

    d.line((80, 880, W - 80, 880), fill=LINE, width=1)
    d.text((80, 910), "The market had priced in escalation. Then the strike didn't come.",
           font=F(SERIF, 40), fill=SOFT)
    save(img, scene["id"])


def supply_slide(scene):
    img, d = base("WHY IT FELL · SUPPLY")
    d.text((80, 220), "The barrels came back", font=F(SERIF, 104), fill=INK)

    cols = [
        ("82%", "of pre-war Hormuz crude flows restored by October"),
        ("+2.3 mb/d", "global supply growth in October"),
        ("+1.7 mb/d", "IEA's Q4 surplus — the first since the war began"),
    ]
    for i, (big, cap) in enumerate(cols):
        x = 80 + i * 600
        d.text((x, 410), big, font=F(SERIF, 96), fill=ACCENT2)
        paragraph(d, (x, 530), cap, F(SANS, 27), SOFT, 500, 37)

    # flow bar
    y = 760
    d.text((80, y - 40), "Hormuz crude flows, October", font=F(SANS, 24), fill=MUTED)
    d.rectangle((80, y, W - 80, y + 26), fill=SURFACE)
    d.rectangle((80, y, 80 + (W - 160) * 0.82, y + 26), fill=ACCENT)
    d.text((80 + (W - 160) * 0.82 + 16, y - 2), "15 mb/d · 82% of pre-war", font=F(SANS, 24), fill=ACCENT2)

    d.text((80, 860), "Inventories built by 52 million barrels in October — the first build since June.",
           font=F(SANS, 26), fill=MUTED)
    save(img, scene["id"])


def otherside_slide(scene):
    img, d = base("THE OTHER SIDE")
    d.text((80, 220), "Cheaper, not cheap", font=F(SERIF, 118), fill=INK)
    d.text((84, 360), "The headline number hides the pain that didn't go away.", font=F(SERIF, 38), fill=SOFT)

    cells = [
        ("$5.8182", "Diesel · down 49.9¢ in a month, but still +53.4% year on year", ACCENT2),
        ("+18.4%", "Gasoline vs. last November", INK),
        ("30+", "Reported attacks around Hormuz in October, the highest since the war began", INK),
        ("2016", "The last time on-land global oil stocks were this low", INK),
    ]
    for i, (big, cap, color) in enumerate(cells):
        x = 80 + (i % 2) * 900
        y = 480 + (i // 2) * 230
        d.text((x, y), big, font=F(SERIF, 92), fill=color)
        paragraph(d, (x, y + 110), cap, F(SANS, 25), MUTED, 780, 34)
        if i % 2 == 0:
            d.line((x, y, x, y + 190), fill=LINE, width=1)
    d.line((80, 900, W - 80, 900), fill=LINE, width=1)
    d.text((80, 930), "The national average is still 56.5 cents above last year.", font=F(SANS, 28), fill=SOFT)
    save(img, scene["id"])


def closer_slide(scene):
    img, d = base("WHAT HAPPENS NEXT")
    d.text((80, 250), "The war premium is", font=F(SERIF, 118), fill=INK)
    d.text((80, 380), "leaving the pump.", font=F(SERIF, 118), fill=INK)
    d.text((80, 530), "The war has not", font=F(SERIF, 118), fill=ACCENT2)
    d.text((80, 660), "left the Gulf.", font=F(SERIF, 118), fill=ACCENT2)

    d.line((80, 820, 640, 820), fill=ACCENT, width=3)
    d.text((80, 850), "EIA: $3.73 gas in 2027 · Goldman: Brent $88 avg 2027 · JPMorgan: high $70s H1 2027",
           font=F(SANS, 24), fill=MUTED)
    save(img, scene["id"])


def static_slides():
    for scene in SCENES:
        if scene["kind"] == "title":
            title_slide(scene)
        elif scene["kind"] == "number":
            number_slide(scene)
        elif scene["kind"] == "timeline":
            timeline_slide(scene)
        elif scene["kind"] == "diplomacy":
            diplomacy_slide(scene)
        elif scene["kind"] == "supply":
            supply_slide(scene)
        elif scene["kind"] == "otherside":
            otherside_slide(scene)
        elif scene["kind"] == "closer":
            closer_slide(scene)


# ---------- chart scene ----------

def date_ord(s):
    from datetime import date
    y, m, d = map(int, s.split("-"))
    return date(y, m, d).toordinal()


X0, X1 = 130, 1790
Y0, Y1 = 330, 900
D0 = date_ord("2026-01-01")
D1 = date_ord("2026-11-30")
V0, V1 = 2.65, 4.65

def X(d):
    return X0 + (date_ord(d) - D0) / (D1 - D0) * (X1 - X0)

def Y(v):
    return Y1 - (v - V0) / (V1 - V0) * (Y1 - Y0)


def chart_base():
    img, d = base("THE DROP, WEEK BY WEEK")
    d.text((80, 210), "From $4.50 to $3.64", font=F(SERIF, 84), fill=INK)
    # grid
    for v in (3.0, 3.5, 4.0, 4.5):
        y = Y(v)
        d.line((X0, y, X1, y), fill=LINE, width=1)
        d.text((X0 - 16 - d.textlength(f"${v:.2f}", font=F(SANS, 22)), y - 11), f"${v:.2f}",
               font=F(SANS, 22), fill=MUTED)
    # x labels
    for s, lab in [("2026-01-05", "Jan"), ("2026-03-02", "Mar"), ("2026-05-04", "May"),
                   ("2026-07-06", "Jul"), ("2026-09-07", "Sep"), ("2026-11-02", "Nov")]:
        x = X(s)
        d.line((x, Y1, x, Y1 + 8), fill=MUTED, width=1)
        tw = d.textlength(lab, font=F(SANS, 22))
        d.text((x - tw / 2, Y1 + 18), lab, font=F(SANS, 22), fill=MUTED)
    # war band
    wx = X("2026-02-28")
    d.rectangle((wx, Y0, X1, Y1), fill=(28, 22, 18))
    d.line((wx, Y0, wx, Y1), fill=ACCENT, width=1)
    return img, d


def chart_frame(progress, annotate_alpha=0.0):
    img, d = chart_base()
    pts = [(X(r[0]), Y(r[1])) for r in WEEKLY_2026]
    n = len(pts)
    upto = max(2, int(progress * (n - 1)) + 1)
    seg = pts[:upto]
    if len(seg) >= 2:
        d.line(seg, fill=ACCENT, width=5, joint="curve")
    hx, hy = seg[-1]
    d.ellipse((hx - 10, hy - 10, hx + 10, hy + 10), fill=BG, outline=ACCENT, width=4)
    d.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=ACCENT)

    if progress >= 0.985:
        # annotations
        marks = [
            ("2026-02-28", 2.94, "War begins", "Feb 28", "start"),
            ("2026-05-11", 4.50, "Peak $4.50", "May 11", "middle"),
            ("2026-09-21", 4.478, "Autumn $4.48", "Sep 21", "end"),
            ("2026-11-16", 3.805, "Now $3.81", "", "end"),
        ]
        for ds, v, lab, sub, anchor in marks:
            x, y = X(ds), Y(v)
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=INK, outline=BG, width=2)
            tw = d.textlength(lab, font=F(SANS, 23))
            if anchor == "start":
                d.text((x + 12, y - 38), lab, font=F(SANS, 23), fill=SOFT)
            elif anchor == "middle":
                d.text((x - tw / 2, y - 40), lab, font=F(SANS, 23), fill=SOFT)
            else:
                d.text((x - tw - 12, y - 40), lab, font=F(SANS, 23), fill=SOFT)
            if sub:
                sw = d.textlength(sub, font=F(SANS, 19))
                if anchor == "middle":
                    d.text((x - sw / 2, y - 66), sub, font=F(SANS, 19), fill=MUTED)
                elif anchor == "end":
                    d.text((x - sw - 12, y - 66), sub, font=F(SANS, 19), fill=MUTED)
        # big delta, above the plot
        d.text((1470, 150), "−15%", font=F(SERIF, 96), fill=ACCENT2)
        d.text((1476, 248), "in a month", font=F(SANS, 24), fill=MUTED)
    return img


def render_chart_frames(duration):
    frames = int(math.ceil(duration * 30)) + 4
    for i in range(frames):
        p = min(1.0, (i / max(1, frames * 0.55)) ** 0.9)
        img = chart_frame(p)
        img.save(FRAMES / f"f{i:05d}.png", optimize=False)
    print("chart frames", frames)


# ---------- audio / video ----------

def run(cmd):
    print("$", " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def gen_audio():
    for scene in SCENES:
        mp3 = AUDIO / f"{scene['id']}.mp3"
        if mp3.exists() and mp3.stat().st_size > 1000:
            print("audio exists", scene["id"])
            continue
        run(["edge-tts", "--voice", VOICE, "--text", scene["narration"], "--write-media", str(mp3)])
        print("audio", scene["id"], mp3.stat().st_size)


def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=nk=1:nw=1", str(path)
    ]).decode().strip()
    return float(out)


def build_segments():
    segs = []
    for scene in SCENES:
        audio = AUDIO / f"{scene['id']}.mp3"
        dur = duration(audio) + 0.8
        out = SEGMENTS / f"{scene['id']}.mp4"
        fade_out = max(0.1, dur - 0.35)
        if scene["kind"] == "chart":
            render_chart_frames(dur)
            inputs = ["-framerate", "30", "-i", str(FRAMES / "f%05d.png"), "-i", str(audio)]
        else:
            inputs = ["-loop", "1", "-framerate", "30", "-i", str(SLIDES / f"{scene['id']}.png"), "-i", str(audio)]
        vf = f"fade=t=in:st=0:d=0.35,fade=t=out:st={fade_out:.2f}:d=0.35,format=yuv420p"
        cmd = ["ffmpeg", "-y", *inputs, "-vf", vf, "-t", f"{dur:.2f}",
               "-af", "apad=pad_dur=0.8", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
               "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               "-movflags", "+faststart", str(out)]
        run(cmd)
        segs.append(out)
        print("segment", out, f"{dur:.1f}s")
    return segs


def concat(segs):
    listfile = SEGMENTS / "list.txt"
    with listfile.open("w", encoding="utf-8") as fh:
        for s in segs:
            fh.write(f"file '{s.as_posix()}'\n")
    out = OUT / "gas-prices-2026.mp4"
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
         "-movflags", "+faststart", str(out)])
    print("final", out, out.stat().st_size)
    # thumbnail
    run(["ffmpeg", "-y", "-ss", "2", "-i", str(out), "-frames:v", "1", "-q:v", "2",
         str(OUT / "thumbnail.jpg")])


def main():
    stage = sys.argv[1] if len(sys.argv) > 1 else "all"
    if stage in ("slides", "all"):
        static_slides()
        # poster frame for chart review
        chart_frame(1.0).save(SLIDES / "06-chart.png", optimize=True)
        print("slide 06-chart (poster)")
    if stage in ("audio", "all"):
        gen_audio()
    if stage in ("video", "all"):
        if stage == "all":
            # slides are already rendered above; chart frames are rendered per segment
            pass
        segs = build_segments()
        concat(segs)


if __name__ == "__main__":
    main()
