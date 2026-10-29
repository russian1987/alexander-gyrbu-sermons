# Александр Гырбу — проповеди по темам (unofficial index)
Static site (HTML/CSS/JS, no build). All data is in `videos.json`; videos are only linked/embedded from YouTube.

## Update automatically
    pip install yt-dlp && python3 update.py
`update.py` searches YouTube + known channels, keeps only titles naming Гырбу/Girbu/Gyrbu/Gîrbu, fetches dates (cached in `meta_cache.json`), assigns topics by keyword rules (`TOPICS` list) and rewrites `videos.json`. Commit and push.

## Add a video by hand
Add an object to `extra.json` (a JSON list; merged on each update):
    {"id":"VIDEO_ID","title":"...","channel":"...","date":"YYYYMMDD","duration":3600,"type":"sermon","topics":["Вера"],"thumb":"https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg"}
`type` is `sermon` or `clip`. To add a topic, add a `(name, regex)` pair to `TOPICS` in update.py.

## Summaries (конспекты)
`summaries/<id>.json` = bilingual RU/EN summary; `summaries/index.json` lists ids (cards show a "Конспект / Summary" link only for these).
Pipeline: `python3 tools/summarize.py fetch <id>` (captions → transcripts/, git-ignored) → write summaries/<id>.json → `python3 tools/summarize.py index`.
`update.py` only rewrites videos.json/meta_cache.json, so summaries survive re-runs. Page: `summary.html?id=<id>`.
