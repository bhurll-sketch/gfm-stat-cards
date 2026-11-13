"""GFM Review card and carousel renderer (spec: Project instructions, sections 6 and 7).

Usage:
  python3 -I tools/gfm_render.py card     spec.json  out.png
  python3 -I tools/gfm_render.py carousel spec.json  out_dir   (writes slide PNGs + PDF)

Card spec:
  {"kicker": "US INFLATION", "big": "+0.4%",
   "headline": "US consumer prices rose faster than forecast in October",
   "stats": [{"label": "Core CPI", "value": "+0.3%", "tone": "up"}, ...],   # 2 or 3, tone up|down|neutral
   "source": "Source: BLS, Reuters. 10 Nov 2026"}

Carousel spec:
  {"date_label": "9 to 12 Nov 2026", "file_stub": "week-in-markets_13nov",
   "cover": {"big": "-2.7%", "headline": ["The S&P 500's worst week", "since April 2025"],
             "context": "One line of context."},
   "slides": [{"kicker": "THE SCOREBOARD", "title": "Tech took the hardest hit",
               "subtitle": "Weekly change, major US indexes",
               "chart": {"type": "hbar", "labels": [...], "values": [...], "tone": "down|up|neutral",
                         "suffix": "%", "decimals": 1, "signed": true},
               "keyfig": "optional gold line"},
              {"chart": {"type": "line", "labels": ["6 Oct\\nrecord", ...], "values": [...], "decimals": 0}}],
   "watch": [["Tue 17 Nov", "US retail sales"], ...]}
"""
import io, json, os, sys
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
BG_TOP, BG_BOT = (10, 22, 41), (16, 36, 62)
INK, MUTED, KICKER = (243, 244, 246), (170, 182, 198), (120, 150, 190)
GOLD, RULE, PANEL = (212, 167, 44), (60, 78, 104), (22, 44, 74)
TONE = {"down": (232, 104, 104), "up": (88, 196, 140), "neutral": (79, 155, 230)}

FD = "/usr/share/fonts/truetype/google-fonts/"
_fallback = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf"
def F(style, size):
    p = FD + f"Poppins-{style}.ttf"
    if not os.path.exists(p):
        p = _fallback % ("-Bold" if style == "Bold" else "")
    return ImageFont.truetype(p, size)

for s in ("Regular", "Medium", "Bold"):
    p = FD + f"Poppins-{s}.ttf"
    if os.path.exists(p):
        font_manager.fontManager.addfont(p)
plt.rcParams["font.family"] = "Poppins" if os.path.exists(FD + "Poppins-Regular.ttf") else "DejaVu Sans"

LOGO = Image.open(os.path.join(HERE, "assets", "logo_box.png")).convert("RGBA")
_face = Image.open(os.path.join(HERE, "assets", "portrait.png")).convert("RGBA").resize((300, 300), Image.LANCZOS)
_mask = Image.new("L", _face.size, 0); ImageDraw.Draw(_mask).ellipse((0, 0, 299, 299), fill=255)
FACE = Image.new("RGBA", _face.size, (0, 0, 0, 0)); FACE.paste(_face, (0, 0), _mask)

hexc = lambda c: "#%02x%02x%02x" % c


def canvas():
    im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3)))
    return im


def centre(d, y, text, font, fill):
    d.text(((W - d.textlength(text, font=font)) / 2, y), text, font=font, fill=fill)


def wrap(d, text, font, maxw):
    lines, cur = [], ""
    for wd in text.split():
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    lines.append(cur)
    return [l for l in lines if l]


def fit(d, text, style, size, maxw, min_size=60):
    while size > min_size and d.textlength(text, font=F(style, size)) > maxw:
        size -= 6
    return F(style, size)


def portrait(im, d, x, y, size):
    fc = FACE.resize((size, size), Image.LANCZOS)
    im.paste(fc, (x, y), fc)
    d.ellipse((x - 2, y - 2, x + size + 2, y + size + 2), outline=GOLD, width=4)


