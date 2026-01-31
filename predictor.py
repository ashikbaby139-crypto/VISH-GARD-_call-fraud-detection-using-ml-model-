import pickle
import string
from nltk.corpus import stopwords
import os

# ---------- Load trained artifacts ----------
with open("vectorizer.pkl", "rb") as f:
    tfidf = pickle.load(f)

with open("model.pkl", "rb") as f:
    model = pickle.load(f)

STOPWORDS = set(stopwords.words("english"))

# ---------- Load Fraud Keywords from File ----------
def load_keywords(file_name="fraud_keywords.txt"):
    keywords = []
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            kw = line.strip().lower()
            if kw:
                keywords.append(kw)

    return keywords

FRAUD_KEYWORDS = load_keywords()

# ---------- Text Preprocessing ----------
def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = "".join(c for c in text if c not in string.punctuation)
    words = [w for w in text.split() if w.lower() not in STOPWORDS]
    return " ".join(words)

# ---------- ROBUST Keyword Detection ----------
def keyword_score(text):
    text_norm = text.lower().replace(" ", "")
    found = []

    for kw in FRAUD_KEYWORDS:
        kw_norm = kw.replace(" ", "")
        if kw_norm in text_norm:
            found.append(kw)

    return len(found), found

# ---------- FINAL HYBRID PREDICTION ----------
def predict_fraud_hybrid(text):
    X = tfidf.transform([preprocess(text)])
    proba = model.predict_proba(X)[0]   # [fraud, normal]
    ml_confidence = proba[0] * 100

    kw_count, found_keywords = keyword_score(text)

    # 🚨 Force fraud if OTP detected (real-world rule)
    if "otp" in found_keywords:
        return 0, 100.0, found_keywords

    # Strong keyword boosting
    final_confidence = ml_confidence + (kw_count * 20)
    final_confidence = min(final_confidence, 100)

    # Lower threshold for voice fraud
    if final_confidence >= 40:
        decision = 0   # Fraud
    else:
        decision = 1   # Safe

    return decision, round(final_confidence, 2), found_keywords
