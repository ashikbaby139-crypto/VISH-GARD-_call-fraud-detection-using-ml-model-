import os
import json
import threading
import pyaudio
from vosk import Model, KaldiRecognizer


LOG_FILE = "transcripts.log"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "vosk-model-small-en-us")

model = Model(MODEL_PATH)

p = pyaudio.PyAudio()

recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)

# 🔴 GLOBAL TRANSCRIPTION STATE
live_partial = ""
live_final = ""

def audio_loop():
    global live_partial, live_final

    stream = p.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=4000
    )

    stream.start_stream()

    while True:
        data = stream.read(4000, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "").strip()
            if text:
                live_final += " " + text
                live_partial = ""
        else:
            partial = json.loads(recognizer.PartialResult())
            live_partial = partial.get("partial", "")

# 🚀 Start microphone listener ONCE
threading.Thread(target=audio_loop, daemon=True).start()

def get_live_text():
    return (live_final + " " + live_partial).strip()
from datetime import datetime
# save  as .log file



def save_transcript_to_file(text, decision, confidence, keywords):
    if decision != 0:
        return  # only save fraud

    entry = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "text": text.strip(),
        "confidence": confidence,
        "keywords": keywords
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

