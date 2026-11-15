"""Builds docs/presentacion/guion_jass_es.html (+ PDF with Chrome) from docs/PITCH_SCRIPT_ES.md: one source of truth.
Usage (from docs/presentacion):  python build_guion.py"""
import io, os, re, subprocess, tempfile, shutil, html

HERE = os.path.dirname(os.path.abspath(__file__))
md = io.open(os.path.join(HERE, '..', 'PITCH_SCRIPT_ES.md'), encoding='utf-8').read()

def esc(t): return html.escape(t, quote=False)
def fmt(body):
    body = body.strip()
    out = []
    for para in body.split('\n'):
        p = esc(para.strip())
        p = re.sub(r'^&quot;|&quot;$|^"|"$', '', p)
        p = re.sub(r'\[([^\]]+)\]', r'<span class="cue">[\1]</span>', p)
        if p: out.append(p)
    return '<br>'.join(out)

blocks = []
for m in re.finditer(r'\*\*(\d) · ([^\n]*?)\*\*\n(.*?)(?=\n\*\*\d ·|\n## |\Z)', md, re.S):
    n, head, body = m.group(1), m.group(2), m.group(3)
    t = re.search(r'\((\d+) s\)', head); title = re.sub(r'\s*\(\d+ s\).*$', '', head)
    note = re.search(r'—\s*(.*)$', head)
    blocks.append((n, title, t.group(1) if t else '', note.group(1) if note else '', fmt(body)))

CUM = [10, 50, 85, 135, 180, 220, 240]
def clock(s): return f'{s // 60}:{s % 60:02d}'
rows = ''
prev = 0
for (n, title, secs, note, text), end in zip(blocks, CUM):
    rows += f'<section><div class="h"><span class="n">{n}</span><b>{esc(title)}</b><span class="t">{clock(prev)}–{clock(end)}</span>' + (f'<span class="nt">{esc(note)}</span>' if note else '') + f'</div><p>{text}</p></section>\n'
    prev = end

page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><title>Guion de Jass · RotaHawk</title>
<style>
  @page{{size:A4;margin:10mm 13mm}}
  *{{box-sizing:border-box}}
  body{{font:13.6px/1.42 "Segoe UI",system-ui,Arial,sans-serif;color:#111;margin:0}}
  h1{{font-size:22px;margin:0;color:#0B1F3A}}h1 span{{color:#b8921d}}
  .sub{{color:#555;margin:2px 0 8px;font-size:12px}}
  section{{margin:0 0 6px;break-inside:avoid}}
  .h{{display:flex;align-items:center;gap:8px;border-bottom:2px solid #D4AF37;padding-bottom:2px;margin-bottom:3px}}
  .n{{background:#0B1F3A;color:#fff;border-radius:50%;width:20px;height:20px;display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700}}
  .h b{{font-size:14px;color:#0B1F3A}}.t{{margin-left:auto;font-weight:700;color:#8a6d12;font-size:13px}}.nt{{font-size:11px;color:#666}}
  p{{margin:0}}
  .cue{{color:#9a6a00;font-style:italic;font-size:12.5px}}
  .box{{background:#fff7dc;border-left:3px solid #D4AF37;padding:4px 9px;margin:6px 0;font-size:11.5px}}
  .box b{{color:#0B1F3A}}
  .foot{{color:#666;font-size:11px;margin-top:6px}}
  * {{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
</style></head><body>
<h1>Rota<span>Hawk</span> · Guion de Jass</h1>
<p class="sub">Solo Jass expone · Pitch de 3 a 5 minutos (este guion: 4:00) · Los textos entre corchetes son indicaciones, no se dicen</p>
{rows}
<div class="box"><b>Para ajustar el tiempo.</b> A 3:30: omite la explicación del chat en la slide 4 (−15 s) y la última frase de la slide 6 (−10 s). Hasta 5:00: deja correr la animación dos veces o abre la web en vivo para los jueces.<br>
<b>Si algo falla.</b> Sonda con guiones: di la frase de la slide 5 y sigue. Sin internet: la web usa su respuesta guardada y la animación es local. La animación falla: reproduce el MP4. Cronómetro y notas: tecla <b>P</b> en las slides.</div>
<p class="foot">jassjmz.github.io/rotahalcon · slides/es.html · Guion escrito por el Rol 4: léelo en voz alta y cámbialo a tus palabras.</p>
</body></html>'''
src = os.path.join(HERE, 'guion_jass_es.html'); io.open(src, 'w', encoding='utf-8', newline='\n').write(page)

CH = next((p for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe') if os.path.exists(p)), None)
if CH:
    prof = tempfile.mkdtemp()
    subprocess.run([CH, '--headless=new', '--disable-gpu', f'--user-data-dir={prof}', '--no-pdf-header-footer', f'--print-to-pdf={os.path.join(HERE, "guion_jass_es.pdf")}', 'file:///' + src.replace('\\', '/')],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    shutil.rmtree(prof, ignore_errors=True)
    print('wrote guion_jass_es.html and guion_jass_es.pdf')
else:
    print('wrote guion_jass_es.html (Chrome not found: print it to PDF yourself)')
