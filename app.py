import os, uuid, subprocess, threading, time
from pathlib import Path
from flask import Flask, request, jsonify, send_file, render_template_string, abort
from werkzeug.utils import secure_filename

ROOT = Path(__file__).resolve().parent
UPLOADS = ROOT / "uploads"
OUTPUTS = ROOT / "outputs"
WORK = ROOT / "work"
for p in (UPLOADS, OUTPUTS, WORK):
    p.mkdir(exist_ok=True)

ALLOWED = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"}
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "100"))
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 1024 * 1024
jobs = {}
lock = threading.Lock()

PAGE = r"""<!doctype html>
<html lang="si">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cartoon Studio</title>
  <style>
    *{box-sizing:border-box}body{margin:0;background:linear-gradient(145deg,#111827,#263b55);font-family:system-ui,-apple-system,sans-serif;color:#f8fafc;min-height:100vh}
    .wrap{max-width:760px;margin:auto;padding:28px 16px 60px}.hero{text-align:center;margin:12px 0 26px}
    .logo{font-size:42px}.hero h1{font-size:clamp(28px,6vw,42px);margin:6px 0}.hero p{color:#cbd5e1;margin:0}
    .panel{background:#fff;color:#172033;border-radius:22px;padding:22px;box-shadow:0 18px 50px #0005}
    label{display:block;font-weight:700;margin:16px 0 7px}input,textarea,select{width:100%;padding:13px;border:1px solid #cbd5e1;border-radius:12px;font:inherit;background:#f8fafc;color:#172033}
    textarea{min-height:120px;resize:vertical}.hint{font-size:13px;color:#64748b;margin-top:6px}
    .filebox{border:2px dashed #94a3b8;border-radius:14px;padding:18px;background:#f8fafc}
    button{width:100%;border:0;border-radius:13px;background:#6d4aff;color:white;padding:15px;font-weight:800;font-size:17px;margin-top:22px;cursor:pointer}
    button:disabled{opacity:.55;cursor:wait}.status{display:none;margin-top:18px;padding:14px;border-radius:12px;background:#eef2ff;color:#27336a;overflow-wrap:anywhere}
    .bar{height:9px;background:#dbeafe;border-radius:9px;margin-top:10px;overflow:hidden}.bar span{display:block;height:100%;width:20%;background:#6d4aff;animation:pulse 1.3s infinite alternate}
    @keyframes pulse{to{width:85%}}.download{display:inline-block;margin-top:12px;padding:12px 16px;background:#0f9d72;color:white;text-decoration:none;border-radius:10px;font-weight:700}
    .foot{text-align:center;color:#cbd5e1;font-size:12px;margin-top:20px;line-height:1.6}
    .two{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:520px){.two{grid-template-columns:1fr}.panel{padding:17px}}
  </style>
</head>
<body><main class="wrap">
  <header class="hero"><div class="logo">🎬</div><h1>Cartoon Studio</h1><p>ඔබේ voice එකෙන් cartoon MP4 එකක් හදන්න</p></header>
  <section class="panel">
    <form id="form">
      <label>Voice file එක</label>
      <div class="filebox"><input id="voice" name="voice" type="file" accept="audio/*" required>
      <div class="hint">MP3, WAV, M4A, AAC, OGG හෝ FLAC · උපරිම {{max_mb}} MB</div></div>
      <label>Cartoon title එක</label><input name="title" maxlength="70" placeholder="උදා: පුංචි වීරයා">
      <label>කතාවේ script එක (Optional)</label>
      <textarea name="script" placeholder="Voice එකේ කියන කතාව මෙතැන paste කරන්න. Script එක දුන්නොත් scenes වඩා හොඳින් බෙදන්න පුළුවන්."></textarea>
      <div class="two">
        <div><label>Video size</label><select name="size"><option value="720x1280">720 × 1280 (ඉක්මන්)</option><option value="1080x1920">1080 × 1920 (උසස්)</option></select></div>
        <div><label>Quality</label><select name="preset"><option value="ultrafast">ඉක්මන්</option><option value="fast" selected>සාමාන්‍ය</option><option value="medium">වඩා හොඳ</option></select></div>
      </div>
      <button id="go" type="submit">✨ Cartoon MP4 හදන්න</button>
    </form>
    <div class="status" id="status"><strong id="msg">ඔබේ video එක සකස් කරමින්...</strong><div class="bar"><span></span></div><div id="detail" class="hint"></div></div>
  </section>
  <p class="foot">ඔබේ audio එක server එකට upload කර render කරයි. Render අවසන් වූ පසු MP4 එක download කරන්න.<br>මෙය procedural 2D cartoon renderer එකකි; AI voice recognition හෝ full 3D animation නොමැත.</p>
</main>
<script>
  const form=document.getElementById('form'), btn=document.getElementById('go'), statusBox=document.getElementById('status');
  form.addEventListener('submit',async e=>{
    e.preventDefault();
    const f=document.getElementById('voice').files[0];
    if(!f){alert('Voice file එක තෝරන්න.');return}
    btn.disabled=true;btn.textContent='Upload කරමින්...';statusBox.style.display='block';
    document.getElementById('msg').textContent='Voice file එක upload කරමින්...';
    document.getElementById('detail').textContent='File size: '+(f.size/1024/1024).toFixed(1)+' MB';
    try{
      const data=new FormData(form);
      const r=await fetch('/api/render',{method:'POST',body:data});
      const j=await r.json();if(!r.ok)throw new Error(j.error||'Upload අසාර්ථකයි');
      document.getElementById('msg').textContent='Video එක render කරමින්...';
      document.getElementById('detail').textContent='මේ සඳහා audio එකේ දිග සහ video resolution එක අනුව කාලයක් ගත විය හැක.';
      const poll=async()=>{
        const s=await fetch('/api/status/'+j.id);const x=await s.json();
        if(x.state==='done'){
          document.getElementById('msg').textContent='✅ ඔබේ Cartoon MP4 එක සූදානම්!';
          document.getElementById('detail').innerHTML='<a class="download" href="/download/'+j.id+'">⬇ MP4 Download කරන්න</a>';
          btn.disabled=false;btn.textContent='✨ තවත් Cartoon එකක් හදන්න';return;
        }
        if(x.state==='error'){throw new Error(x.error||'Render අසාර්ථකයි')}
        document.getElementById('detail').textContent=x.message||'Rendering...';
        setTimeout(poll,2500);
      }; await poll();
    }catch(err){document.getElementById('msg').textContent='⚠️ '+err.message;document.getElementById('detail').textContent='Audio format එක සහ server setup එක පරීක්ෂා කරන්න.';btn.disabled=false;btn.textContent='නැවත උත්සාහ කරන්න'}
  });
</script></body></html>"""

