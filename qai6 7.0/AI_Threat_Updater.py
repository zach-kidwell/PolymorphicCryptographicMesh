import json
import os
import numpy as np
from sklearn.tree import DecisionTreeClassifier

THREAT_FILE = "quantum_threat_data.json"

# ============================================================
# === LOAD + SAVE THREAT DATA
# ============================================================

def load_threat_data():
    if not os.path.exists(THREAT_FILE):
        raise FileNotFoundError(f"{THREAT_FILE} not found.")
    with open(THREAT_FILE, "r") as f:
        return json.load(f)

def save_threat_data(data):
    with open(THREAT_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================================================
# === FEATURE ENCODING
# ============================================================

STATUS_MAP = {
    "Broken": 0,
    "Deprecated": 1,
    "Safe": 2,
    "Finalist": 3,
    "Other": 4
}

RISK_MAP = {
    "High Risk": 1,
    "Low Risk": 0
}

RISK_MAP_REV = {v: k for k, v in RISK_MAP.items()}


def encode_features(entry):
    return [
        entry["security_level"],
        entry["quantum_cost"],
        STATUS_MAP.get(entry["status"], STATUS_MAP["Other"])
    ]


# ============================================================
# === QUANTUM AUTO-DECAY MODEL
# ============================================================

def quantum_decay(entry):
    """
    Apply decay based on quantum algorithm pressure.
    Higher quantum_cost = more vulnerable to Grover/Shor.
    Lower security_level = faster decay.
    Status also influences decay.
    """

    base = 0.0

    # Quantum cost pressure (Grover/Shor)
    base += entry["quantum_cost"] * 0.15

    # Low security level decays faster
    base += (5 - entry["security_level"]) * 0.10

    # Status decay
    status = entry["status"]
    if status == "Broken":
        base += 0.50
    elif status == "Deprecated":
        base += 0.30
    elif status == "Safe":
        base += 0.05
    elif status == "Finalist":
        base += 0.02

    # Clamp decay between 0 and 1
    return min(max(base, 0.0), 1.0)


# ============================================================
# === AI THREAT MODEL
# ============================================================

class ThreatAI:
    """
    AI that learns risk classification from threat data,
    applies quantum auto-decay, and updates the JSON file.
    """

    def __init__(self):
        self.data = load_threat_data()
        self.model = DecisionTreeClassifier(max_depth=4, random_state=42)

    def train(self):
        X = [encode_features(entry) for entry in self.data]
        y = [RISK_MAP[entry["risk"]] for entry in self.data]

        self.model.fit(X, y)
        print("[AI] Training complete. Model learned threat patterns.")

    def predict_risk(self, entry):
        features = np.array(encode_features(entry)).reshape(1, -1)
        pred = self.model.predict(features)[0]
        return RISK_MAP_REV[pred]

    def apply_decay(self, entry):
        """
        Combine AI prediction + quantum decay to produce final risk.
        """
        ai_risk = self.predict_risk(entry)
        decay_factor = quantum_decay(entry)

        # Convert to numeric
        ai_numeric = RISK_MAP[ai_risk]

        # Apply decay: if decay is high, push toward High Risk
        final_numeric = ai_numeric + decay_factor

        # Threshold
        final_risk = "High Risk" if final_numeric >= 0.5 else "Low Risk"

        return final_risk, decay_factor

    def update_all(self):
        """
        Apply decay to all existing entries and update JSON.
        """
        for entry in self.data:
            final_risk, decay = self.apply_decay(entry)
            entry["risk"] = final_risk
            entry["decay_factor"] = round(decay, 3)
            print(f"[AI] {entry['algorithm']} → {final_risk} (decay={decay:.3f})")

        save_threat_data(self.data)
        print("[AI] quantum_threat_data.json updated with decay-adjusted risks.")


# ============================================================
# === MAIN
# ============================================================

if __name__ == "__main__":
    ai = ThreatAI()
    ai.train()
    ai.update_all()
