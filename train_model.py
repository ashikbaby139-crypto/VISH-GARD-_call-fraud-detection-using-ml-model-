import pandas as pd
import string
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import BernoulliNB

# ---------- Load dataset ----------
df = pd.read_csv(
    "SMSSpamCollection.csv",
    sep="\t",
    header=None,
    names=["label", "text"]
)

df = df.dropna(subset=["label", "text"])

# ---------- Normalize labels ----------
df["label"] = df["label"].str.lower().str.strip()
df["label"] = df["label"].map({
    "spam": 0,
    "fraud": 0,
    "scam": 0,
    "ham": 1,
    "normal": 1
})

df = df.dropna(subset=["label"])
df["label"] = df["label"].astype(int)

# ---------- Preprocessing ----------
STOPWORDS = set(stopwords.words("english"))

def preprocess(text):
    if not isinstance(text, str):
        return ""
    text = "".join(c for c in text if c not in string.punctuation)
    words = [w for w in text.split() if w.lower() not in STOPWORDS]
    return " ".join(words)

df["clean"] = df["text"].apply(preprocess)

# ---------- Vectorization ----------
tfidf = TfidfVectorizer()
X = tfidf.fit_transform(df["clean"])
y = df["label"]

# ---------- Train ----------
model = BernoulliNB()
model.fit(X, y)

# ---------- Save ----------
pickle.dump(tfidf, open("vectorizer.pkl", "wb"))
pickle.dump(model, open("model.pkl", "wb"))

print("✅ Model trained and saved successfully")
print(f"📊 Samples used: {len(df)}")
print(df["label"].value_counts())
