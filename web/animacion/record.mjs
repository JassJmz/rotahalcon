// Records the short animation to an MP4 with headless Chrome (DevTools screencast) and ffmpeg. No screen recorder needed.
//   node record.mjs es [out.mp4]      (or "en")        Output default: ./RotaHawk_animacion_<lang>.mp4
// Needs: Node 22+, Chrome, and an ffmpeg (here: the one bundled with the Python package imageio-ffmpeg, or any ffmpeg on PATH).
import { spawn, spawnSync, execFileSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readdirSync, rmSync, existsSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const lang = process.argv[2] === 'en' ? 'en' : 'es';
const out = resolve(process.argv[3] || join(HERE, `RotaHawk_animacion_${lang}.mp4`));
const W = 1280, H = 720, SCALE = 1.5, DELAY = 1500, PORT = 9333 + (lang === 'en' ? 1 : 0), MAX_MS = 90000;

const CHROME = ['C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'].find(existsSync);
if (!CHROME) throw new Error('Chrome not found');
function findFfmpeg() {
  try { return execFileSync('python', ['-c', 'import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())'], { encoding: 'utf8' }).trim(); } catch (e) { /* fall through */ }
  return 'ffmpeg';
}
const FFMPEG = findFfmpeg();

const work = mkdtempSync(join(tmpdir(), 'rotahawk-rec-'));
const framesDir = join(work, 'frames'); mkdirSync(framesDir);
const url = pathToFileURL(join(HERE, 'index.html')).href + `?short=1&lang=${lang}&delay=${DELAY}`;

const chrome = spawn(CHROME, ['--headless=new', '--disable-gpu', `--remote-debugging-port=${PORT}`, `--user-data-dir=${join(work, 'profile')}`, `--window-size=${W},${H}`, '--hide-scrollbars', '--no-first-run', 'about:blank'], { stdio: 'ignore' });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const killChrome = () => { try { spawnSync('taskkill', ['/PID', String(chrome.pid), '/T', '/F'], { stdio: 'ignore' }); } catch (e) { /* ignore */ } };

try {
  let wsUrl;
  for (let i = 0; i < 60 && !wsUrl; i++) {
    try { const list = await (await fetch(`http://127.0.0.1:${PORT}/json/list`)).json(); wsUrl = list.find(t => t.type === 'page')?.webSocketDebuggerUrl; } catch (e) { /* not ready */ }
    if (!wsUrl) await sleep(250);
  }
  if (!wsUrl) throw new Error('Chrome did not start');
  const ws = new WebSocket(wsUrl);
  await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

  let id = 0; const pending = new Map(), frames = []; let loadedAt = null, nFrames = 0;
  const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); return; }
    if (m.method === 'Page.loadEventFired') loadedAt = Date.now() / 1000;
    if (m.method === 'Page.screencastFrame') {
      const { data, metadata, sessionId } = m.params; const name = `f${String(nFrames++).padStart(6, '0')}.jpg`;
      writeFileSync(join(framesDir, name), Buffer.from(data, 'base64')); frames.push({ name, ts: metadata.timestamp });
      send('Page.screencastFrameAck', { sessionId }).catch(() => {});
    }
  };

  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', { width: W, height: H, deviceScaleFactor: SCALE, mobile: false });
  await send('Page.startScreencast', { format: 'jpeg', quality: 92, maxWidth: Math.round(W * SCALE), maxHeight: Math.round(H * SCALE), everyNthFrame: 1 });
  await send('Page.navigate', { url });

  // wait for the page to announce the end of the animation
  const t0 = Date.now(); let done = false;
  while (Date.now() - t0 < MAX_MS) {
    await sleep(250);
    const r = await send('Runtime.evaluate', { expression: 'document.title' }).catch(() => null);
    if (r && r.result && r.result.value === 'ANIM_DONE') { done = true; break; }
  }
  if (!done) throw new Error('The animation did not finish in time');
  await sleep(1800);                                   // hold the last scene a moment
  const endTs = Date.now() / 1000;
  await send('Page.stopScreencast').catch(() => {});
  ws.close();

  const startTs = loadedAt + DELAY / 1000 - 0.2;       // first scene starts after the delay
  const used = frames.filter(f => f.ts >= startTs && f.ts <= endTs);
  if (used.length < 30) throw new Error(`Too few frames captured (${used.length})`);
  const lines = [];
  used.forEach((f, i) => {
    const next = i + 1 < used.length ? used[i + 1].ts : endTs;
    lines.push(`file '${join(framesDir, f.name).replace(/\\/g, '/')}'`, `duration ${Math.min(Math.max(next - f.ts, 0.001), 1.2).toFixed(4)}`);
  });
  lines.push(`file '${join(framesDir, used[used.length - 1].name).replace(/\\/g, '/')}'`);
  writeFileSync(join(work, 'list.txt'), lines.join('\n'));
  const secs = (used[used.length - 1].ts - used[0].ts).toFixed(1);
  console.log(`captured ${frames.length} frames, using ${used.length} (${secs} s, about ${(used.length / secs).toFixed(0)} fps)`);

  const r = spawnSync(FFMPEG, ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', join(work, 'list.txt'),
    '-vf', 'scale=1920:1080:flags=lanczos,format=yuv420p', '-r', '30', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', out], { encoding: 'utf8' });
  if (r.status !== 0) throw new Error('ffmpeg failed: ' + r.stderr);
  console.log('wrote', out);
} finally {
  killChrome();
  await sleep(500);
  try { rmSync(work, { recursive: true, force: true }); } catch (e) { /* ignore */ }
}
