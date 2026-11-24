import json, re, sys

spec = json.load(open(sys.argv[1]))
NOM = "https://www.gfmreview.com/nominations"
THIRD = {"01": "#FinTech", "02": "#WealthManagement", "03": "#FinTech", "04": "#InsurTech", "05": "#Payments",
         "06": "#FinTech", "07": "#FinTech", "08": "#FinancialServices", "09": "#FinancialInclusion"}
DAYS = {"2026-11-24": "Tuesday 24 November", "2026-11-29": "Sunday 29 November", "2026-12-01": "Tuesday 1 December",
        "2026-12-06": "Sunday 6 December", "2026-12-08": "Tuesday 8 December", "2026-12-13": "Sunday 13 December",
        "2026-12-15": "Tuesday 15 December", "2026-12-20": "Sunday 20 December", "2026-12-22": "Tuesday 22 December"}
WORDS = {2: "two", 3: "three"}


def join_names(names):
    return names[0] if len(names) == 1 else ", ".join(names[:-1]) + " and " + names[-1]


out = []
for c in spec["cards"]:
    ws = c["winners"]
    n = WORDS[len(ws)]
    third = THIRD[c["id"]]
    tags = f"#GFMReviewAwards #FinancialServices {third}" if third != "#FinancialServices" else "#GFMReviewAwards #FinancialServices #Awards2026"
    lines = []
    for w in ws:
        lines.append(f"{w['name']}: {' and '.join(w['awards'])}")
    li = (f"Congratulations to {n} more GFM Review Award winners.\n"
          f"Each has been recognised for notable success in its field.\n\n"
          + "\n\n".join(lines) +
          "\n\nThe GFM Review Awards recognise companies and institutions judged on criteria including transparency, "
          "governance, innovation and customer service. We are delighted to celebrate each of these organisations.\n\n"
          f"Nominations are open, and entry is free:\n{NOM}\n\n{tags}")
    SHORT = {"Future Forex SA (Pty) Ltd": "Future Forex", "Provenance Ltd.": "Provenance", "Turim 21 Investimentos Ltda.": "Turim 21 Investimentos",
             "Rahimafrooz Globatt Limited": "Rahimafrooz Globatt", "ALGOGENE FINANCIAL TECHNOLOGY COMPANY LIMITED": "ALGOGENE",
             "BYDFi Fintech LTD": "BYDFi", "PRLab B.V.": "PRLab", "QuietGrowth Pty Ltd": "QuietGrowth", "X Securities (Mauritius) Ltd": "X Securities",
             "Rainforest Pay, Inc.": "Rainforest", "Giottus Technologies Private Limited": "Giottus", "SV Capital Proprietary Limited": "SV Capital",
             "Fennech Pte Ltd": "Fennech", "Seto Financial Inc.": "Seto Financial", "Senior Summit Insurance Group LLC": "Senior Summit Insurance Group",
             "Antivirus s.r.o. ": "", "Antivirus s.r.o.": "Antivirus (Patron GO)", "PT HastaPrada Indonesia": "HastaPrada"}
    short = [SHORT.get(w["name"], w["name"]) for w in ws]
    x = (f"Congratulations to {n} more GFM Review Award winners: {join_names(short)}.\n\n"
         f"Nominations are open, and entry is free: {NOM}\n\n#GFMReviewAwards #FinancialServices")
    xlen = len(re.sub(r"https?://\S+", "x" * 23, x))
    out.append({"id": c["id"], "date": c["date"], "day": DAYS[c["date"]], "linkedin": li, "x": x, "x_len": xlen,
                "alt": f"GFM Review Awards 2026 winners card, {c['month']}: " + "; ".join(lines) + ". Nominate at gfmreview.com/nominations."})

json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
md = ["# GFM Review Award winner series: captions for approval\n",
      "Posts at 12:00 London time to the GFM Review LinkedIn page and GFM Review X, one card each time.\n"]
for o in out:
    md.append(f"## Card {o['id']}: {o['day']}\n\n### LinkedIn\n\n{o['linkedin']}\n\n### X ({o['x_len']} characters)\n\n{o['x']}\n")
open(sys.argv[3], "w").write("\n".join(md))
for o in out:
    print(o["id"], o["day"], "X:", o["x_len"], "| em dash:", "—" in o["linkedin"] + o["x"], "|", o["x"].split("\n")[0][:110])
