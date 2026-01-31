import re

FRAUD_FILE = "fraud_numbers.txt"

# ---------- Normalize FIRST ----------
def normalize_number(number):
    return re.sub(r"\D", "", number)

# ---------- Load fraud numbers ----------
def load_fraud_numbers():
    try:
        with open(FRAUD_FILE, "r", encoding="utf-8") as f:
            return set(
                normalize_number(line.strip())
                for line in f
                if line.strip()
            )
    except FileNotFoundError:
        return set()

# ✅ NOW SAFE
FRAUD_NUMBERS = load_fraud_numbers()

# ---------- Known suspicious prefixes ----------
SUSPICIOUS_PREFIXES = [
    "140",
    "160",
    "1800",
    "999",
    "888"
]

# ---------- Main check ----------
def check_phone_number(number):
    score = 0
    reasons = []

    num = normalize_number(number)

    # 🔴 Blacklist check
    if num in FRAUD_NUMBERS:
        return {
            "number": number,
            "status": "🚨 Fraud / Spam (Blacklisted)",
            "confidence": 100,
            "reasons": ["Number found in fraud database"]
        }

    # Length checks
    if len(num) < 10:
        score += 40
        reasons.append("Too short")

    if len(num) > 13:
        score += 30
        reasons.append("Too long")

    # Repeated digits
    if re.fullmatch(r"(\d)\1{6,}", num):
        score += 50
        reasons.append("Repeated digits pattern")

    # Prefix checks
    for p in SUSPICIOUS_PREFIXES:
        if num.startswith(p):
            score += 30
            reasons.append(f"Suspicious prefix: {p}")
            break

    # Invalid start
    if num and num[0] in ["0", "1"]:
        score += 20
        reasons.append("Invalid starting digit")

    # Final decision
    if score >= 60:
        status = "🚨 Fraud / Spam"
    elif score >= 30:
        status = "⚠️ Suspicious"
    else:
        status = "✅ Likely Legitimate"

    confidence = min(score + 20, 100)

    return {
        "number": number,
        "status": status,
        "confidence": confidence,
        "reasons": reasons
    }