def header(im, kicker):
    d = ImageDraw.Draw(im)
    lw = 420
    lg = LOGO.resize((lw, int(LOGO.height * lw / LOGO.width)), Image.LANCZOS)
    im.paste(lg, ((W - lw) // 2, 56), lg)
    y = 56 + lg.height + 34
    centre(d, y, kicker.upper(), F("Bold", 26), KICKER)
    return d, y + 60


def footer(d, page=None):
    d.line([(90, H - 120), (W - 90, H - 120)], fill=RULE, width=2)
    d.text((90, H - 98), "gfmreview.com", font=F("Medium", 30), fill=GOLD)
    if page:
        f = F("Medium", 28)
        d.text((W - 90 - d.textlength(page, font=f), H - 96), page, font=f, fill=MUTED)


def byline(im, d, y):
    portrait(im, d, W - 90 - 150, y, 150)
    d.text((90, y + 30), "Brett Hurll", font=F("Bold", 34), fill=INK)
    d.text((90, y + 76), "Editor, GFM Review", font=F("Regular", 28), fill=MUTED)


# ---------- standard card ----------
def render_card(spec, out):
    im = canvas(); d, y = header(im, spec["kicker"])
    big = spec["big"]
    fb = fit(d, big, "Bold", 210, W - 160)
    centre(d, 360, big, fb, INK)
    y = 360 + fb.size + 40
    for ln in wrap(d, spec["headline"], F("Medium", 38), W - 220)[:3]:
        centre(d, y, ln, F("Medium", 38), MUTED); y += 54
    stats = spec.get("stats", [])[:3]
    if stats:
        y += 36
        n = len(stats); gap = 20; bw = (W - 180 - gap * (n - 1)) // n
        for i, s in enumerate(stats):
            x = 90 + i * (bw + gap)
            d.rounded_rectangle((x, y, x + bw, y + 150), radius=18, fill=PANEL)
            col = TONE.get(s.get("tone", "neutral"), TONE["neutral"])
            fv = fit(d, s["value"], "Bold", 50, bw - 30, 30)
            d.text((x + (bw - d.textlength(s["value"], font=fv)) / 2, y + 26), s["value"], font=fv, fill=col)
            fl = fit(d, s["label"], "Medium", 26, bw - 24, 18)
            d.text((x + (bw - d.textlength(s["label"], font=fl)) / 2, y + 100), s["label"], font=fl, fill=MUTED)
        y += 150
    if spec.get("source"):
        centre(d, y + 28, spec["source"], F("Regular", 22), KICKER)
    byline(im, d, H - 300)
    footer(d)
    im.save(out, optimize=True)
    return out


# ---------- charts ----------
def _fmt(v, c):
    dec = c.get("decimals", 1)
    s = f"{v:,.{dec}f}"
    if c.get("signed") and v > 0: s = "+" + s
    return c.get("prefix", "") + s + c.get("suffix", "")


def _png(fig):
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=200, transparent=True); plt.close(fig)
    buf.seek(0); return Image.open(buf).convert("RGBA")


def chart(c):
    fig, ax = plt.subplots(figsize=(4.5, 3.5))
    vals, labels = c["values"], c["labels"]
    if c["type"] == "hbar":
        col = hexc(TONE.get(c.get("tone", "neutral"), TONE["neutral"]))
        ys = list(range(len(labels)))[::-1]
        ax.barh(ys, vals, height=0.56, color=col)
        lo, hi = min(0, min(vals)), max(0, max(vals)); span = (hi - lo) or 1
        ax.set_xlim(lo - span * (0.35 if lo < 0 else 0.02), hi + span * (0.35 if hi > 0 else 0.02))
        ax.axvline(0, color=hexc(MUTED), lw=1)
        ax.set_yticks(ys); ax.set_yticklabels(labels, color=hexc(INK), fontsize=11, fontweight="medium")
        ax.set_xticks([])
        for yi, v in zip(ys, vals):
            off = span * 0.03
            ax.text(v - off if v < 0 else v + off, yi, _fmt(v, c), va="center", ha="right" if v < 0 else "left",
                    color=hexc(INK), fontsize=11, fontweight="bold")
    else:
        col = hexc(TONE["neutral"]); xs = list(range(len(vals)))
        ax.plot(xs, vals, color=col, lw=2.2, zorder=2)
        ax.scatter(xs, vals, s=46, color=col, edgecolor=hexc(BG_BOT), linewidth=2, zorder=3)
        lo, hi = min(vals), max(vals); span = (hi - lo) or 1
        for x, v in zip(xs, vals):
            ax.text(x, v + span * 0.07, _fmt(v, c), ha="center", color=hexc(INK), fontsize=10.5, fontweight="bold")
        ax.set_xticks(xs); ax.set_xticklabels(labels, color=hexc(MUTED), fontsize=9.5)
        ax.set_ylim(lo - span * 0.2, hi + span * 0.25); ax.set_yticks([]); ax.set_xlim(-0.4, len(vals) - 0.6)
    for s in ax.spines.values(): s.set_visible(False)
    ax.tick_params(length=0, pad=8)
    fig.tight_layout()
    img = _png(fig)
    return img.resize((W - 160, int(img.height * (W - 160) / img.width)), Image.LANCZOS)


# ---------- carousel ----------
def render_carousel(spec, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    total = len(spec["slides"]) + 2
    slides = []
    cv = spec["cover"]
    im = canvas(); d, y = header(im, f"Week in Markets  |  {spec['date_label']}")
    fb = fit(d, cv["big"], "Bold", 230, W - 160)
    centre(d, 430, cv["big"], fb, INK)
    y = 720
    for ln in cv["headline"][:2]:
        centre(d, y, ln, F("Bold", 44), INK); y += 60
    y += 14
    for ln in wrap(d, cv.get("context", ""), F("Regular", 30), W - 240)[:2]:
        centre(d, y, ln, F("Regular", 30), MUTED); y += 44
    centre(d, 1000, "Swipe for the charts  >", F("Bold", 30), GOLD)
    byline(im, d, H - 330); footer(d, f"1 / {total}")
    slides.append(im)

    for i, s in enumerate(spec["slides"], 2):
        im = canvas(); d, y = header(im, s["kicker"])
        for ln in wrap(d, s["title"], F("Bold", 54), W - 180)[:2]:
            centre(d, y, ln, F("Bold", 54), INK); y += 70
        y += 6
        for ln in wrap(d, s.get("subtitle", ""), F("Regular", 30), W - 200)[:2]:
            centre(d, y, ln, F("Regular", 30), MUTED); y += 44
        y += 20
        ch = chart(s["chart"]); im.paste(ch, (80, y), ch)
        if s.get("keyfig"):
            d.text((90, min(y + ch.height + 10, H - 180)), s["keyfig"], font=F("Bold", 32), fill=GOLD)
        footer(d, f"{i} / {total}")
        slides.append(im)

    im = canvas(); d, y = header(im, "What to watch next"); y += 10
    for date, what in spec["watch"][:4]:
        d.rounded_rectangle((90, y, W - 90, y + 104), radius=18, fill=PANEL)
        d.text((126, y + 30), date, font=F("Bold", 32), fill=GOLD)
        d.text((390, y + 30), what, font=fit(d, what, "Medium", 32, W - 90 - 390 - 30, 20), fill=INK)
        y += 124
    y += 30
    portrait(im, d, (W - 150) // 2, y, 150); y += 175
    centre(d, y, "Follow Brett Hurll for the weekly briefing", F("Bold", 34), INK); y += 52
    centre(d, y, "DM 'Brief' for this week's full note", F("Regular", 30), MUTED)
    footer(d, f"{total} / {total}")
    slides.append(im)

    stub = spec["file_stub"]; paths = []
    for n, s in enumerate(slides, 1):
        p = os.path.join(out_dir, f"{stub}_slide{n}.png"); s.save(p, optimize=True); paths.append(p)
    pdf = os.path.join(out_dir, f"{stub}.pdf")
    slides[0].save(pdf, save_all=True, append_images=slides[1:], resolution=150)
    paths.append(pdf)
    return paths


if __name__ == "__main__":
    kind, spec_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
    spec = json.load(open(spec_path))
    res = render_card(spec, out) if kind == "card" else render_carousel(spec, out)
    print(res if isinstance(res, str) else "\n".join(res))
