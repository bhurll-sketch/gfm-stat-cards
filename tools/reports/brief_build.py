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
DESK_MAIL = "alix.middleton@gfmreview.com"

PILLS = {
    "overdue": ("#FCEBEB", "#A32D2D", "Overdue"),
    "revenue": ("#FAEEDA", "#854F0B", "Revenue"),
    "today": ("#E6F1FB", "#0C447C", "Today"),
    "waiting": ("#F1EFE8", "#5F5E5A", "Waiting"),
    "approve": ("#EAF3DE", "#27500A", "Approve"),
    "check": ("#FCEBEB", "#A32D2D", "Check"),
    "draft": ("#E6F1FB", "#0C447C", "Draft"),
    "article": ("#EEEDFE", "#3C3489", "Article"),
}

# Priority marker (Brett, 23 November 2026). 1 = act now, 2 = today, 3 = can wait.
KIND_PRIORITY = {"overdue": 1, "revenue": 1, "approve": 2, "today": 2, "draft": 2, "article": 2, "check": 2, "waiting": 3}
PRIORITY = {
    1: (RED, "#ffffff", "P1 Act now"),
    2: (NAVY, "#ffffff", "P2 Today"),
    3: ("#E4E3DC", "#5F5E5A", "P3 Can wait"),
}


def priority(it, default=3):
    p = it.get("priority")
    if p in (1, 2, 3):
        return p
    if it.get("kind"):
        return KIND_PRIORITY.get(it["kind"], 3)
    return default


def ppill(p):
    bg, fg, label = PRIORITY[p]
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:10px;font-weight:700;letter-spacing:.4px;'
            f'text-transform:uppercase;padding:2px 8px;border-radius:9px;white-space:nowrap">{E(label)}</span>')


def mailto(subject, body):
    if not subject.startswith("Intelligence Desk"):
        subject = "Intelligence Desk: " + subject
    return ("mailto:" + DESK_MAIL + "?subject=" + urllib.parse.quote(subject)
            + "&body=" + urllib.parse.quote(body))


def target(a):
    if a.get("seed"):
        return "https://claude.ai/new?q=" + urllib.parse.quote(a["seed"])
    if a.get("mail"):
        return mailto(a["mail"]["subject"], a["mail"]["body"])
    return a["url"]


def button(label, url, primary):
    if primary:
        style = f"background:{NAVY};color:#ffffff;border:1px solid {NAVY}"
    else:
        style = f"background:#ffffff;color:{NAVY};border:1px solid #B5D4F4"
    return (f'<a href="{A(url)}" style="{style};display:inline-block;font-family:{FONT};font-size:13px;font-weight:600;'
            f'line-height:16px;text-decoration:none;padding:8px 13px;border-radius:6px;margin:8px 6px 0 0">{E(label)}</a>')


def buttons(acts):
    return "".join(button(a["label"], target(a), i == 0) for i, a in enumerate(acts[:4]))


def textlinks(acts):
    out = []
    for a in acts[:4]:
        out.append(f'<a href="{A(target(a))}" style="color:{NAVY};font-weight:600;text-decoration:none">{E(a["label"])}</a>')
    return '<span style="color:#B4B3A8">&nbsp;&middot;&nbsp;</span>'.join(out)


def tile(n, label, colour):
    c = "#B4B3A8" if n in (0, "0") else colour
    return (f'<td width="25%" style="padding:4px" valign="top"><table width="100%" cellpadding="0" cellspacing="0" role="presentation" '
            f'style="background:#ffffff;border:1px solid {LINE};border-radius:8px"><tr><td style="padding:10px 6px;text-align:center;font-family:{FONT}">'
            f'<div style="font-size:24px;font-weight:700;color:{c};line-height:1.1">{E(n)}</div>'
            f'<div style="font-size:11px;color:{SOFT};margin-top:3px">{E(label)}</div></td></tr></table></td>')


def pill(kind):
    bg, fg, label = PILLS.get(kind, PILLS["waiting"])
    return (f'<span style="display:inline-block;background:{bg};color:{fg};font-size:10px;font-weight:700;letter-spacing:.4px;'
            f'text-transform:uppercase;padding:2px 7px;border-radius:9px">{E(label)}</span>')


def card(it, accent):
    p = priority(it)
    edge = RED if p == 1 else accent
    meta = " &middot; ".join(E(x) for x in [it.get("mailbox"), it.get("waited")] if x)
    warn = (f'<div style="font-size:12px;color:#A32D2D;line-height:1.5;margin-top:4px">&#9888;&nbsp;{E(it["warn"])}</div>'
            if it.get("warn") else "")
    return (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 10px 0;background:#ffffff;'
            f'border:1px solid {LINE};border-left:4px solid {edge};border-radius:6px"><tr><td style="padding:12px 14px;font-family:{FONT}">'
            f'<div>{ppill(p)}&nbsp;{pill(it.get("kind", "waiting"))}<span style="font-size:12px;color:{FAINT}">&nbsp;&nbsp;{meta}</span></div>'
            f'<div style="font-size:15px;font-weight:700;color:{INK};line-height:1.35;margin-top:6px">{E(it["title"])}</div>'
            f'<div style="font-size:13px;color:{SOFT};line-height:1.5;margin-top:3px">{E(it["detail"])}</div>'
            f'{warn}<div>{buttons(it.get("actions", []))}</div></td></tr></table>')


