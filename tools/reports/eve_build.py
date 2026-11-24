import urllib.parse, json, sys, html

E = lambda x: html.escape(str(x), quote=False)
A = lambda x: html.escape(str(x), quote=True)

NAVY = "#0B3D6E"
RED = "#A32D2D"
INK = "#2C2C2A"
SOFT = "#5F5E5A"
FAINT = "#888780"
LINE = "#E4E3DC"
FONT = "'Open Sans',Arial,Helvetica,sans-serif"

# Priority marker (Brett, 23 November 2026). 1 = act now, 2 = today, 3 = can wait.
PRIORITY = {
    1: (RED, "#ffffff", "P1 Act now"),
    2: (NAVY, "#ffffff", "P2 Today"),
    3: ("#E4E3DC", "#5F5E5A", "P3 Can wait"),
}


def ppill(p):
    bg, fg, label = PRIORITY.get(p, PRIORITY[3])
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:10px;font-weight:700;letter-spacing:.4px;'
            f'text-transform:uppercase;padding:2px 8px;border-radius:9px;white-space:nowrap">{E(label)}</span>')


def button(label, url, primary):
    if primary:
        style = f"background:{NAVY};color:#ffffff;border:1px solid {NAVY}"
    else:
        style = f"background:#ffffff;color:{NAVY};border:1px solid #B5D4F4"
    return (f'<a href="{A(url)}" style="{style};display:inline-block;font-family:{FONT};font-size:13px;font-weight:600;'
            f'line-height:16px;text-decoration:none;padding:8px 13px;border-radius:6px;margin:8px 6px 0 0">{E(label)}</a>')


def tile(n, label, colour):
    c = "#B4B3A8" if n in (0, "0") else colour
    return (f'<td width="25%" style="padding:4px" valign="top"><table width="100%" cellpadding="0" cellspacing="0" role="presentation" '
            f'style="background:#ffffff;border:1px solid {LINE};border-radius:8px"><tr><td style="padding:10px 6px;text-align:center;font-family:{FONT}">'
            f'<div style="font-size:24px;font-weight:700;color:{c};line-height:1.1">{E(n)}</div>'
            f'<div style="font-size:11px;color:{SOFT};margin-top:3px">{E(label)}</div></td></tr></table></td>')


def heading(text, note=None):
    n = f'<div style="font-size:12px;color:{FAINT};line-height:1.5;margin:-4px 0 8px 0">{E(note)}</div>' if note else ""
    return (f'<div style="font-size:12px;font-weight:700;color:{SOFT};letter-spacing:.8px;text-transform:uppercase;'
            f'margin-bottom:8px">{E(text)}</div>{n}')


def block(inner, pad="20px 24px 0 24px"):
    return f'<tr><td style="padding:{pad};font-family:{FONT}">{inner}</td></tr>'


def panel(inner, pad="12px 14px"):
    return (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;border:1px solid {LINE};'
            f'border-radius:6px"><tr><td style="padding:{pad};font-family:{FONT}">{inner}</td></tr></table>')


def pct(n, d):
    return "-" if not d else f"{100.0 * n / d:.1f}%"


def stats_table(title, rows):
    """rows: [{name, sent, bounced, failed, replies, positive}] ; last row is the total."""
    th = (f'style="font-family:{FONT};font-size:11px;font-weight:700;color:{SOFT};text-align:right;padding:7px 6px;'
          f'border-bottom:1px solid {LINE};white-space:nowrap"')
    head = (f'<tr><td style="font-family:{FONT};font-size:11px;font-weight:700;color:{SOFT};padding:7px 6px 7px 12px;'
            f'border-bottom:1px solid {LINE}">{E(title)}</td>'
            f'<td {th}>Sent</td><td {th}>Bounce rate</td><td {th}>Failed</td><td {th}>Replies</td><td {th}>Reply rate</td>'
            f'<td {th}>Interested</td></tr>')
    body = ""
    for i, r in enumerate(rows):
        total = (i == len(rows) - 1)
        alert = (r.get("name") == "Unregistered" and int(r["sent"]) > 0)
        w = "700" if total or alert else "400"
        bg = "#F4F8FC" if total else ("#FCEBEB" if alert else "#ffffff")
        delivered = max(int(r["sent"]) - int(r["bounced"]) - int(r["failed"]), 0)
        td = (f'style="font-family:{FONT};font-size:13px;font-weight:{w};color:{INK};text-align:right;padding:7px 6px;'
              f'background:{bg};border-bottom:1px solid {LINE};white-space:nowrap"')
        body += (f'<tr><td style="font-family:{FONT};font-size:13px;font-weight:{w};color:{INK};padding:7px 6px 7px 12px;'
                 f'background:{bg};border-bottom:1px solid {LINE}">{E(r["name"])}</td>'
                 f'<td {td}>{E(r["sent"])}</td>'
                 f'<td {td}>{E(pct(int(r["bounced"]), int(r["sent"])))} <span style="color:{FAINT};font-weight:400">({E(r["bounced"])})</span></td>'
                 f'<td {td}>{E(r["failed"])}</td>'
                 f'<td {td}>{E(r["replies"])}</td>'
                 f'<td {td}>{E(pct(int(r["replies"]), delivered))}</td>'
                 f'<td {td}>{E(r.get("positive", 0))}</td></tr>')
    return (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;border:1px solid {LINE};'
            f'border-radius:6px;margin:0 0 10px 0;border-collapse:separate">{head}{body}</table>')


