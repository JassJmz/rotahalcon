"""Takes the real screenshots used on the result slide (web compare cards and assistant chat), in English and Spanish.
Needs Chrome, a local server serving web/ (python -m http.server 8090 --directory web) and the live API.
Usage (from web/slides):  python make_shots.py [base_url]
Re-run it whenever the engine or the assistant answers change, then python build_slides.py."""
import os, subprocess, sys, tempfile, shutil
from PIL import Image, ImageChops

BASE = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8090'
CHROME = next((p for p in (r'C:\Program Files\Google\Chrome\Application\chrome.exe', r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe') if os.path.exists(p)), 'chrome')
HERE = os.path.dirname(os.path.abspath(__file__)); IMG = os.path.join(HERE, 'img'); os.makedirs(IMG, exist_ok=True)
BG = (11, 31, 58)

def shot(kind, lang, size):
    out = os.path.join(IMG, f'shot-{kind}-{lang}.png'); prof = tempfile.mkdtemp()
    url = f'{BASE}/index.html?lang={lang}&shot={kind}&v={os.getpid()}'
    subprocess.run([CHROME, '--headless=new', '--disable-gpu', f'--user-data-dir={prof}', '--hide-scrollbars', '--force-device-scale-factor=2',
                    '--virtual-time-budget=60000', f'--window-size={size}', f'--screenshot={out}', url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=240)
    shutil.rmtree(prof, ignore_errors=True)
    im = Image.open(out).convert('RGB')
    diff = ImageChops.difference(im, Image.new('RGB', im.size, BG)).convert('L').point(lambda v: 255 if v > 12 else 0)
    box = diff.getbbox()
    if box:
        im = im.crop((max(0, box[0] - 4), max(0, box[1] - 4), min(im.width, box[2] + 4), min(im.height, box[3] + 4)))
    im.save(out.replace('.png', '.webp'), 'WEBP', quality=92, method=6); os.remove(out)
    print(kind, lang, im.size)

for lang in ('en', 'es'):
    shot('compare', lang, '1100,420'); shot('chat', lang, '640,260')