def group(g, accent):
    """A batch of similar items: one main button, then one row each with small links."""
    gp = priority(g, 2)
    edge = RED if gp == 1 else accent
    rows = ""
    for r in g["rows"]:
        line2 = " &middot; ".join(E(x) for x in [r.get("to"), r.get("subject")] if x)
        warn = f'<div style="font-size:12px;color:#A32D2D">&#9888;&nbsp;{E(r["warn"])}</div>' if r.get("warn") else ""
        rp = ppill(1) + "&nbsp; " if r.get("priority") == 1 and gp != 1 else ""
        rows += (f'<tr><td style="padding:9px 14px;border-top:1px solid {LINE};font-family:{FONT}">'
                 f'<div style="font-size:14px;color:{INK};line-height:1.4">{rp}<b>{E(r["ref"])}</b>&nbsp; {E(r["firm"])}</div>'
                 f'<div style="font-size:12px;color:{SOFT};line-height:1.45;margin-top:1px">{line2}</div>{warn}'
                 f'<div style="font-size:12px;margin-top:4px">{textlinks(r.get("actions", []))}</div></td></tr>')
    more = (f'<tr><td style="padding:8px 14px;border-top:1px solid {LINE};font-family:{FONT};font-size:12px;color:{FAINT}">'
            f'{E(g["more"])}</td></tr>') if g.get("more") else ""
    return (f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 12px 0;background:#ffffff;'
            f'border:1px solid {LINE};border-left:4px solid {edge};border-radius:6px">'
            f'<tr><td style="padding:12px 14px 10px 14px;font-family:{FONT}">'
            f'<div>{ppill(gp)}</div>'
            f'<div style="font-size:15px;font-weight:700;color:{INK};margin-top:6px">{E(g["title"])} '
            f'<span style="color:{FAINT};font-weight:600">({E(g["count"])})</span></div>'
            f'<div style="font-size:13px;color:{SOFT};line-height:1.5;margin-top:3px">{E(g["detail"])}</div>'
            f'<div>{buttons(g.get("actions", []))}</div></td></tr>{rows}{more}</table>')


def heading(text, count=None, note=None):
    c = f' <span style="color:{FAINT};font-weight:600">({count})</span>' if count is not None else ""
    n = f'<div style="font-size:12px;color:{FAINT};line-height:1.5;margin:-4px 0 8px 0">{E(note)}</div>' if note else ""
    return (f'<div style="font-size:12px;font-weight:700;color:{SOFT};letter-spacing:.8px;text-transform:uppercase;'
            f'margin-bottom:8px">{E(text)}{c}</div>{n}')


def block(inner, pad="20px 24px 0 24px"):
    return f'<tr><td style="padding:{pad};font-family:{FONT}">{inner}</td></tr>'


# sections in priority order (Brett, 23 November 2026: replies come before new outreach): key, heading, accent, note
SECTIONS = [
    ("replies", "Replies you owe", "#BA7517",
     "People who have written to GFM Review and are waiting for an answer. These come before any new outreach."),
    ("emails", "Emails to approve", "#3B6D11",
     "Cold and article-led emails can be approved as a batch. Follow-ups are approved one by one."),
    ("unsent", "Approved but not yet sent", RED,
     "Emails you have approved that have not left yet, and why. Nothing approved should wait more than one working day."),
    ("articles", "Articles", "#534AB7", None),
    ("prospects", "New prospects to decide", NAVY,
     "Approve sends them into research and outreach. Hold keeps them for later. End drops them."),
    ("tasks", "Tasks and decisions", "#5F5E5A", None),
    ("fix", "Check Margaret's sent emails", "#E24B4A", None),
    ("system", "Agents that failed or missed a run", RED,
     "Scheduled work that did not run as planned since the last report."),
]


def count_p1(d):
    n = 0
    for key, *_ in SECTIONS:
        sec = d["sections"].get(key) or {}
        for c in sec.get("cards", []):
            n += 1 if priority(c) == 1 else 0
        for g in sec.get("groups", []):
            if priority(g, 2) == 1:
                n += int(g["count"])
            else:
                n += sum(1 for r in g["rows"] if r.get("priority") == 1)
    return n


