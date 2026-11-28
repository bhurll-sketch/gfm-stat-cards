#!/usr/bin/env python3
"""GFM Review article artwork and infographics, v2 (28 Nov 2026).

Usage:
  python3 -I gfm_art.py artwork <spec.json> <out.jpg>
  python3 -I gfm_art.py infographic <spec.json> <out.jpg>

Fonts: Noto Serif (headlines), Open Sans (everything else), bundled in fonts/.
Palettes: six blue gradients, one muted gold accent.
"""
import json, math, os, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageStat

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.path.join(HERE, 'fonts')
GOLD = (196, 160, 82)

PALETTES = {
    # name: (top colour, bottom colour, headline, body text, dark?)
    'pale_sky':  ((246, 249, 253), (214, 228, 244), (16, 36, 66), (70, 88, 112), False),
    'steel':     ((236, 240, 245), (190, 203, 219), (20, 34, 56), (64, 78, 98), False),
    'ocean':     ((222, 238, 246), (150, 192, 214), (10, 40, 64), (40, 70, 92), False),
    'ice':       ((252, 253, 255), (229, 240, 251), (22, 44, 78), (86, 104, 128), False),
    'navy_night':((24, 44, 82), (9, 20, 42), (255, 255, 255), (190, 205, 225), True),
    'twilight':  ((40, 58, 104), (112, 122, 178), (255, 255, 255), (222, 228, 245), True),
}


def font(kind, size):
    w = {'serif': 'noto-serif-600', 'serif-b': 'noto-serif-700', 'sans': 'open-sans-400',
         'sans-sb': 'open-sans-600', 'sans-b': 'open-sans-700'}[kind]
    return ImageFont.truetype(os.path.join(FD, w + '.ttf'), size)


def gradient(w, h, pal, angle=0):
    a, b = pal[0], pal[1]
    base = Image.new('RGB', (w, h))
    px = base.load()
    ca, sa = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    span = abs(w * sa) + abs(h * ca)
    for y in range(h):
        for x in range(0, w, 1):
            t = ((x - w / 2) * sa + (y - h / 2) * ca) / span + 0.5
            t = min(1, max(0, t))
            px[x, y] = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return base


def fast_gradient(w, h, pal, angle=0):
    small = gradient(180, 120, pal, angle)
    return small.resize((w, h), Image.BICUBIC)


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def fit_text(draw, text, kind, maxw, maxh, start, minsize=28, spacing=1.12):
    size = start
    while size >= minsize:
        f = font(kind, size)
        lines = wrap(draw, text, f, maxw)
        h = len(lines) * size * spacing
        if h <= maxh and all(draw.textlength(l, font=f) <= maxw for l in lines):
            return f, lines, size
        size -= 2
    raise ValueError(f'Text does not fit: {text!r}')


def draw_lines(draw, xy, lines, f, size, fill, spacing=1.12, anchor='la', align_center=False, w=None):
    x, y = xy
    for i, l in enumerate(lines):
        if align_center:
            lw = draw.textlength(l, font=f)
            draw.text((x + (w - lw) / 2, y + i * size * spacing), l, font=f, fill=fill)
        else:
            draw.text((x, y + i * size * spacing), l, font=f, fill=fill)
    return y + len(lines) * size * spacing


def mark(img, pal, x=70, y=64):
    d = ImageDraw.Draw(img)
    f = font('sans-b', 26)
    d.ellipse((x, y + 9, x + 12, y + 21), fill=GOLD)
    txt = 'G F M   R E V I E W'
    d.text((x + 26, y), txt, font=f, fill=pal[2])


def kicker(img, pal, text, x, y, color=None):
    d = ImageDraw.Draw(img)
    d.rectangle((x, y + 14, x + 54, y + 17), fill=GOLD)
    d.text((x + 72, y), text.upper(), font=font('sans-b', 24), fill=color or pal[3], spacing=4)


def is_light(im):
    a = im.split()[-1] if im.mode == 'RGBA' else None
    rgb = im.convert('RGB')
    st = ImageStat.Stat(rgb, mask=a.point(lambda v: 255 if v > 40 else 0) if a else None)
    return sum(st.mean[:3]) / 3 > 215


