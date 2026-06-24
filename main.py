import os

from flask import Flask, render_template, request
from sklearn.tree import DecisionTreeClassifier


app = Flask(__name__)


# Training examples for the proof-of-concept model.
# Each row represents a simplified security case.
TRAINING_DATA = [
    {"algorithm": "RSA-2048", "age": 14, "vulnerabilities": 6, "quantum_threat": 8, "sensitivity": 9, "risk": "High Risk"},
    {"algorithm": "RSA-2048", "age": 12, "vulnerabilities": 4, "quantum_threat": 7, "sensitivity": 8, "risk": "High Risk"},
    {"algorithm": "ECC-256", "age": 11, "vulnerabilities": 5, "quantum_threat": 8, "sensitivity": 8, "risk": "High Risk"},
    {"algorithm": "ECC-256", "age": 9, "vulnerabilities": 3, "quantum_threat": 7, "sensitivity": 7, "risk": "Medium Risk"},
    {"algorithm": "AES-256", "age": 22, "vulnerabilities": 1, "quantum_threat": 4, "sensitivity": 9, "risk": "Low Risk"},
    {"algorithm": "AES-256", "age": 20, "vulnerabilities": 2, "quantum_threat": 5, "sensitivity": 8, "risk": "Medium Risk"},
    {"algorithm": "Kyber", "age": 3, "vulnerabilities": 1, "quantum_threat": 8, "sensitivity": 9, "risk": "Low Risk"},
    {"algorithm": "Kyber", "age": 2, "vulnerabilities": 0, "quantum_threat": 9, "sensitivity": 8, "risk": "Low Risk"},
    {"algorithm": "Dilithium", "age": 3, "vulnerabilities": 1, "quantum_threat": 8, "sensitivity": 8, "risk": "Low Risk"},
    {"algorithm": "Dilithium", "age": 2, "vulnerabilities": 0, "quantum_threat": 9, "sensitivity": 9, "risk": "Low Risk"},
    {"algorithm": "SPHINCS+", "age": 4, "vulnerabilities": 1, "quantum_threat": 8, "sensitivity": 7, "risk": "Low Risk"},
    {"algorithm": "3DES", "age": 25, "vulnerabilities": 8, "quantum_threat": 5, "sensitivity": 8, "risk": "High Risk"},
]


RISK_LEVELS = {
    "Low Risk": 1,
    "Medium Risk": 2,
    "High Risk": 3,
}


def algorithm_features(algorithm_name):
    """Turn an algorithm name into simple numeric features."""
    name = algorithm_name.lower()

    is_asymmetric = int("rsa" in name or "ecc" in name)
    is_symmetric = int("aes" in name or "3des" in name)
    is_post_quantum = int("kyber" in name or "dilithium" in name or "sphincs" in name)
    is_signature = int("dilithium" in name or "sphincs" in name)

    return [is_asymmetric, is_symmetric, is_post_quantum, is_signature]


def make_features(case):
    """Build the model input features from one security case."""
    return [
        case["age"],
        case["vulnerabilities"],
        case["quantum_threat"],
        case["sensitivity"],
        *algorithm_features(case["algorithm"]),
    ]


def train_model():
    """Train a small explainable decision tree using the example data."""
    x_train = [make_features(case) for case in TRAINING_DATA]
    y_train = [case["risk"] for case in TRAINING_DATA]

    model = DecisionTreeClassifier(max_depth=4, random_state=42)
    model.fit(x_train, y_train)
    return model


MODEL = train_model()


def recommend_replacement(algorithm, risk_label, quantum_threat, sensitivity):
    """Choose a simple encryption recommendation based on the prediction."""
    name = algorithm.lower()

    if risk_label == "Low Risk":
        return "Keep Encryption", "No replacement needed"

    if "rsa" in name or "ecc" in name:
        return "Replace Encryption", "Kyber + AES-256 hybrid encryption"

    if "3des" in name:
        return "Replace Encryption", "AES-256"

    if "aes" in name and quantum_threat >= 7 and sensitivity >= 8:
        return "Replace Encryption", "Kyber + AES-256 hybrid encryption"

    if "dilithium" in name or "sphincs" in name:
        return "Keep Encryption", "Dilithium or SPHINCS+ for post-quantum signatures"

    if sensitivity >= 8:
        return "Replace Encryption", "Kyber + AES-256 hybrid encryption"

    return "Replace Encryption", "AES-256"


def predict_case(algorithm, age, vulnerabilities, quantum_threat, sensitivity):
    """Run feature extraction, risk prediction, and recommendation."""
    case = {
        "algorithm": algorithm,
        "age": int(age),
        "vulnerabilities": int(vulnerabilities),
        "quantum_threat": int(quantum_threat),
        "sensitivity": int(sensitivity),
    }

    features = [make_features(case)]
    risk_label = str(MODEL.predict(features)[0])
    confidence = max(MODEL.predict_proba(features)[0])
    recommendation, replacement = recommend_replacement(
        algorithm,
        risk_label,
        case["quantum_threat"],
        case["sensitivity"],
    )

    return {
        **case,
        "risk_label": risk_label,
        "risk_score": RISK_LEVELS[risk_label],
        "confidence": round(confidence * 100),
        "recommendation": recommendation,
        "replacement": replacement,
    }


def print_demo_results():
    """Print a few example predictions in the terminal."""
    demo_cases = [
        ("RSA-2048", 14, 6, 8, 9),
        ("ECC-256", 10, 4, 8, 8),
        ("AES-256", 22, 1, 4, 9),
        ("Kyber", 3, 1, 9, 9),
        ("Dilithium", 3, 1, 8, 8),
    ]

    print("\nPolymorphic Cryptographic Mesh - AI Risk Demo")
    print("Security Data -> Feature Extraction -> AI Model -> Risk Prediction -> Encryption Recommendation")
    print("-" * 80)

    for demo in demo_cases:
        result = predict_case(*demo)
        print(f"Algorithm: {result['algorithm']}")
        print(f"Age: {result['age']} years")
        print(f"Vulnerabilities: {result['vulnerabilities']}")
        print(f"Quantum Threat Level: {result['quantum_threat']}")
        print(f"Data Sensitivity: {result['sensitivity']}")
        print(f"AI Risk Prediction: {result['risk_label']} (score {result['risk_score']}/3)")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Suggested Replacement: {result['replacement']}")
        print("-" * 80)


@app.route("/", methods=["GET", "POST"])
def index():
    """Render the form and show the prediction result."""
    result = None
    form_values = {
        "algorithm": "RSA-2048",
        "age": 14,
        "vulnerabilities": 6,
        "quantum_threat": 8,
        "sensitivity": 9,
    }

    if request.method == "POST":
        form_values = {
            "algorithm": request.form.get("algorithm", "RSA-2048"),
            "age": request.form.get("age", 0),
            "vulnerabilities": request.form.get("vulnerabilities", 0),
            "quantum_threat": request.form.get("quantum_threat", 0),
            "sensitivity": request.form.get("sensitivity", 0),
        }
        result = predict_case(**form_values)

    return render_template("index.html", result=result, form_values=form_values)


if __name__ == "__main__":
    print_demo_results()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
