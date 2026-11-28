# GFM Review article artwork and infographics (v2, 28 Nov 2026)

    git clone --depth 1 https://github.com/bhurll-sketch/gfm-stat-cards /tmp/gfm && cd /tmp/gfm/article-art
    python3 -I gfm_art.py artwork spec.json artwork.jpg        # 1800 x 1200
    python3 -I gfm_art.py infographic spec.json infographic.jpg # 1600 x 1000

Fonts bundled (Noto Serif headlines, Open Sans text). See examples/ for every spec shape.

Artwork layouts: cover, split, tiers, constellation, number (needs big_number {value, caption, source}).
Palettes: pale_sky, steel, ocean, ice, navy_night, twilight.
Infographic types: line (6+ real points), track (score comparison), ranked (logos), stats (+ optional timeline), combo.
Logos: companies[].logo = path to a checked logo file from the firm's own website; otherwise the name is shown.
The renderer refuses overlapping tiles and text that does not fit: change the spec and run again.