def build(d):
    rows = []
    rows.append(f'<tr><td style="background:{NAVY};padding:20px 24px;font-family:{FONT}">'
                f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
                f'<td valign="top"><div style="font-size:11px;color:#B5D4F4;letter-spacing:1.2px">GFM REVIEW OFFICE</div>'
                f'<div style="font-size:21px;font-weight:700;color:#ffffff;margin-top:3px">Morning briefing</div>'
                f'<div style="font-size:13px;color:#E6F1FB;margin-top:2px">{E(d["date"])}</div></td>'
                f'<td valign="top" align="right" style="font-size:12px;color:#B5D4F4;white-space:nowrap">Everything that needs you</td>'
                f'</tr></table></td></tr>')
    rows.append(block(f'<div style="font-size:14px;color:{INK};line-height:1.6">{E(d.get("greeting", "Good morning Brett,"))}<br><br>{E(d["headline"])}</div>',
                      "18px 24px 4px 24px"))
    t = d["tiles"]
    rows.append('<tr><td style="padding:10px 20px 2px 20px"><table width="100%" cellpadding="0" cellspacing="0" role="presentation"><tr>'
                + tile(t["waiting"], "Waiting on you", NAVY) + tile(count_p1(d), "P1: act now", RED)
                + tile(t["emails"], "Emails to approve", "#3B6D11") + tile(t["revenue"], "Revenue items", "#854F0B")
                + '</tr></table></td></tr>')
    rows.append(block(f'<div style="font-size:12px;color:{SOFT};line-height:2">{ppill(1)}&nbsp; a reply from a prospect or winner, or anything overdue'
                      f'&nbsp;&nbsp; {ppill(2)}&nbsp; approvals and drafts for today&nbsp;&nbsp; {ppill(3)}&nbsp; no deadline</div>',
                      "8px 24px 0 24px"))
    if d.get("top3"):
        lines = "".join(f'<div style="margin:3px 0"><b>{i + 1}.</b>&nbsp; {E(x)}</div>' for i, x in enumerate(d["top3"]))
        rows.append(f'<tr><td style="padding:12px 24px 0 24px"><table width="100%" cellpadding="0" cellspacing="0" role="presentation" '
                    f'style="background:#FAEEDA;border-radius:6px"><tr><td style="padding:11px 14px;font-family:{FONT};font-size:13px;color:#633806;line-height:1.5">'
                    f'<div style="font-weight:700;margin-bottom:4px">Do these first</div>{lines}</td></tr></table></td></tr>')
    if d.get("meetings"):
        m = "".join(f'<div style="font-size:13px;color:{INK};line-height:1.55;margin:0 0 6px 0"><b>{E(x["time"])}</b>&nbsp; {E(x["who"])}'
                    + (f'<span style="color:{SOFT}"> &middot; {E(x["note"])}</span>' if x.get("note") else "") + '</div>' for x in d["meetings"])
        rows.append(block(heading("Today's meetings") +
                          f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#ffffff;border:1px solid {LINE};border-radius:6px">'
                          f'<tr><td style="padding:12px 14px 6px 14px;font-family:{FONT}">{m}</td></tr></table>'))
    num = 0
    for key, title, accent, note in SECTIONS:
        sec = d["sections"].get(key) or {}
        groups = sorted(sec.get("groups", []), key=lambda g: priority(g, 2))
        cards = sorted(sec.get("cards", []), key=priority)
        n = sum(int(g["count"]) for g in groups) + len(cards)
        if not n:
            continue
        num += 1
        inner = "".join(group(g, accent) for g in groups) + "".join(card(c, accent) for c in cards)
        rows.append(block(heading(f"{num}. {title}", n, note) + inner))
    if d.get("all_clear"):
        rows.append(block(f'<div style="font-size:12px;color:{FAINT};line-height:1.5">{E(d["all_clear"])}</div>', "4px 24px 0 24px"))
    if d.get("tidy"):
        rows.append(block(f'<div style="font-size:12px;color:{FAINT};line-height:1.5">{E(d["tidy"])}</div>', "6px 24px 0 24px"))
    rows.append(block(f'<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#F1EFE8;border-radius:6px">'
                      f'<tr><td style="padding:10px 14px;font-family:{FONT};font-size:12px;color:{SOFT};line-height:1.6">'
                      f'<b>How the buttons work.</b><br>'
                      f'<b>Approve, Hold and End</b> on desk items open a short email to the desk that is already written. Press Send and it is done at the next desk run (09:47, 13:47 or 18:47).<br>'
                      f'<b>Approve</b> on a held email opens the approval page, where you send it or discard it.<br>'
                      f'<b>Buttons that mention Claude</b> open a new Claude chat with the instruction already written.<br>'
                      f'<b>Edit and Open</b> take you to the draft, the document or the email itself.</td></tr></table>', "18px 24px 0 24px"))
    links = "".join(button(l["label"], l["url"], i == 0) for i, l in enumerate(d["links"]))
    rows.append(f'<tr><td style="padding:18px 24px 4px 24px;border-top:1px solid {LINE};font-family:{FONT}">'
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