def run_job(job_id, audio_path, title, script, size, preset):
    out = OUTPUTS / f"{job_id}.mp4"
    work = WORK / job_id
    work.mkdir(exist_ok=True)
    script_path = work / "script.txt"
    script_path.write_text(script, encoding="utf-8")
    cmd = ["python", str(ROOT/"engine"/"render.py"), "--voice", str(audio_path),
           "--out", str(out), "--workdir", str(work), "--title", title,
           "--script", str(script_path), "--size", size, "--preset", preset]
    try:
        with lock:
            jobs[job_id] = {"state":"rendering", "message":"Cartoon frames සහ audio එක සකස් කරමින්..."}
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=60*60)
        if p.returncode != 0:
            raise RuntimeError((p.stderr or p.stdout or "Render failed")[-1800:])
        with lock:
            jobs[job_id] = {"state":"done", "message":"MP4 ready"}
    except Exception as e:
        with lock:
            jobs[job_id] = {"state":"error", "error":str(e), "message":"Render failed"}
    finally:
        try: audio_path.unlink(missing_ok=True)
        except Exception: pass

@app.get("/")
def index():
    return render_template_string(PAGE, max_mb=MAX_UPLOAD_MB)

@app.post("/api/render")
def start_render():
    f = request.files.get("voice")
    if not f or not f.filename:
        return jsonify(error="Voice file එකක් තෝරන්න."), 400
    ext = Path(secure_filename(f.filename)).suffix.lower()
    if ext not in ALLOWED:
        return jsonify(error="මෙම audio format එක සහාය නොදක්වයි."), 400
    job_id = uuid.uuid4().hex[:12]
    audio_path = UPLOADS / f"{job_id}{ext}"
    f.save(audio_path)
    title = (request.form.get("title") or "My Cartoon").strip()[:70]
    script = (request.form.get("script") or "").strip()[:30000]
    size = request.form.get("size", "720x1280")
    if size not in {"720x1280","1080x1920"}:
        audio_path.unlink(missing_ok=True)
        return jsonify(error="Invalid video size"), 400
    preset = request.form.get("preset", "fast")
    if preset not in {"ultrafast","fast","medium"}: preset = "fast"
    with lock: jobs[job_id] = {"state":"queued", "message":"Queue එකට එක් කළා..."}
    threading.Thread(target=run_job, args=(job_id,audio_path,title,script,size,preset), daemon=True).start()
    return jsonify(id=job_id)

@app.get("/api/status/<job_id>")
def status(job_id):
    with lock: data = jobs.get(job_id)
    if not data: return jsonify(error="Job එක හමු නොවීය."), 404
    return jsonify(data)

@app.get("/download/<job_id>")
def download(job_id):
    with lock: data = jobs.get(job_id)
    path = OUTPUTS / f"{job_id}.mp4"
    if not data or data.get("state") != "done" or not path.exists(): abort(404)
    return send_file(path, as_attachment=True, download_name="cartoon_short.mp4", mimetype="video/mp4")

@app.errorhandler(413)
def too_large(_):
    return jsonify(error=f"File එක විශාලයි. උපරිමය {MAX_UPLOAD_MB} MB."), 413

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT","7860")), debug=False)
