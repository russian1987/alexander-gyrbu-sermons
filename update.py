#!/usr/bin/env python3
"""Re-collect Alexander Gyrbu videos from YouTube (via yt-dlp) and regenerate videos.json.
Usage: pip install yt-dlp && python3 update.py   (manual entries in extra.json are merged)"""
import json,subprocess,re,os
NAMES=['гырбу','гирбу','girbu','gyrbu','gîrbu','gârbu']
SOURCES=["ytsearch300:Александр Гырбу проповедь","ytsearch300:Александр Гырбу","ytsearch100:Гырбу проповедь 2025","ytsearch100:Гырбу проповедь 2024","ytsearch100:Alexander Girbu sermon","ytsearch100:Гырбу семинар","ytsearch100:Гырбу shorts",
 "https://www.youtube.com/channel/UCvexZwEJiEUrOoHKVvlB13A/videos","https://www.youtube.com/channel/UCvexZwEJiEUrOoHKVvlB13A/shorts",
 "https://www.youtube.com/channel/UCOhWy-saA6FC2RniOHVQryg/videos","https://www.youtube.com/channel/UCOhWy-saA6FC2RniOHVQryg/shorts"]
TOPICS=[("Секты и апологетика","свидетел|jehovah|адвентист|adventist|харизмат|charismat|кальвин|calvin|ислам|islam|католи|cathol|purgator|чистилищ|мормон|религи|religion|секта|cult|языках|языке|tongues|предопредел|predestin|watchtower"),
("Учение о Боге и Троица","троиц|триедин|trinity|иисус не бог|божеств"),("Вопросы и ответы","вопрос|ответ|questions|answers|q&a|интервью|interview|беседа|разговор"),("Вера","faith|trust|вер[аыуе]\\b|доверие|faith"),("Молитва","pray|молитв|молит|prayer"),("Спасение и Евангелие","salvation|gospel|repent|sin\\b|sinned|baptism|крещени|witness to|спасени|евангел|покаян|крест|возрожд|грешн|грех"),
("Семья и брак","famil|marri|husband|wife|child|parent|семь|брак|муж|жен|дет[иея]|родител|молодожен|свадьб"),("Святой Дух","holy spirit|дух[аеу]? свят|святого духа|святой дух|духовн"),
("Покой и Суббота","суббот|покой|отдых"),("Благодать и любовь","grace|love|forgiv|encourag|offend|благодат|любов|милост|прощ"),("Последнее время","end times|judgment|eternity|hell|heaven|armageddon|1000|царство|soul|death|смерт|будущ|знаки|future|последн|пришеств|антихрист|вечност|небес|рай|ад\\b|суд"),
("Служение и церковь","church|ministr|serv|братское|служ|церк|пастор|проповедник|лидер"),("Испытания и страдания","suffer|trial|pain|испытан|страдан|скорб|боль|бур[яи]|трудност|утешен"),
("Христианская жизнь","life|temptation|alcohol|beer|алкогол|vanity|сует|conscience|совест|diligen|idol|идол|commandment|заповед|ходить перед|relationship|scales|price|жизн|ученич|святост|послушан|сердц|мудрост|искушен|победа"),("Праздники","christmas|easter|thanksgiving|рождеств|пасх|воскрес|жатв|благодарени|нов(ый|ого) год"),
("Молодёжь","youth|young|молод|подрост|юнош"),("Библия","bible|scripture|библи|слово божье|писани")]
def run(u):
    try:return json.loads(subprocess.run(['yt-dlp','--flat-playlist','-J',u],capture_output=True,text=True,timeout=900).stdout).get('entries',[])
    except Exception:return []
def topics(t):
    l=t.lower();r=[n for n,p in TOPICS if re.search(p,l)]
    return r[:2] or ["Другое"]
vids={}
for s in SOURCES:
    for e in run(s):
        t=e.get('title') or '';i=e.get('id')
        if not i or not any(n in t.lower() for n in NAMES):continue
        url=e.get('url') or ''
        d=e.get('duration')
        short='/shorts/' in url or '/shorts' in s or (d is not None and d<=180)
        v=vids.get(i,{})
        v.update({k:x for k,x in dict(id=i,title=t,channel=e.get('channel') or e.get('uploader') or v.get('channel') or ('Дети Авраама- Children of Abraham' if 'UCvexZ' in s else ('Духовные Мысли' if 'UCOhWy' in s else '')),
          duration=d or v.get('duration'),date=e.get('upload_date') or v.get('date'),views=e.get('view_count') or v.get('views'),
          type='clip' if (short or v.get('type')=='clip') else 'sermon',topics=topics(t),thumb=f"https://i.ytimg.com/vi/{i}/hqdefault.jpg").items() if x is not None})
        vids[i]=v
# enrich with upload dates (cached in meta_cache.json)
cache=json.load(open('meta_cache.json')) if os.path.exists('meta_cache.json') else {}
from concurrent.futures import ThreadPoolExecutor
def meta(i):
    try:
        d=json.loads(subprocess.run(['yt-dlp','-J','--skip-download','--no-warnings','https://www.youtube.com/watch?v='+i],capture_output=True,text=True,timeout=120).stdout)
        return i,{'date':d.get('upload_date'),'duration':d.get('duration'),'channel':d.get('channel'),'desc':(d.get('description') or '')[:300]}
    except Exception:return i,None
todo=[i for i in vids if i not in cache]
with ThreadPoolExecutor(12) as ex:
    for i,m in ex.map(meta,todo):
        if m:cache[i]=m
json.dump(cache,open('meta_cache.json','w'),ensure_ascii=False)
for i,v in vids.items():
    m=cache.get(i)
    if m:
        for k in ('date','duration','channel'):
            if m.get(k):v[k]=m[k]
        if v['type']=='sermon' and m.get('duration') and m['duration']<=180:v['type']='clip'
        tp=topics(v['title'])
        v['topics']=tp if tp!=["Другое"] else topics(m.get('desc',''))
if os.path.exists('extra.json'):
    for v in json.load(open('extra.json')):vids[v['id']]=v
out=sorted(vids.values(),key=lambda v:-(v.get('views') or 0))
json.dump(out,open('videos.json','w'),ensure_ascii=False,indent=1)
print(len(out),'videos',sum(v['type']=='sermon' for v in out),'sermons')
