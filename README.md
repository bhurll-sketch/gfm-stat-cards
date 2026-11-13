# gfm-stat-cards
Public infographic cards for GFM Review

## Renderer (from 16 Nov 2026)
`tools/gfm_render.py` builds the 1080 x 1350 standard card and the Friday Week in Markets carousel to the GFM Review Social Posting Instructions (sections 6 and 7).

    python3 -I tools/gfm_render.py card tools/example_card.json out.png
    python3 -I tools/gfm_render.py carousel tools/example_carousel.json out_dir

Cards go in `cards/` (day_date_topic.png); carousels in `carousels/` (PNGs plus PDF).
