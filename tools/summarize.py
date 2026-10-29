"""Pipeline for per-video summaries.
Step 1: python3 tools/summarize.py fetch <id>...   -> downloads RU captions, writes transcripts/<id>.txt (cleaned, not committed)
Step 2: summary JSON is written (by an LLM/editor) to summaries/<id>.json:
  {id,title,ru:{overview,outline[],verses[]},en:{...},source:'auto-captions',generated}
Step 3: python3 tools/summarize.py index  -> rebuilds summaries/index.json (list of ids with summaries)
update.py never touches summaries/."""
import sys,os,re,json,subprocess,glob,html
D=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def clean_vtt(p):
    out=[]
    for l in open(p,encoding='utf-8'):
        l=l.strip()
        if not l or '-->' in l or l.startswith(('WEBVTT','Kind:','Language:')):continue
        l=html.unescape(re.sub(r'<[^>]+>','',l)).strip()
        if l and (not out or out[-1]!=l):out.append(l)
    return re.sub(r'\s+',' ',' '.join(out)).replace('[музыка]','').strip()
def fetch(i,tmp='/tmp/gyrbu-subs'):
    os.makedirs(tmp,exist_ok=True);os.makedirs(D+'/transcripts',exist_ok=True)
    subprocess.run(['yt-dlp','-q','--no-warnings','--skip-download','--write-subs','--write-auto-subs','--sub-langs','ru-orig,ru','--sub-format','vtt','-o',f'{tmp}/{i}','https://www.youtube.com/watch?v='+i])
    f=[x for x in (f'{tmp}/{i}.ru-orig.vtt',f'{tmp}/{i}.ru.vtt') if os.path.exists(x)]
    if not f:print(i,'NO CAPTIONS');return None
    t=clean_vtt(f[0]);open(f'{D}/transcripts/{i}.txt','w').write(t);print(i,len(t),'chars');return t
def index():
    ids=sorted(os.path.basename(p)[:-5] for p in glob.glob(D+'/summaries/*.json') if not p.endswith('index.json'))
    json.dump(ids,open(D+'/summaries/index.json','w'));print(len(ids),'summaries')
if __name__=='__main__':
    c=sys.argv[1]
    if c=='fetch':[fetch(i) for i in sys.argv[2:]]
    elif c=='index':index()
