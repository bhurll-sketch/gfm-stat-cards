# gfm-stat-cards
Public infographic cards for GFM Review

## Renderer (from 16 Nov 2026)
`tools/gfm_render.py` builds the 1080 x 1350 standard card and the Friday Week in Markets carousel to the GFM Review Social Posting Instructions (sections 6 and 7).

    python3 -I tools/gfm_render.py card tools/example_card.json out.png
    python3 -I tools/gfm_render.py carousel tools/example_carousel.json out_dir

Cards go in `cards/` (day_date_topic.png); carousels in `carousels/` (PNGs plus PDF).

## Award winner cards (from 24 Nov 2026)
`tools/award_card/gfm_award_card.py` builds the GFM Review Awards winners card (1080 x 1350): dark blue bands, recognition line, two or three winners with their logos, nominations panel, month in the footer. Winners and logos are listed in `tools/award_card/series.json`; logos sit in `tools/award_card/logos/`.

    python3 -I tools/award_card/gfm_award_card.py tools/award_card/series.json out_dir tools/award_card

Cards go in `cards/award-winners/` (day_date_award-winners-NN.png). Posted Tuesdays and Sundays at 12:00 to the GFM Review LinkedIn page and X.
