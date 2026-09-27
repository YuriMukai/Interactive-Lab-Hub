#!/usr/bin/env python3
"""
Parking Assistant - Wizard of Oz prototype (Lab 3 Part 2)

The Pi acts as the car:
  - listens to the driver (uses listen.py for VAD + faster-whisper)
  - speaks with Piper
  - shows its state on the MiniPiTFT screen (listening / thinking / checking safety ...)
  - top button (A) = emergency STOP, bottom button (B) = reset to idle

The wizard controls the car from a web page:
  http://ras-yuri.local:5000   (phone or laptop on the same Wi-Fi)

Everything is saved to ../session_log.jsonl
"""
import os, re, sys, json, time, math, queue, atexit, threading, subprocess, datetime, logging
from flask import Flask, jsonify, request, Response

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = os.path.join(HERE, "..", "voices")
VOICE = "en_US-lessac-medium"
MIN_SILENCE = "0.7"          # end-of-turn silence (seconds) - from Part 1 results
ECHO_WINDOW = 2.5            # ignore transcripts this soon after the car spoke (it hears itself)
LOG_PATH = os.path.join(HERE, "..", "session_log.jsonl")

# ---------------------------------------------------------------- shared state
lock = threading.Lock()
state = {"screen": "idle", "changed": time.monotonic(),
         "speaking": False, "speaking_until": 0.0}
log = []


def add_log(kind, text):
    entry = {"time": datetime.datetime.now().strftime("%H:%M:%S"), "kind": kind, "text": text}
    with lock:
        log.append(entry)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    print(f"[{entry['time']}] {kind:>7}: {text}", flush=True)


def get_screen():
    with lock:
        return state["screen"]


def set_screen(name):
    with lock:
        if state["screen"] == name:
            return
        state["screen"] = name
        state["changed"] = time.monotonic()
    add_log("screen", name)


# ---------------------------------------------------------------- speaking
speech_q = queue.Queue()


def say(text, start=None, after=None):
    speech_q.put((text, start, after))