def tile(item, w, h, pal, name_size=30):
    """A logo (or name) on a rounded tile with a soft shadow. Returns RGBA."""
    pad = 18
    canvas = Image.new('RGBA', (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    logo = None
    if item.get('logo') and os.path.exists(item['logo']):
        logo = Image.open(item['logo']).convert('RGBA')
        bbox = logo.getbbox()
        if bbox:
            logo = logo.crop(bbox)
    bg = (255, 255, 255)
    if logo is not None and is_light(logo):
        bg = (16, 36, 66)
    sh = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 6, pad + w, pad + h + 6), 14, fill=(10, 25, 50, 70 if not pal[4] else 140))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    canvas.alpha_composite(sh)
    ImageDraw.Draw(canvas).rounded_rectangle((pad, pad, pad + w, pad + h), 14, fill=bg + (255,))
    if logo is not None:
        lw, lh = w - 44, h - 30
        r = min(lw / logo.width, lh / logo.height)
        lg = logo.resize((max(1, int(logo.width * r)), max(1, int(logo.height * r))), Image.LANCZOS)
        canvas.alpha_composite(lg, (pad + (w - lg.width) // 2, pad + (h - lg.height) // 2))
    else:
        d = ImageDraw.Draw(canvas)
        s = name_size
        f = font('sans-sb', s)
        while d.textlength(item['name'], font=f) > w - 30 and s > 16:
            s -= 1
            f = font('sans-sb', s)
        tw = d.textlength(item['name'], font=f)
        d.text((pad + (w - tw) / 2, pad + h / 2 - s * 0.62), item['name'], font=f, fill=(16, 36, 66))
    return canvas, pad


def paste_tile(img, item, x, y, w, h, pal, placed, gap=12):
    for (a, b, c, d) in placed:  # overlap check first, then draw
        if x - gap < c and x + w + gap > a and y - gap < d and y + h + gap > b:
            raise ValueError(f'Tiles overlap at {item["name"]}')
    W, H = img.size
    if x < 20 or y < 20 or x + w > W - 20 or y + h > H - 20:
        raise ValueError(f'Tile off the canvas: {item["name"]}')
    t, pad = tile(item, w, h, pal)
    img.alpha_composite(t, (int(x - pad), int(y - pad)))
    placed.append((x, y, x + w, y + h))


# ---------------- artwork layouts ----------------

def layout_cover(img, spec, pal):
    """Headline-led: big serif headline over the top, logo row(s) along the bottom."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    mark(img, pal)
    items = spec['companies'][:10]
    n = len(items)
    rows = 1 if n <= 5 else 2
    free_top, free_bot = 150, 1200 - 70 - rows * 118 - (rows - 1) * 26 - 90
    f, lines, s = fit_text(d, spec['label'], 'serif', W - 260, free_bot - free_top - 80, 132)
    hh = len(lines) * s * 1.12 + 70
    ty = free_top + (free_bot - free_top - hh) / 2
    kicker(img, pal, spec['kicker'], 70, ty)
    draw_lines(d, (70, ty + 70), lines, f, s, pal[2])
    per = math.ceil(n / rows)
    gap = 26
    tw = int((W - 140 - gap * (per - 1)) / per)
    th = 118
    placed = []
    y0 = H - 70 - rows * th - (rows - 1) * gap
    d.line((70, y0 - 44, W - 70, y0 - 44), fill=GOLD, width=3)
    for i, it in enumerate(items):
        r, c = divmod(i, per)
        cnt = per if r < rows - 1 else n - per * (rows - 1)
        off = (W - 140 - (cnt * tw + (cnt - 1) * gap)) / 2
        paste_tile(img, it, 70 + off + c * (tw + gap), y0 + r * (th + gap), tw, th, pal, placed)


def layout_split(img, spec, pal):
    """Split panel: headline on a solid block left, logo mosaic right."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    pw = int(W * 0.44)
    block = (16, 36, 66) if not pal[4] else (255, 255, 255)
    btxt = (255, 255, 255) if not pal[4] else (16, 36, 66)
    d.rectangle((0, 0, pw, H), fill=block)
    mpal = (None, None, btxt, btxt, pal[4])
    mark(img, mpal)
    kicker(img, pal, spec['kicker'], 70, 420, color=GOLD)
    f, lines, s = fit_text(d, spec['label'], 'serif', pw - 140, 420, 92)
    draw_lines(d, (70, 480), lines, f, s, btxt)
    items = spec['companies'][:10]
    n = len(items)
    cols = 2 if n <= 6 else 3
    rows = math.ceil(n / cols)
    gx, gy = 30, 30
    area_w, area_h = W - pw - 140, H - 200
    tw = int((area_w - gx * (cols - 1)) / cols)
    th = min(150, int((area_h - gy * (rows - 1)) / rows))
    y0 = (H - (rows * th + (rows - 1) * gy)) / 2
    placed = []
    for i, it in enumerate(items):
        r, c = divmod(i, cols)
        cnt = cols if r < rows - 1 else n - cols * (rows - 1)
        x = pw + 70 + c * (tw + gx) + (cols - cnt) * (tw + gx) / 2
        paste_tile(img, it, x, y0 + r * (th + gy), tw, th, pal, placed)


def layout_tiers(img, spec, pal):
    """Tiers: lead firms large, others to watch smaller, headline top left."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    mark(img, pal)
    kicker(img, pal, spec['kicker'], 70, 170)
    f, lines, s = fit_text(d, spec['label'], 'serif', W - 140, 230, 96)
    draw_lines(d, (70, 220), lines, f, s, pal[2])
    items = spec['companies'][:10]
    lead = items[:spec.get('lead_count', min(5, len(items)))]
    rest = items[len(lead):]
    placed = []
    y = 540
    d.text((70, y - 52), 'LEAD FIRMS', font=font('sans-b', 22), fill=pal[3])
    gap = 26
    tw = int((W - 140 - gap * (len(lead) - 1)) / len(lead)); th = 170
    for i, it in enumerate(lead):
        paste_tile(img, it, 70 + i * (tw + gap), y, tw, th, pal, placed)
    if rest:
        y2 = y + th + 120
        d.line((70, y2 - 62, W - 70, y2 - 62), fill=GOLD, width=2)
        d.text((70, y2 - 50), 'OTHERS TO WATCH', font=font('sans-b', 22), fill=pal[3])
        tw2 = int((W - 140 - gap * (max(len(rest), 5) - 1)) / max(len(rest), 5)); th2 = 108
        for i, it in enumerate(rest):
            paste_tile(img, it, 70 + i * (tw2 + gap), y2 + 10, tw2, th2, pal, placed)


def layout_constellation(img, spec, pal):
    """Constellation: logos scattered at varied sizes on soft rings, headline lower left."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    rnd = random.Random(spec.get('seed', 7))
    cx, cy = int(W * 0.66), int(H * 0.44)
    ring = (255, 255, 255, 60) if pal[4] else (16, 36, 66, 30)
    ov = Image.new('RGBA', img.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    for r in (180, 330, 480, 630):
        od.ellipse((cx - r, cy - r, cx + r, cy + r), outline=ring, width=2)
    for _ in range(140):
        a = rnd.random() * 6.283; r = rnd.uniform(120, 640)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a) * 0.9
        od.ellipse((x - 2, y - 2, x + 2, y + 2), fill=ring)
    img.alpha_composite(ov)
    mark(img, pal)
    items = spec['companies'][:10]
    placed = [(40, 680, 840, 1180)]  # keep the headline area clear
    sizes = [(300, 132), (270, 120), (250, 112)] + [(220, 100)] * 7
    slots = []
    for k, r in enumerate((250, 450)):
        cnt = 4 if k == 0 else 6
        for j in range(cnt):
            a = -math.pi / 2 + j * 2 * math.pi / cnt + (0.35 if k else 0)
            slots.append((cx + r * math.cos(a), cy + r * 0.82 * math.sin(a)))
    for i, it in enumerate(items):
        w, h = sizes[i]
        for tries in range(600):
            if tries < 40:
                sx, sy = slots[i][0] + rnd.uniform(-80, 80), slots[i][1] + rnd.uniform(-60, 60)
            else:
                sx, sy = rnd.uniform(860 + w / 2, W - 50 - w / 2), rnd.uniform(150 + h / 2, H - 50 - h / 2)
            try:
                paste_tile(img, it, sx - w / 2, sy - h / 2, w, h, pal, placed, gap=26)
                break
            except ValueError:
                continue
        else:
            raise ValueError(f'No room for {it["name"]}')
    kicker(img, pal, spec['kicker'], 70, 720)
    f, lines, s = fit_text(d, spec['label'], 'serif', 760, 330, 96)
    draw_lines(d, (70, 780), lines, f, s, pal[2])


def layout_number(img, spec, pal):
    """Typographic: one big sourced number as the hero, logos small underneath."""
    W, H = img.size
    d = ImageDraw.Draw(img)
    mark(img, pal)
    kicker(img, pal, spec['kicker'], 70, 170)
    big = spec['big_number']
    f = font('serif-b', 330)
    while d.textlength(big['value'], font=f) > W - 140:
        f = font('serif-b', f.size - 10)
    d.text((62, 200), big['value'], font=f, fill=pal[2])
    y = 200 + f.size * 1.12
    f2, lines, s = fit_text(d, big['caption'], 'sans', W - 300, 120, 40, minsize=26)
    y = draw_lines(d, (70, y), lines, f2, s, pal[3], spacing=1.3)
    d.text((70, y + 6), big['source'], font=font('sans', 22), fill=pal[3])
    f3, l3, s3 = fit_text(d, spec['label'], 'serif', W - 140, 70, 52, minsize=30)
    items = spec['companies'][:10]
    gap = 22
    per = min(5, len(items)); rows = math.ceil(len(items) / per)
    tw = int((W - 140 - gap * (per - 1)) / per); th = 92
    yt = H - 70 - rows * th - (rows - 1) * gap
    draw_lines(d, (70, yt - 40 - s3 * 1.12), l3, f3, s3, pal[2])
    placed = []
    for i, it in enumerate(items):
        r, c = divmod(i, per)
        paste_tile(img, it, 70 + c * (tw + gap), yt + r * (th + gap), tw, th, pal, placed)


LAYOUTS = {'cover': layout_cover, 'split': layout_split, 'tiers': layout_tiers,
           'constellation': layout_constellation, 'number': layout_number}


def artwork(spec, out):
    pal = PALETTES[spec['palette']]
    img = fast_gradient(1800, 1200, pal, spec.get('angle', 20)).convert('RGBA')
    LAYOUTS[spec['layout']](img, spec, pal)
    img.convert('RGB').save(out, quality=90)


# ---------------- infographics v2: newsroom style (matplotlib) ----------------
# Rules taken from the Economist, FT and Reuters chart desks:
# - the title states the finding; the subtitle gives the measure and units
# - plain light background, horizontal gridlines only, no axis lines, values on the right
# - direct labels instead of legends; label key points, not every point
# - one highlight colour, everything else muted; bars start at zero and are sorted
# - short annotations with a thin leader line explain what matters
# - a coloured rule and tag at the top, source and credit at the bottom, one left margin

INK = '#14213d'; MUTED = '#5c6b80'; GRID = '#d5dde8'; HI = '#1d5a96'; SOFT = '#9fb6cf'; ACC = '#c4a052'
PAPER = {'pale_sky': '#f4f7fb', 'steel': '#eef1f5', 'ocean': '#eef5f8', 'ice': '#f8fbfe', 'navy_night': '#f4f7fb', 'twilight': '#f3f4fa'}
BAND = {'pale_sky': '#5b8db8', 'steel': '#4a5d78', 'ocean': '#2f7ca0', 'ice': '#7aa7d6', 'navy_night': '#14284f', 'twilight': '#3d4f8f'}
L = 0.06  # one left margin for everything


def _mpl():
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import font_manager as fm, pyplot as plt
    for f in os.listdir(FD):
        fm.fontManager.addfont(os.path.join(FD, f))
    plt.rcParams.update({'font.family': 'Open Sans', 'font.size': 16, 'axes.edgecolor': 'none',
                         'axes.unicode_minus': False})
    return plt


def fmt(v, p):
    d = p.get('decimals', 0 if float(v).is_integer() else 1)
    return f"{p.get('prefix', '')}{v:,.{d}f}{p.get('suffix', '')}"


def frame(fig, spec):
    import textwrap
    band = BAND[spec['palette']]
    fig.patches.append(__import__('matplotlib').patches.Rectangle((0, 0.985), 1, 0.015, transform=fig.transFigure, color=band))
    fig.patches.append(__import__('matplotlib').patches.Rectangle((L, 0.93), 0.012, 0.035, transform=fig.transFigure, color=ACC))
    fig.text(L + 0.02, 0.947, spec.get('tag', '').upper(), fontsize=14, fontweight=700, color=MUTED, va='center')
    tsize = min(36, 36 * 56 / max(56, len(spec['title'])))
    fig.text(L, 0.905, spec['title'], fontfamily='Noto Serif', fontsize=tsize, fontweight=700, color=INK, va='top')
    fig.text(L, 0.835, spec.get('subtitle', ''), fontsize=18, color=MUTED, va='top')
    fig.add_artist(__import__('matplotlib').lines.Line2D([L, 1 - L], [0.085, 0.085], transform=fig.transFigure, color=GRID, lw=1))
    src = textwrap.fill(spec['source'], 140)
    fig.text(L, 0.065, src, fontsize=12.5, color=MUTED, va='top', linespacing=1.4)
    fig.text(1 - L, 0.065, 'GFM REVIEW', fontsize=13, fontweight=700, color=INK, ha='right', va='top')


def axes(fig, box):
    ax = fig.add_axes(box)
    ax.set_facecolor('none')
    ax.tick_params(colors=MUTED, length=0, labelsize=15)
    ax.yaxis.tick_right()
    ax.grid(axis='y', color=GRID, lw=1)
    ax.set_axisbelow(True)
    return ax


def nice_max(v):
    m = 10 ** math.floor(math.log10(v)); 
    for k in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10):
        if k * m >= v:
            return k * m


def note(ax, xy, text, xytext, ha='left'):
    ax.annotate(text, xy=xy, xytext=xytext, textcoords='offset points', fontsize=14.5, color=INK, ha=ha, va='center',
                bbox=dict(boxstyle='round,pad=0.35', fc='white', ec='none', alpha=0.9),
                arrowprops=dict(arrowstyle='-', color=MUTED, lw=1, shrinkA=4, shrinkB=6), linespacing=1.35)


def chart_line(ax, p):
    import matplotlib.ticker as mt
    n = len(p['labels'])
    top = nice_max(max(max(s['values']) for s in p['series']) * 1.08)
    for i, s in enumerate(p['series']):
        col = HI if i == p.get('highlight', 0) else SOFT
        ax.plot(range(n), s['values'], color=col, lw=4 if col == HI else 2.5, solid_capstyle='round', zorder=3)
        ax.scatter([n - 1], [s['values'][-1]], color=col, s=70, zorder=4)
        if p.get('label_first', True) and n > 1:
            ax.text(0, s['values'][0] + (ax.get_ylim()[1] if False else 0), '', fontsize=1)
        ax.text(n - 1 + 0.08, s['values'][-1], f"{s.get('label', s['name'])}\n{fmt(s['values'][-1], p)}", color=col, fontsize=15, fontweight=700, va='center')
        if p.get('area') and col == HI:
            ax.fill_between(range(n), s['values'], color=HI, alpha=0.07)
    ax.set_xlim(-0.2, n - 1 + 0.9)
    ax.set_ylim(0, top)
    ax.yaxis.set_major_locator(mt.MaxNLocator(5))
    ax.yaxis.set_major_formatter(mt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_xticks(range(n)); ax.set_xticklabels(p['labels'])
    for a in p.get('notes', []):
        s = p['series'][a.get('series', 0)]
        note(ax, (a['x'], s['values'][a['x']]), a['text'], tuple(a.get('offset', (30, 60))), a.get('ha', 'left'))


def chart_hbar(ax, p, logos=False):
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    items = sorted(p['items'], key=lambda x: x['value'], reverse=True)
    n = len(items)
    mx = max(i['value'] for i in items)
    hi = p.get('highlight')
    for k, it in enumerate(items):
        y = n - 1 - k
        col = HI if (hi is None and k == 0) or it['name'] == hi else SOFT
        ax.barh(y, it['value'], color=col, height=0.5)
        ax.text(it['value'] + mx * 0.015, y, fmt(it['value'], p), va='center', fontsize=17, fontweight=700, color=INK)
        if logos and it.get('logo') and os.path.exists(it['logo']):
            ab = AnnotationBbox(OffsetImage(logo_image(it['logo'], 44), zoom=1), (-mx * 0.02, y), frameon=False, box_alignment=(1, 0.5), annotation_clip=False)
            ax.add_artist(ab)
        else:
            ax.text(-mx * 0.02, y, it['name'], ha='right', va='center', fontsize=16, fontweight=600, color=INK)
    ax.set_xlim(0, mx * 1.15); ax.set_ylim(-0.6, n - 0.4); ax.set_clip_on(False)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.axvline(0, color=INK, lw=1.2)


def chart_bars(ax, p):
    import matplotlib.ticker as mt
    labels = p['labels']; s = p['series'][0]['values']
    hi = p.get('highlight', max(range(len(s)), key=lambda i: s[i]))
    top = nice_max(max(s) * 1.15)
    for i, v in enumerate(s):
        ax.bar(i, v, 0.38, color=HI if i == hi else SOFT)
        ax.text(i, v + top * 0.02, fmt(v, p), ha='center', va='bottom', fontsize=18, fontweight=700, color=INK)
    ax.set_ylim(0, top); ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels, fontsize=16, color=INK)
    ax.yaxis.set_major_locator(mt.MaxNLocator(5))
    ax.axhline(0, color=INK, lw=1.2)
    for a in p.get('notes', []):
        note(ax, (a['x'], s[a['x']]), a['text'], tuple(a.get('offset', (80, 40))))


def chart_track(ax, p):
    """Score track (dot plot on a 0-to-max scale): better than two fat bars for a comparison of a few scores."""
    items = p['items']; mx = p.get('max', 10); n = len(items)
    hi = p.get('highlight', max(range(n), key=lambda i: items[i]['value']))
    for k, it in enumerate(items):
        y = n - 1 - k
        ax.plot([0, mx], [y, y], color=GRID, lw=14, solid_capstyle='round', zorder=1)
        col = HI if k == hi else SOFT
        ax.plot([0, it['value']], [y, y], color=col, lw=14, solid_capstyle='round', zorder=2)
        ax.scatter([it['value']], [y], s=520, color=col, edgecolor='white', lw=3, zorder=3)
        ax.text(it['value'], y + 0.26, fmt(it['value'], p), ha='center', fontsize=24, fontfamily='Noto Serif', fontweight=700, color=INK)
        ax.text(0, y - 0.3, it['name'], ha='left', va='top', fontsize=16, color=INK, fontweight=600)
    for t in range(0, int(mx) + 1, p.get('step', 2)):
        ax.text(t, -0.95, str(t), ha='center', fontsize=13, color=MUTED)
    if p.get('gap') and n == 2:
        a, b = items[0]['value'], items[1]['value']
        ax.annotate('', xy=(b, n - 1.5), xytext=(a, n - 1.5), arrowprops=dict(arrowstyle='<->', color=ACC, lw=2))
        ax.text((a + b) / 2, n - 1.5 + 0.08, p['gap'], ha='center', va='bottom', fontsize=16, fontweight=700, color=ACC)
    ax.set_xlim(-0.3, mx + 0.4); ax.set_ylim(-1.1, n - 0.4)
    ax.axis('off')


def logo_image(path, h):
    im = Image.open(path).convert('RGBA')
    im = im.crop(im.getbbox())
    r = h / im.height
    im = im.resize((int(im.width * r), h), Image.LANCZOS)
    bg = Image.new('RGBA', (im.width + 20, h + 14), (16, 36, 66, 255) if is_light(im) else (255, 255, 255, 0))
    bg.alpha_composite(im, (10, 7))
    return bg


def stats_row(fig, box, stats):
    import textwrap
    x0, y0, w, h = box
    n = len(stats); cw = w / n
    for i, st in enumerate(stats):
        x = x0 + i * cw
        if i:
            fig.add_artist(__import__('matplotlib').lines.Line2D([x - 0.015, x - 0.015], [y0, y0 + h], transform=fig.transFigure, color=GRID, lw=1.2))
        fig.text(x, y0 + h, st['value'], fontfamily='Noto Serif', fontsize=st.get('size', 52), fontweight=700, color=HI if i == 0 else INK, va='top')
        fig.text(x, y0 + h - 0.105, textwrap.fill(st['label'], int(cw * 1600 / 10.5)), fontsize=16, color=MUTED, va='top', linespacing=1.4)


def timeline(fig, box, events):
    import textwrap, matplotlib.patches as mp, matplotlib.lines as ml
    x0, y0, w, h = box
    ym = y0 + h * 0.55
    fig.add_artist(ml.Line2D([x0, x0 + w], [ym, ym], transform=fig.transFigure, color=SOFT, lw=2))
    for i, e in enumerate(events):
        x = x0 + w * i / (len(events) - 1) if len(events) > 1 else x0
        ha = 'left' if i == 0 else 'right' if i == len(events) - 1 else 'center'
        fig.add_artist(mp.Circle((x, ym), 0.006, transform=fig.transFigure, color=ACC if e.get('key') else HI, zorder=5))
        fig.text(x, ym + 0.028, e['date'], ha=ha, fontsize=15, fontweight=700, color=INK)
        fig.text(x, ym - 0.03, textwrap.fill(e['text'], 26), ha=ha, va='top', fontsize=13.5, color=MUTED, linespacing=1.35)


def section_label(fig, x, y, text):
    fig.text(x, y, text.upper(), fontsize=13, fontweight=700, color=MUTED)


def infographic(spec, out):
    plt = _mpl()
    fig = plt.figure(figsize=(16, 10), dpi=100, facecolor=PAPER[spec['palette']])
    frame(fig, spec)
    t = spec['type']
    if t == 'line':
        chart_line(axes(fig, [L, 0.16, 0.8, 0.6]), spec['panel'])
    elif t in ('ranked', 'hbar'):
        ax = fig.add_axes([L + 0.2, 0.16, 0.68, 0.6]); ax.set_facecolor('none')
        chart_hbar(ax, spec['panel'], logos=t == 'ranked')
    elif t == 'track':
        ax = fig.add_axes([L, 0.17, 1 - 2 * L, 0.58]); ax.set_facecolor('none')
        chart_track(ax, spec['panel'])
    elif t == 'bars':
        chart_bars(axes(fig, [L, 0.16, 0.86, 0.6]), spec['panel'])
    elif t == 'stats':
        stats_row(fig, (L, 0.42, 1 - 2 * L, 0.32), spec['panel']['stats'])
        if spec['panel'].get('timeline'):
            section_label(fig, L, 0.33, 'Timetable')
            timeline(fig, (L + 0.02, 0.13, 1 - 2 * L - 0.04, 0.16), spec['panel']['timeline'])
    elif t == 'combo':
        section_label(fig, L, 0.765, spec['main'].get('heading', ''))
        chart_line(axes(fig, [L, 0.39, 0.54, 0.35]), spec['main'])
        x2 = 0.68
        section_label(fig, x2, 0.765, spec['stats'].get('heading', 'Key figures'))
        for i, st in enumerate(spec['stats']['stats']):
            stats_row(fig, (x2, 0.585 - i * 0.2, 1 - L - x2, 0.155), [dict(st, size=44)])
        section_label(fig, L, 0.3, spec['timeline'].get('heading', 'Timeline'))
        timeline(fig, (L + 0.02, 0.11, 1 - 2 * L - 0.04, 0.16), spec['timeline']['events'])
    fig.savefig(out + '.png', dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)
    Image.open(out + '.png').convert('RGB').save(out, quality=92)
    os.remove(out + '.png')


if __name__ == '__main__':
    mode, spec_path, out = sys.argv[1:4]
    spec = json.load(open(spec_path))
    (artwork if mode == 'artwork' else infographic)(spec, out)
    print('ok', out)
