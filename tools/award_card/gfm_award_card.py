"""GFM Review award-winner card template.

Renders the weekly winners card (1080 x 1350) signed off on 24 Nov 2026:
dark blue bands top and bottom, white middle, the recognition line, two or
three winners with their logos, and an invitation to nominate.

    python3 -I gfm_award_card.py series.json out_dir [assets_dir]

series.json holds {"cards": [{"id", "month", "winners": [{"name", "awards": [...], "logo"}]}]}.
Logos are looked up in assets_dir/logos; the white GFM logo is assets_dir/gfm-logo-white.png.
"""
import json, os, sys, html
from playwright.sync_api import sync_playwright

BAND, ACC, INK, GREY, RULE, TINT = "#14304F", "#1F5F99", "#1C2633", "#4A5563", "#DCE1E8", "#EEF4FA"
RECOGNITION = ("Recognising companies and institutions that have achieved notable success in their fields, "
               "judged on criteria including transparency, governance, innovation and customer service.")


def rosette(size, color, sw=1.7):
    return (f'<svg aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" style="flex: none"><circle cx="12" cy="9" r="6"></circle>'
            f'<circle cx="12" cy="9" r="2.6"></circle><path d="M8.6 13.8 7 22l5-2.8 5 2.8-1.6-8.2"></path></svg>')


def logo_box(src, name):
    if src:
        inner = f'<img src="{src}" alt="{html.escape(name)} logo" style="max-width: 100%; max-height: 100%; width: auto; height: auto; display: block">'
        border = f"border: 1px solid {RULE};"
    else:
        inner = f'<span style="font-size: 18px; font-weight: 600; color: {GREY}">[{html.escape(name.split()[0])} logo]</span>'
        border = "border: 2px dashed #AEB8C6;"
    return (f'<div style="flex: none; width: 210px; height: 100px; {border} border-radius: 14px; display: flex; align-items: center; '
            f'justify-content: center; padding: 12px 20px; box-sizing: border-box; text-align: center">{inner}</div>')


def card_html(card, assets, tight=0):
    winners = card["winners"]
    compact = len(winners) >= 3
    pad_row = ["30px", "24px", "18px", "14px"][min(3, (1 if compact else 0) + tight)]
    rec_size = [31, 31, 28, 27][min(3, (1 if compact else 0) + tight)]
    rows = []
    for i, w in enumerate(winners):
        aw = "".join(f'<div style="display: flex; align-items: center; gap: 14px; font-size: 23px; font-weight: 500; line-height: 1.35; color: {ACC}">'
                     f'{rosette(28, ACC)}<span>{html.escape(a)}</span></div>' for a in w["awards"])
        border = "" if i == len(winners) - 1 else f"border-bottom: 1px solid {RULE};"
        logo = f"file://{assets}/logos/{w['logo']}" if w.get("logo") else None
        rows.append(f'''<div style="padding: {pad_row} 0; {border} display: flex; align-items: center; gap: 28px">
<div style="flex: 1; display: flex; flex-direction: column; gap: 14px">
<div style="font-size: 34px; font-weight: 600; line-height: 1.2; color: {INK}">{html.escape(w["name"])}</div>
{aw}
</div>
{logo_box(logo, w["name"])}
</div>''')
    arrow = ('<svg aria-hidden="true" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
             'stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14"></path><path d="M13 6l6 6-6 6"></path></svg>')
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>body{{margin:0}}</style></head><body>
<div style="width: 1080px; height: 1350px; box-sizing: border-box; background: #FFFFFF; color: {INK}; font-family: 'Open Sans', sans-serif; display: flex; flex-direction: column; overflow: hidden">
<div style="flex: none; background: {BAND}; padding: 52px 96px; display: flex; align-items: center; justify-content: space-between; gap: 24px">
<img src="file://{assets}/gfm-logo-white.png" alt="Global Financial Market Review" style="height: 92px; width: auto; display: block">
<div style="display: flex; flex-direction: column; align-items: flex-end; gap: 4px">
<div style="font-size: 20px; font-weight: 600; letter-spacing: 0.14em; text-transform: uppercase; color: #C9D6E6">GFM Review Awards</div>
<div style="font-size: 34px; font-weight: 600; color: #FFFFFF">2026</div>
</div>
</div>
<div style="flex: 1; display: flex; flex-direction: column; padding: {"56px" if compact else "64px"} 96px 56px">
<p style="margin: 0; font-size: {rec_size}px; font-weight: 500; line-height: 1.45; color: {INK}">{RECOGNITION}</p>
<div style="margin-top: {"32px" if compact else "40px"}; border-top: 2px solid {INK}; display: flex; flex-direction: column">
{"".join(rows)}
</div>
<div style="margin-top: auto; padding: 32px 36px; background: {TINT}; border-radius: 16px; display: flex; flex-direction: column; gap: 14px">
<div style="font-size: 30px; font-weight: 600; line-height: 1.25; color: {INK}">Nominate your organisation</div>
<div style="font-size: 23px; line-height: 1.5; color: {INK}">Nominations for the GFM Review Awards are open, and entry is free.</div>
<div style="margin-top: 6px; display: flex; align-items: center; gap: 12px; font-size: 26px; font-weight: 600; color: {ACC}">gfmreview.com/nominations {arrow}</div>
</div>
</div>
<div style="flex: none; background: {BAND}; padding: 40px 96px; display: flex; align-items: center; justify-content: space-between; gap: 24px">
<div style="font-size: 22px; line-height: 1.4; color: #C9D6E6">{html.escape(card["month"])}</div>
<div style="font-size: 22px; font-weight: 600; color: #FFFFFF">gfmreview.com/awards</div>
</div>
</div></body></html>'''


def main():
    spec, out = sys.argv[1], sys.argv[2]
    assets = os.path.abspath(sys.argv[3] if len(sys.argv) > 3 else os.path.dirname(os.path.abspath(spec)))
    os.makedirs(out, exist_ok=True)
    cards = json.load(open(spec))["cards"]
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.environ.get("CHROME", "/usr/bin/google-chrome"), args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for c in cards:
            tmp = os.path.join(out, f"_card{c['id']}.html")
            for tight in range(3):
                open(tmp, "w").write(card_html(c, assets, tight))
                pg.goto("file://" + os.path.abspath(tmp)); pg.wait_for_timeout(500)
                # the bottom band must sit fully inside the 1350px card; tighten spacing until it does
                over = pg.evaluate("""() => document.body.firstElementChild.lastElementChild.getBoundingClientRect().bottom > 1350.5""")
                if not over:
                    break
            path = os.path.join(out, f"gfm-award-winners_{c['id']}.png")
            pg.screenshot(path=path, clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            os.remove(tmp)
            print(path, "OVERFLOW" if over else "ok")
        b.close()


if __name__ == "__main__":
    main()