def speech_worker():
    while True:
        text, start, after = speech_q.get()
        if start:
            set_screen(start)
        elif get_screen() in ("idle", "listening", "thinking"):
            set_screen("talking")
        with lock:
            state["speaking"] = True
        add_log("car", text)
        piper = subprocess.Popen(
            [sys.executable, "-m", "piper", "--model", VOICE, "--data-dir", VOICES,
             "--output-raw", "--", text],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        subprocess.run(["aplay", "-q", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                       stdin=piper.stdout)
        piper.wait()
        with lock:
            state["speaking"] = False
            state["speaking_until"] = time.monotonic()
        if after:
            set_screen(after)
        elif get_screen() == "talking":
            set_screen("listening")


def clear_speech_queue():
    while not speech_q.empty():
        try:
            speech_q.get_nowait()
        except queue.Empty:
            break


# ---------------------------------------------------------------- listening
LINE_RE = re.compile(r"^\[.*?\]\s+(.*)$")   # listen.py prints "[0.7s speech, ...]  text"
listen_proc = None


def listener():
    global listen_proc
    cmd = [sys.executable, "-u", os.path.join(HERE, "listen.py"), "--min-silence", MIN_SILENCE, "--model", "base.en"]
    listen_proc = subprocess.Popen(cmd, cwd=HERE, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in listen_proc.stdout:
        m = LINE_RE.match(line.strip())
        if not m:
            if line.strip():
                print("[listen.py]", line.rstrip(), flush=True)   # show errors / status
            continue
        text = m.group(1).strip()
        if not text:
            continue
        with lock:
            echo = state["speaking"] or (time.monotonic() - state["speaking_until"] < ECHO_WINDOW)
        if echo:
            add_log("echo", text)          # probably the car hearing its own voice
            continue
        add_log("driver", text)
        if get_screen() in ("idle", "listening"):
            set_screen("thinking")         # show the driver that the car heard them
    add_log("error", f"listen.py stopped (exit code {listen_proc.wait()})")


@atexit.register
def _cleanup():
    if listen_proc and listen_proc.poll() is None:
        listen_proc.terminate()


# ---------------------------------------------------------------- actions
def emergency_stop(source):
    add_log("button", f"STOP ({source})")
    clear_speech_queue()
    say("Stopped. Do you want me to continue?", start="stopped")


def reset(source):
    add_log("button", f"reset ({source})")
    clear_speech_queue()
    set_screen("idle")


# ---------------------------------------------------------------- screen
try:
    import board, digitalio
    import adafruit_rgb_display.st7789 as st7789
    from PIL import Image, ImageDraw, ImageFont
    HAVE_SCREEN = True
except Exception as e:  # lets the prototype run on a Pi without the screen libraries
    print("Screen not available, running without it:", e)
    HAVE_SCREEN = False

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def screen_loop():
    if not HAVE_SCREEN:
        return
    disp = st7789.ST7789(board.SPI(), cs=digitalio.DigitalInOut(board.D5),
                         dc=digitalio.DigitalInOut(board.D25), rst=None, baudrate=64000000,
                         width=135, height=240, x_offset=53, y_offset=40)
    backlight = digitalio.DigitalInOut(board.D22)
    backlight.switch_to_output()
    backlight.value = True
    btn_a = digitalio.DigitalInOut(board.D23)
    btn_b = digitalio.DigitalInOut(board.D24)
    btn_a.switch_to_input(pull=digitalio.Pull.UP)
    btn_b.switch_to_input(pull=digitalio.Pull.UP)

    W, H = disp.height, disp.width          # 240 x 135 landscape
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    big = ImageFont.truetype(FONT_BOLD, 24)
    mid = ImageFont.truetype(FONT_BOLD, 17)
    small = ImageFont.truetype(FONT, 12)

    def ctext(y, text, font, fill="white"):
        d.text((W // 2, y), text, font=font, fill=fill, anchor="mm")

    def spinner(cx, cy, r, frame, color):
        n = 8
        for i in range(n):
            a = 2 * math.pi * i / n - math.pi / 2
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            k = (frame - i) % n
            s = 6 if k == 0 else 4
            c = color if k < 3 else (80, 80, 80)
            d.ellipse((x - s, y - s, x + s, y + s), fill=c)

    def sound_bars(x, y, frame, color="white"):
        for i in range(4):
            h = 4 + int(8 * abs(math.sin(frame * 0.5 + i)))
            d.rectangle((x + i * 6, y - h, x + i * 6 + 3, y), fill=color)

    prev_a = prev_b = False
    frame = 0
    while True:
        a, b = not btn_a.value, not btn_b.value
        if a and not prev_a:
            emergency_stop("button A")
        if b and not prev_b:
            reset("button B")
        prev_a, prev_b = a, b

        with lock:
            screen = state["screen"]
            t = time.monotonic() - state["changed"]
            speaking = state["speaking"]

        if screen == "idle":
            d.rectangle((0, 0, W, H), fill=(30, 30, 35))
            ctext(50, "Parking Assist", mid)
            ctext(85, 'Just ask me to park', small, (180, 180, 180))
        elif screen == "listening":
            d.rectangle((0, 0, W, H), fill=(15, 40, 90))
            r = 16 + 6 * abs(math.sin(frame * 0.2))
            d.ellipse((W / 2 - r, 50 - r, W / 2 + r, 50 + r), outline=(120, 190, 255), width=3)
            d.ellipse((W / 2 - 8, 42, W / 2 + 8, 58), fill=(120, 190, 255))
            ctext(105, "Listening...", mid)
        elif screen == "thinking":
            d.rectangle((0, 0, W, H), fill=(15, 40, 90))
            spinner(W / 2, 50, 22, frame, (255, 255, 255))
            ctext(105, "Thinking...", mid)
        elif screen == "talking":
            d.rectangle((0, 0, W, H), fill=(15, 40, 90))
            sound_bars(W // 2 - 12, 62, frame)
            ctext(105, "Speaking...", mid)
        elif screen == "checking":
            d.rectangle((0, 0, W, H), fill=(120, 80, 0))
            spinner(W / 2, 48, 22, frame, (255, 220, 120))
            ctext(100, "Checking safety...", mid)
            ctext(122, "Looking around the car", small, (255, 230, 180))
        elif screen == "clear":
            d.rectangle((0, 0, W, H), fill=(20, 110, 50))
            d.line((W / 2 - 22, 48, W / 2 - 6, 64, W / 2 + 24, 30), fill="white", width=7)
            ctext(100, "All clear", big)
        elif screen == "parking":
            d.rectangle((0, 0, W, H), fill=(15, 40, 90))
            ctext(30, "Parking...", big)
            p = min(t / 10.0, 1.0)                     # fills over ~10 seconds
            d.rectangle((20, 60, W - 20, 78), outline="white", width=2)
            d.rectangle((23, 63, 23 + (W - 46) * p, 75), fill=(120, 190, 255))
            ctext(110, "Press top button to STOP", small, (200, 200, 200))
        elif screen == "parked":
            d.rectangle((0, 0, W, H), fill=(20, 110, 50))
            ctext(50, "Parked", big)
            ctext(90, "Don't forget your bag!", small)
        elif screen == "stopped":
            flash = (frame // 5) % 2 == 0
            d.rectangle((0, 0, W, H), fill=(170, 20, 20) if flash else (120, 10, 10))
            ctext(55, "STOPPED", big)
            ctext(95, "Say 'continue' or 'cancel'", small)

        if speaking and screen != "talking":
            sound_bars(W - 30, H - 6, frame)          # small "I'm talking" indicator

        disp.image(img, 90)
        frame += 1
        time.sleep(0.08)


# ---------------------------------------------------------------- wizard web page
app = Flask(__name__)
logging.getLogger("werkzeug").setLevel(logging.ERROR)


@app.route("/")
def index():
    return Response(CONTROLLER_HTML, mimetype="text/html")


@app.route("/api/log")
def api_log():
    since = int(request.args.get("since", 0))
    with lock:
        return jsonify({"entries": log[since:], "next": len(log),
                        "screen": state["screen"], "speaking": state["speaking"]})


@app.route("/api/say", methods=["POST"])
def api_say():
    data = request.get_json(force=True)
    text = (data.get("text") or "").strip()
    if text:
        say(text, data.get("start"), data.get("after"))
    return jsonify(ok=True)


@app.route("/api/screen", methods=["POST"])
def api_screen():
    set_screen(request.get_json(force=True)["name"])
    return jsonify(ok=True)


@app.route("/api/stop", methods=["POST"])
def api_stop():
    emergency_stop("wizard")
    return jsonify(ok=True)


@app.route("/api/reset", methods=["POST"])
def api_reset():
    reset("wizard")
    return jsonify(ok=True)


CONTROLLER_HTML = r"""<!doctype html>
<html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parking Wizard</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;padding:12px;background:#111;color:#eee;max-width:900px;margin:auto}
 h2{font-size:15px;color:#aaa;margin:16px 0 6px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:8px}
 button{font-size:14px;padding:10px;border:0;border-radius:8px;background:#2a3b5c;color:#fff;text-align:left;cursor:pointer}
 button:active{transform:scale(.97)}
 .scr button{background:#333;text-align:center}
 .stop{background:#b01818!important;font-weight:bold;text-align:center}
 #log{background:#000;border-radius:8px;padding:8px;height:260px;overflow-y:auto;font-size:14px}
 .driver{color:#7cf;font-weight:bold} .car{color:#8e8} .echo{color:#555} .screen,.button{color:#c90;font-size:12px}
 #free{width:100%;box-sizing:border-box;font-size:15px;padding:10px;border-radius:8px;border:0;margin-bottom:6px}
 #status{font-size:13px;color:#aaa}
</style></head><body>
<div id="status">screen: -</div>
<h2>What the driver said</h2>
<div id="log"></div>

<h2>Car says (script)</h2>
<div class="grid" id="presets"></div>

<h2>Free text</h2>
<input id="free" placeholder="Type anything and press Enter">
<button onclick="sayFree()" style="width:100%;text-align:center">Speak</button>

<h2>Screen</h2>
<div class="grid scr">
 <button onclick="scr('idle')">Idle</button>
 <button onclick="scr('listening')">Listening</button>
 <button onclick="scr('thinking')">Thinking</button>
 <button onclick="scr('checking')">Checking safety</button>
 <button onclick="scr('clear')">All clear</button>
 <button onclick="scr('parking')">Parking</button>
 <button onclick="scr('parked')">Parked</button>
 <button class="stop" onclick="post('/api/stop',{})">STOP</button>
 <button onclick="post('/api/reset',{})">Reset session</button>
</div>

<script>
const PRESETS = [
 ["Greet", "Hi, I'm your parking assistant. Just tell me when you'd like to park.", null],
 ["Propose LEFT", "Sure. The spot on your left is open and close to the entrance. Shall I park there?", null],
 ["Offer RIGHT", "No problem. There is also an open spot on your right. Would you like that one?", null],
 ["Check safety", "Okay. Let me check the area for safety.", "checking"],
 ["All clear LEFT + confirm", "All clear. Ready to park on the left. Should I start?", "clear"],
 ["All clear RIGHT + confirm", "All clear. Ready to park on the right. Should I start?", "clear"],
 ["Start parking", "Parking now. Say stop anytime.", "parking"],
 ["Parked", "Parked. Don't forget your bag.", "parked"],
 ["Say again", "Sorry, could you say that again?", null],
 ["Continue?", "Stopped. Do you want me to continue?", "stopped"],
];
const box = document.getElementById('presets');
PRESETS.forEach(([label, text, start]) => {
  const b = document.createElement('button');
  b.innerHTML = '<b>' + label + '</b><br><small>' + text + '</small>';
  b.onclick = () => post('/api/say', {text, start});
  box.appendChild(b);
});
function post(url, body){ return fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}); }
function scr(name){ post('/api/screen',{name}); }
function sayFree(){ const f=document.getElementById('free'); if(f.value.trim()){ post('/api/say',{text:f.value}); f.value=''; } }
document.getElementById('free').addEventListener('keydown', e => { if(e.key==='Enter') sayFree(); });

let next = 0;
async function poll(){
  try{
    const r = await (await fetch('/api/log?since='+next)).json();
    next = r.next;
    const log = document.getElementById('log');
    r.entries.forEach(e => {
      const d = document.createElement('div');
      d.className = e.kind;
      const who = {driver:'DRIVER', car:'CAR', echo:'(echo)', screen:'screen →', button:'button'}[e.kind] || e.kind;
      d.textContent = e.time + '  ' + who + '  ' + e.text;
      log.appendChild(d);
    });
    if(r.entries.length) log.scrollTop = log.scrollHeight;
    document.getElementById('status').textContent = 'screen: ' + r.screen + (r.speaking ? '  🔊 speaking' : '');
  }catch(e){}
  setTimeout(poll, 700);
}
poll();
</script></body></html>"""


# ---------------------------------------------------------------- main
if __name__ == "__main__":
    add_log("session", "start")
    threading.Thread(target=speech_worker, daemon=True).start()
    threading.Thread(target=listener, daemon=True).start()
    threading.Thread(target=screen_loop, daemon=True).start()
    print("Wizard controller: http://ras-yuri.local:5000", flush=True)
    app.run(host="0.0.0.0", port=5000, threaded=True, use_reloader=False)
