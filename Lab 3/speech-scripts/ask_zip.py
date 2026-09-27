import os, re, subprocess, sys, datetime
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
VOICES = os.path.join(HERE, "..", "voices")
VOICE = "en_US-lessac-medium"

def speak(text):
    # Piper で喋る（課題Aと同じ方法）
    piper = subprocess.Popen(
        [sys.executable, "-m", "piper", "--model", VOICE, "--data-dir", VOICES,
         "--output-raw", "--", text],
        stdout=subprocess.PIPE)
    subprocess.run(["aplay", "-q", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-"],
                   stdin=piper.stdout)
    piper.wait()

def record(path, seconds=5):
    # マイクで録音する
    subprocess.run(["arecord", "-q", "-d", str(seconds), "-f", "S16_LE",
                    "-c", "1", "-r", "16000", path])

print("Loading model...")
model = WhisperModel("base.en", compute_type="int8")

speak("Hi! What is your zip code?")
print("Listening... (5 seconds)")
record("answer.wav")

segments, _ = model.transcribe("answer.wav")
text = " ".join(s.text for s in segments).strip()
digits = re.sub(r"\D", "", text)   # 数字だけ取り出す

print("Heard :", text)
print("Digits:", digits)

if digits:
    speak("I heard " + " ".join(digits) + ". Thank you!")
else:
    speak("Sorry, I did not catch a number.")

with open("zip_answers.txt", "a") as f:
    f.write(f"{datetime.datetime.now()}\t{text}\t{digits}\n")
print("Saved to zip_answers.txt")