STAGE = {
    "won": ("#EAF3DE", "#27500A"),
    "warm": ("#FAEEDA", "#854F0B"),
    "open": ("#E6F1FB", "#0C447C"),
    "cold": ("#F1EFE8", "#5F5E5A"),
    "lost": ("#FCEBEB", "#A32D2D"),
}


def wep_table(items):
    th = f'style="font-family:{FONT};font-size:11px;font-weight:700;color:{SOFT};text-align:left;padding:7px 8px;border-bottom:1px solid {LINE}"'
    head = f'<tr><td {th}>Winner</td><td {th}>Stage</td><td {th}>Last contact</td><td {th}>Next step</td></tr>'
    body = ""
    for w in items:
        bg, fg = STAGE.get(w.get("tone", "open"), STAGE["open"])
        link = (f'<br><a href="{A(w["url"])}" style="font-size:12px;color:{NAVY};font-weight:600;text-decoration:none">Open email</a>'
                if w.get("url") else "")
        td = f'style="font-family:{FONT};font-size:13px;color:{INK};padding:8px;border-bottom:1px solid {LINE};vertical-align:top;line-height:1.4"'
        body += (f'<tr><td {td}><b>{E(w["firm"])}</b><br><span style="font-size:12px;color:{SOFT}">{E(w.get("award", ""))}</span></td>'
                 f'<td {td}><span style="display:inline-block;background:{bg};color:{fg};font-size:11px;font-weight:700;padding:2px 8px;'
                 f'border-radius:9px;white-space:nowrap">{E(w["stage"])}</span></td>'
                 f'<td {td}><span style="white-space:nowrap">{E(w.get("last", ""))}</span></td>'
                 f'<td {td}>{E(w.get("next", ""))}{link}</td></tr>')
    return (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;border:1px solid {LINE};'
            f'border-radius:6px;border-collapse:separate">{head}{body}</table>')


def flagged(items):
    """items: [{p, text}] sorted P1 first; each line starts with its priority marker."""
    out = ""
    for x in sorted(items, key=lambda x: x.get("p", 3)):
        out += (f'<tr><td valign="top" style="padding:6px 8px 6px 0;white-space:nowrap">{ppill(x.get("p", 3))}</td>'
                f'<td valign="top" style="padding:6px 0;font-family:{FONT};font-size:13px;color:{INK};line-height:1.5">{E(x["text"])}</td></tr>')
    return f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation">{out}</table>'


