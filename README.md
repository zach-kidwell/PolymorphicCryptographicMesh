# Polymorphic Cryptographic Mesh

This is a simple proof-of-concept AI module for a Quantum AI course project.

The app demonstrates this pipeline:

```text
Security Data -> Feature Extraction -> AI Model -> Risk Prediction -> Encryption Recommendation
```

The model learns from example security cases. It uses a small in-code dataset with features such as algorithm age, vulnerability count, quantum threat level, and data sensitivity level.

In a real system, the dataset would come from cybersecurity reports, cryptographic standards, and quantum computing progress estimates.

This module represents the AI decision-making part of the Polymorphic Cryptographic Mesh.

## What It Does

- Trains a scikit-learn `DecisionTreeClassifier`.
- Predicts whether an encryption method is low, medium, or high risk.
- Recommends whether to keep or replace the encryption method.
- Suggests replacements such as Kyber, AES-256, SPHINCS+, or Dilithium.
- Provides a small web interface that can run locally or on Render.

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
python main.py
```

Open the local web app:

```text
http://localhost:5000
```

When `main.py` starts, it also prints example predictions in the terminal.

## Example Output

```text
Algorithm: RSA-2048
Age: 14 years
Vulnerabilities: 6
Quantum Threat Level: 8
Data Sensitivity: 9

AI Risk Prediction: High Risk
Recommendation: Replace Encryption
Suggested Replacement: Kyber + AES-256 hybrid encryption
```

## Deploy on Render

Create a new Render Web Service from this GitHub repository.

Use these settings:

```text
Environment: Python
Build Command: pip install -r requirements.txt
Start Command: gunicorn main:app
```

The included `Procfile` also tells Render to start the app with:

```text
web: gunicorn main:app
```
