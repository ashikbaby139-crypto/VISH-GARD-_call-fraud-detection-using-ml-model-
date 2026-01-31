from flask import Flask, render_template, jsonify, request
from predictor import predict_fraud_hybrid
from phone_checker import check_phone_number

import stt_vosk
import os
import json

LOG_FILE = "transcripts.log"

app = Flask(__name__)

# ---------- GLOBAL STATE ----------
fraud_saved = False   # 🔒 prevents duplicate evidence

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("home.html")

# ---------- AUDIO PAGE ----------
@app.route("/audio")
def audio_page():
    return render_template("audio.html")
#-----------phone number page------

@app.route("/number")
def number_page():
    return render_template("number.html")


# ---------- LIVE LISTEN ----------
@app.route("/listen")
def listen_route():
    global fraud_saved

    # ✅ CORRECT CALL
    text = stt_vosk.get_live_text()

    if not text:
        return jsonify({
            "text": "",
            "result": "",
            "confidence": "",
            "keywords": []
        })

    decision, confidence, keywords = predict_fraud_hybrid(text)

    result = "🚨 Scam Detected" if decision == 0 else "✅ No Scam"

    # 🔒 SAVE ONLY ONCE PER CALL
    if decision == 0 and not fraud_saved:
        stt_vosk.save_transcript_to_file(
            text=text,
            decision=decision,
            confidence=confidence,
            keywords=keywords
        )
        fraud_saved = True

    return jsonify({
        "text": text,
        "result": result,
        "confidence": f"{confidence} %",
        "keywords": keywords
    })

# ---------- RESET ----------
@app.route("/reset")
def reset():
    global fraud_saved
    fraud_saved = False

    # ✅ RESET MODULE STATE CORRECTLY
    stt_vosk.live_final = ""
    stt_vosk.live_partial = ""

    return jsonify({"status": "reset"})

# ---------- TEXT PAGE ----------
@app.route("/text")
def text_page():
    return render_template("text.html")

# ---------- TEXT ANALYSIS ----------
@app.route("/analyze_text", methods=["POST"])
def analyze_text():
    text = request.json.get("text", "").strip()

    decision, confidence, keywords = predict_fraud_hybrid(text)

    if decision == 0:
        stt_vosk.save_transcript_to_file(
            text=text,
            decision=decision,
            confidence=confidence,
            keywords=keywords
        )

    return jsonify({
        "text": text,
        "result": "🚨 Scam Detected" if decision == 0 else "✅ No Scam",
        "confidence": f"{confidence} %",
        "keywords": keywords
    })

# ---------- LOG PAGE ----------
@app.route("/logs")
def logs_page():
    logs = []

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except:
                    pass

    return render_template("logs.html", logs=logs)

# ---------- DELETE SINGLE LOG ----------
@app.route("/delete_log", methods=["POST"])
def delete_log():
    index = int(request.json["index"])

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if 0 <= index < len(lines):
        lines.pop(index)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return jsonify({"status": "deleted"})

# ---------- CLEAR ALL LOGS ----------
@app.route("/clear_logs", methods=["POST"])
def clear_logs():
    open(LOG_FILE, "w").close()
    return jsonify({"status": "cleared"})

#---------phone number checking--------

@app.route("/check_number", methods=["POST"])
def check_number():
    number = request.json.get("number", "").strip()

    if not number:
        return jsonify({"error": "No number provided"})

    result = check_phone_number(number)
    return jsonify(result)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)