def build(d):
    rows = []
    rows.append(f'<tr><td style="background:{NAVY};padding:20px 24px;font-family:{FONT}">'
                f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
                f'<td valign="top"><div style="font-size:11px;color:#B5D4F4;letter-spacing:1.2px">GFM REVIEW OFFICE</div>'
                f'<div style="font-size:21px;font-weight:700;color:#ffffff;margin-top:3px">Evening report</div>'
                f'<div style="font-size:13px;color:#E6F1FB;margin-top:2px">{E(d["date"])}</div></td>'
                f'<td valign="top" align="right" style="font-size:12px;color:#B5D4F4;white-space:nowrap">Results and tomorrow</td>'
                f'</tr></table></td></tr>')
    rows.append(block(f'<div style="font-size:14px;color:{INK};line-height:1.6">Good evening Brett,<br><br>{E(d["headline"])}</div>',
                      "18px 24px 4px 24px"))
    t = d["tiles"]
    rows.append('<tr><td style="padding:10px 20px 2px 20px"><table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
                + tile(t["sent"], "Emails sent today", NAVY) + tile(t["replies"], "Replies today", "#854F0B")
                + tile(t["interested"], "Interested", "#3B6D11") + tile(t["waiting"], "Waiting on you", RED)
                + '</tr></table></td></tr>')

    # 1. needs you: carried items, approved emails not sent, failed agents, each with a priority marker
    if d.get("carried"):
        rows.append(block(heading("1. Still needs you", "The most important open items, P1 first. All of them appear in full, with buttons, in the morning briefing.")
                          + panel(flagged(d["carried"]), "8px 14px")))

    # 2. done today
    if d.get("done"):
        done = "".join(f'<div style="font-size:13px;color:{INK};line-height:1.55;margin:0 0 6px 0">'
                       f'<span style="color:#3B6D11;font-weight:700">&#10003;</span>&nbsp; {E(x)}</div>' for x in d["done"])
        rows.append(block(heading("2. Done today") + panel(done, "12px 14px 6px 14px")))

    # 3. campaign success, one row per campaign in the register
    c = d["campaigns"]
    inner = heading("3. Campaign results", c.get("note"))
    for tbl in c["tables"]:
        inner += stats_table(tbl["title"], tbl["rows"])
    if c.get("by_domain"):
        inner += stats_table("By sending domain (to date)", c["by_domain"])
    elif c.get("domain_note"):
        inner += f'<div style="font-size:12px;color:{FAINT};line-height:1.5;margin:0 0 6px 0">{E(c["domain_note"])}</div>'
    if c.get("insight"):
        inner += (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#E6F1FB;border-radius:6px">'
                  f'<tr><td style="padding:10px 14px;font-family:{FONT};font-size:13px;color:#0C447C;line-height:1.5">'
                  f'<b>What the numbers say:</b> {E(c["insight"])}</td></tr></table>')
    rows.append(block(inner))

    # 4. WEPs in the wild
    w = d["weps"]
    inner = heading("4. Award winners and the WEP", w.get("note"))
    s = w["summary"]
    inner += ('<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 10px 0"><tr>'
              + tile(s["winners"], "Winners announced", NAVY) + tile(s["meetings"], "Meetings booked or held", "#0C447C")
              + tile(s["presented"], "WEPs presented", "#854F0B") + tile(s["won"], "Taken up", "#3B6D11")
              + '</tr></table>')
    if w.get("items"):
        inner += wep_table(w["items"])
    if w.get("tidy"):
        inner += f'<div style="font-size:12px;color:{FAINT};line-height:1.5;margin-top:6px">{E(w["tidy"])}</div>'
    rows.append(block(inner))

    # 5. tomorrow
    if d.get("tomorrow"):
        rows.append(block(heading("5. Tomorrow") + f'<div style="font-size:13px;color:{INK};line-height:1.6">{E(d["tomorrow"])}</div>'))

    links = "".join(button(l["label"], l["url"], i == 0) for i, l in enumerate(d["links"]))
    rows.append(f'<tr><td style="padding:22px 24px 4px 24px;border-top:1px solid {LINE};font-family:{FONT}">'
                f'<div style="font-size:12px;font-weight:700;color:{SOFT};margin-top:14px">Quick links</div>{links}</td></tr>')
    rows.append(f'<tr><td style="padding:18px 24px 22px 24px;font-family:{FONT};font-size:14px;color:{INK};line-height:1.6">'
                f'Kind regards,<br><br>Alix<div style="font-size:11px;color:{FAINT};margin-top:12px">{E(d["next"])}</div></td></tr>')
    return (f'<div style="background:#F1EFE8;padding:20px 0;font-family:{FONT}">'
            f'<table align="center" width="640" cellpadding="0" cellspacing="0" role="presentation" style="width:100%;max-width:640px;'
            f'background:#F9F9F7;border:1px solid {LINE};font-family:{FONT}">{"".join(rows)}</table></div>')


if __name__ == "__main__":
    d = json.load(open(sys.argv[1]))
    out = build(d)
    for bad in (chr(8212), chr(8211)):
        if bad in out:
            sys.exit("em or en dash found: remove it from data.json")
    open(sys.argv[2], "w").write(out)
    print("ok", len(out), "bytes")
