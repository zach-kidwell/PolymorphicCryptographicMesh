# Polymorphic Cryptographic Mesh

An educational prototype exploring adaptive cryptography, quantum-threat classification, weighted mesh routing, and per-hop key mutation.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2Fzach-kidwell%2FPolymorphicCryptographicMesh)

## Interactive classroom demo

The browser demo turns the research prototype into a short, visual lesson:

1. A decision-tree classifier assesses the selected cryptographic algorithm.
2. Lower-risk algorithms use the simple secure channel.
3. Algorithms exposed to quantum attacks activate layered mesh protection.
4. The encryption key mutates at every logical relay before the recipient recovers the message.

The visualization uses Alice and Bob as sender and recipient. Nodes A–H are logical security relays, not geographic locations.

> **Educational scope:** This is a conceptual simulator, not a production security system. Quantum-inspired routing does not itself guarantee quantum security.

## Run the demo locally

From the repository root:

```powershell
cd "qai6 7.0/web_demo"
py -3 server.py
```

Then open <http://127.0.0.1:4173/>.

The demo is dependency-free. You can also open `qai6 7.0/web_demo/index.html` directly in a browser.

## Deploy with a Render Blueprint

Click **Deploy to Render** above, or:

1. Open the Render Dashboard and choose **New → Blueprint**.
2. Connect `zach-kidwell/PolymorphicCryptographicMesh`.
3. Render will detect the root-level `render.yaml` file.
4. Review the static-site service and select **Apply**.

The Blueprint publishes `qai6 7.0/web_demo` as a static site and automatically redeploys when the linked branch receives a commit.

## Research prototype

The Python implementation in `qai6 7.0` includes:

- a Qiskit/Aer quantum random-bit generator;
- a decision-tree quantum-threat classifier;
- Grover-inspired weighted route selection;
- a polymorphic XOR cipher with per-hop mutations;
- a classical RSA fallback channel; and
- NetworkX/Matplotlib mesh visualizations.

## Project layout

```text
render.yaml                 Render Blueprint
qai6 7.0/
├── PCM.py                  Main cryptographic mesh prototype
├── quantum_threat_data.json
├── mesh_animation.py
└── web_demo/
    ├── index.html
    ├── qmesh-lab.css
    ├── app.js
    └── server.py
```
