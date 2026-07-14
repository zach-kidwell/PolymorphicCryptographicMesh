import os
import json
import random
import math
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import networkx as nx

from mesh_animation import animate_transition

# ============================================================
# === LOAD UPDATED QUANTUM THREAT DATA (NIST PQC STYLE)
# ============================================================

def load_threat_data(path="quantum_threat_data.json"):
    if not os.path.exists(path):
        raise FileNotFoundError("quantum_threat_data.json not found.")
    with open(path, "r") as f:
        return json.load(f)

THREAT_DATA = load_threat_data()

def make_features(case):
    return [
        case["security_level"],
        case["quantum_cost"],
        int(case["status"] == "Broken"),
        int(case["status"] == "Deprecated"),
        int(case["status"] == "Finalist"),
    ]

def train_model():
    x_train = [make_features(c) for c in THREAT_DATA]
    y_train = [c["risk"] for c in THREAT_DATA]
    model = DecisionTreeClassifier(max_depth=3, random_state=42)
    model.fit(x_train, y_train)
    return model

MODEL = train_model()

def predict_risk(algorithm):
    for entry in THREAT_DATA:
        if entry["algorithm"].lower() == algorithm.lower():
            features = [make_features(entry)]
            return MODEL.predict(features)[0]
    return "Unknown"


# ============================================================
# === QUANTUM THREAT CLASSIFIER (QSVM-STYLE STUB)
# ============================================================

class QuantumThreatClassifier:
    """
    Stub: conceptually a QSVM; here we reuse the classical model
    but keep the interface quantum-flavored.
    """
    def __init__(self, model, data):
        self.model = model
        self.data = data

    def classify_algorithm(self, algorithm):
        return predict_risk(algorithm)


# ============================================================
# === QUANTUM RANDOM + ENTROPY AMPLIFICATION
# ============================================================

class QuantumRandom:
    def __init__(self):
        self.backend = AerSimulator()

    def random_bits(self, n_bits):
        qc = QuantumCircuit(n_bits, n_bits)
        qc.h(range(n_bits))
        qc.measure(range(n_bits), range(n_bits))
        job = self.backend.run(qc, shots=1)
        result = job.result().get_counts()
        bitstring = list(result.keys())[0]
        return bitstring[::-1]

    def random_bytes(self, n_bytes):
        bits = self.random_bits(n_bytes * 8)
        out = bytearray()
        for i in range(0, len(bits), 8):
            out.append(int(bits[i:i+8], 2))
        return bytes(out)

    def amplified_random_bytes(self, n_bytes):
        n_qubits = n_bytes * 2
        qc = QuantumCircuit(n_qubits, n_qubits)

        for i in range(0, n_qubits, 2):
            qc.h(i)
            qc.cx(i, i+1)

        qc.measure(range(n_qubits), range(n_qubits))
        job = self.backend.run(qc, shots=1)
        result = job.result().get_counts()
        bitstring = list(result.keys())[0][::-1]

        out = bytearray()
        for i in range(0, len(bitstring), 8):
            out.append(int(bitstring[i:i+8], 2))

        while len(out) < n_bytes:
            out.extend(self.random_bytes(1))

        return bytes(out[:n_bytes])


# ============================================================
# === QUANTUM GROVER + AMPLITUDE AMPLIFICATION + WALKS
# ============================================================

class QuantumGroverRouter:
    def __init__(self):
        self.backend = AerSimulator(method="statevector")

    def _oracle(self, n_qubits, good_index):
        oracle = QuantumCircuit(n_qubits)
        bitstring = format(good_index, f"0{n_qubits}b")
        for i, bit in enumerate(reversed(bitstring)):
            if bit == "0":
                oracle.x(i)
        oracle.h(n_qubits - 1)
        oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        oracle.h(n_qubits - 1)
        for i, bit in enumerate(reversed(bitstring)):
            if bit == "0":
                oracle.x(i)
        return oracle

    def _diffusion(self, n_qubits):
        qc = QuantumCircuit(n_qubits)
        qc.h(range(n_qubits))
        qc.x(range(n_qubits))
        qc.h(n_qubits - 1)
        qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)
        qc.h(n_qubits - 1)
        qc.x(range(n_qubits))
        qc.h(range(n_qubits))
        return qc

    def grover_search(self, num_items, good_index):
        n_qubits = math.ceil(math.log2(num_items))
        qc = QuantumCircuit(n_qubits)
        qc.h(range(n_qubits))
        qc.compose(self._oracle(n_qubits, good_index), inplace=True)
        qc.compose(self._diffusion(n_qubits), inplace=True)
        qc.save_statevector()
        job = self.backend.run(qc)
        state = np.asarray(job.result().get_statevector())
        probs = np.abs(state) ** 2
        return int(np.argmax(probs))

    def amplitude_amplification(self, costs):
        # Conceptual: pick argmin(costs) as "amplified" best
        return int(np.argmin(costs))

    def choose_best_path_index(self, path_costs):
        return self.amplitude_amplification(path_costs)

    def quantum_walk_step(self, current_node, neighbors):
        """
        Quantum walk step: keep slight bias but allow variance.
        """
        if len(neighbors) == 1:
            return neighbors[0]
        weights = [0.6] + [0.4/(len(neighbors)-1)]*(len(neighbors)-1)
        return random.choices(neighbors, weights=weights)[0]


# ============================================================
# === RANDOM MESH GENERATION (SPARSE BUT CONNECTED, WITH WEIGHTS)
# ============================================================

class MeshNode:
    def __init__(self, name):
        self.name = name

def generate_random_mesh(min_nodes=4, max_nodes=10):
    """
    Generate a sparse, connected mesh:
    - Start with a random spanning tree (guarantees connectivity).
    - Add a few extra random edges with low probability.
    - Each edge has a positive weight.
    graph structure: {node: {neighbor: weight, ...}, ...}
    """
    num_nodes = random.randint(min_nodes, max_nodes)
    names = [chr(ord('A') + i) for i in range(num_nodes)]
    nodes = [MeshNode(n) for n in names]

    # Initialize empty adjacency with weights
    graph = {n: {} for n in names}

    # Build a random spanning tree to ensure connectivity
    for i in range(1, num_nodes):
        src = names[i]
        dst = random.choice(names[:i])  # connect to any earlier node
        weight = random.randint(1, 10)
        graph[src][dst] = weight
        graph[dst][src] = weight

    # Add a few extra edges with low probability to avoid over-connection
    extra_edge_prob = 0.25
    for i, n in enumerate(names):
        for m in names:
            if n == m:
                continue
            if m in graph[n]:
                continue
            if random.random() < extra_edge_prob:
                weight = random.randint(1, 10)
                graph[n][m] = weight
                graph[m][n] = weight

    return nodes, graph


# ============================================================
# === POLYMORPHIC CIPHER (WITH AMPLIFIED KEYS)
# ============================================================

class PolymorphicCipher:
    def __init__(self, qrng):
        self.qrng = qrng

    def base_encrypt(self, plaintext):
        pt = plaintext.encode()
        key = self.qrng.amplified_random_bytes(len(pt))
        ct = bytes(a ^ b for a, b in zip(pt, key))
        return [ct], [key]

    def mutate_keys_per_hop(self, keys, num_hops):
        hop_mutations = []
        current_keys = keys
        for _ in range(num_hops):
            mutation_set = []
            mutated_keys = []
            for k in current_keys:
                mutation = self.qrng.amplified_random_bytes(len(k))
                mutation_set.append(mutation)
                mutated_keys.append(bytes(a ^ b for a, b in zip(k, mutation)))
            hop_mutations.append(mutation_set)
            current_keys = mutated_keys
        return hop_mutations, current_keys

    def reverse_mutations(self, mutated_keys, hop_mutations):
        keys = mutated_keys
        for mutation_set in reversed(hop_mutations):
            reversed_keys = []
            for k, mutation in zip(keys, mutation_set):
                reversed_keys.append(bytes(a ^ b for a, b in zip(k, mutation)))
            keys = reversed_keys
        return keys

    def decrypt_with_keys(self, chunks, keys):
        ct = chunks[0]
        key = keys[0]
        pt_bytes = bytes(a ^ b for a, b in zip(ct, key))
        return pt_bytes.decode()


# ============================================================
# === POLYMORPHIC MESH WITH WEIGHTED MULTI-HOP QUANTUM ROUTING
# ============================================================

class PolymorphicMesh:
    def __init__(self, nodes, graph, qrng, router):
        self.nodes = {n.name: n for n in nodes}
        self.graph = graph          # {node: {neighbor: weight}}
        self.qrng = qrng
        self.router = router
        self.cipher = PolymorphicCipher(qrng)

        self.paths = []
        self._build_candidate_paths()

    def _find_candidate_paths(self, src, dst, max_paths=6, max_depth=6):
        """
        Simple DFS to collect a handful of candidate paths from src to dst.
        """
        paths = []
        stack = [(src, [src])]

        while stack and len(paths) < max_paths:
            node, path = stack.pop()
            if len(path) > max_depth:
                continue
            if node == dst:
                paths.append(path)
                continue
            for neighbor in self.graph[node].keys():
                if neighbor in path:
                    continue
                stack.append((neighbor, path + [neighbor]))
        return paths

    def _build_candidate_paths(self):
        names = list(self.graph.keys())
        if len(names) >= 3:
            src = names[0]
            dst = names[-1]
            candidate = self._find_candidate_paths(src, dst)
            if candidate:
                self.paths = candidate
            else:
                mid = names[len(names)//2]
                self.paths = [
                    [src, dst],
                    [src, mid, dst],
                ]
        else:
            self.paths = [names]

    def path_cost(self, route):
        """
        Weighted path cost: sum of edge weights along the route.
        """
        cost = 0
        for i in range(len(route) - 1):
            u = route[i]
            v = route[i+1]
            cost += self.graph[u][v]
        return cost

    def build_route_multi_hop(self, src, dst, max_hops=6):
        """
        Primary route builder:
        - Try a quantum-walk-based route with local decisions.
        - If we fail to reach dst, use Grover-style amplitude amplification
          over candidate paths using weighted cost.
        """
        route = [src]
        current = src
        for _ in range(max_hops):
            if current == dst:
                break
            neighbors = list(self.graph[current].keys())
            if dst in neighbors:
                next_hop = dst
            else:
                next_hop = self.router.quantum_walk_step(current, neighbors)
            route.append(next_hop)
            current = next_hop

        if route[-1] != dst:
            costs = [self.path_cost(p) for p in self.paths]
            idx = self.router.choose_best_path_index(costs)
            route = self.paths[idx]

        return route

    def send(self, src, dst, message):
        route = self.build_route_multi_hop(src, dst)
        ct_chunks, base_keys = self.cipher.base_encrypt(message)
        hop_mutations, final_keys = self.cipher.mutate_keys_per_hop(base_keys, len(route) - 1)
        recovered_keys = self.cipher.reverse_mutations(final_keys, hop_mutations)
        recovered = self.cipher.decrypt_with_keys(ct_chunks, recovered_keys)
        return {
            "backend": "Polymorphic Mesh",
            "route": route,
            "ciphertext": [c.hex() for c in ct_chunks],
            "mutations": [[m.hex() for m in hop] for hop in hop_mutations],
            "recovered": recovered
        }


# ============================================================
# === MANUAL RSA
# ============================================================

def is_prime(n, k=8):
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23]
    if n in small_primes:
        return True
    if any(n % p == 0 for p in small_primes):
        return False
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def generate_prime(bits=512):
    while True:
        p = random.getrandbits(bits)
        p |= (1 << bits - 1) | 1
        if is_prime(p):
            return p

def extended_gcd(a, b):
    if a == 0:
        return (b, 0, 1)
    g, y, x = extended_gcd(b % a, a)
    return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception("modular inverse does not exist")
    return x % m

class RSAEncryptor:
    def __init__(self, bits=1024):
        self.p = generate_prime(bits // 2)
        self.q = generate_prime(bits // 2)
        self.n = self.p * self.q
        self.phi = (self.p - 1) * (self.q - 1)
        self.e = 65537
        self.d = modinv(self.e, self.phi)

    def encrypt(self, plaintext):
        m = int.from_bytes(plaintext.encode(), "big")
        c = pow(m, self.e, self.n)
        return hex(c)[2:]

    def decrypt(self, ciphertext_hex):
        c = int(ciphertext_hex, 16)
        m = pow(c, self.d, self.n)
        return m.to_bytes((m.bit_length() + 7) // 8, "big").decode()


# ============================================================
# === SECURE CHANNEL
# ============================================================

class SecureChannel:
    def __init__(self, rsa, mesh, threat_classifier):
        self.rsa = rsa
        self.mesh = mesh
        self.threat_classifier = threat_classifier

    def send(self, src, dst, message, algorithm):
        risk = self.threat_classifier.classify_algorithm(algorithm)
        ids_threat = "Low"
        use_mesh = (risk == "High Risk")
        if use_mesh:
            result = self.mesh.send(src, dst, message)
            result["risk"] = risk
            result["ids_threat"] = ids_threat
            return result
        else:
            ct = self.rsa.encrypt(message)
            recovered = self.rsa.decrypt(ct)
            return {
                "backend": "RSA",
                "risk": risk,
                "ids_threat": ids_threat,
                "ciphertext": ct,
                "recovered": recovered
            }


# ============================================================
# === CLEAN OUTPUT FORMATTER
# ============================================================

def print_result(title, result):
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)

    print(f"Backend:        {result['backend']}")
    print(f"Risk Level:     {result['risk']}")
    print(f"IDS Threat:     {result['ids_threat']}")

    if result["backend"] == "RSA":
        print("\n--- RSA Encryption ---")
        print(f"Ciphertext:     {result['ciphertext']}")
        print(f"Recovered:      {result['recovered']}")
    else:
        print("\n--- Polymorphic Mesh Encryption ---")
        print(f"Route:          {' -> '.join(result['route'])}")

        print("\nCiphertext Chunks:")
        for i, chunk in enumerate(result["ciphertext"]):
            print(f"  Chunk {i+1}: {chunk}")

        print("\nKey Mutations Per Hop:")
        for hop_index, hop in enumerate(result["mutations"]):
            print(f"  Hop {hop_index+1}:")
            for key_index, key in enumerate(hop):
                print(f"    Key {key_index+1}: {key}")

        print(f"\nRecovered:      {result['recovered']}")

    print("=" * 60 + "\n")


# ============================================================
# === DISPLAY NODE MAP (WITH WEIGHTS)
# ============================================================

def print_node_map(nodes, graph):
    print("\n" + "=" * 60)
    print("Generated Mesh Node Map (Weighted)")
    print("=" * 60)
    for n in nodes:
        name = n.name
        neighbors = graph[name]
        neighbor_str = ", ".join(f"{nbr}(w={wt})" for nbr, wt in neighbors.items())
        print(f"Node {name}: neighbors -> {neighbor_str}")
    print("=" * 60 + "\n")


def show_node_map_popup(nodes, graph):
    G = nx.Graph()

    for n in nodes:
        G.add_node(n.name)

    for src, neighbors in graph.items():
        for dst, weight in neighbors.items():
            if not G.has_edge(src, dst):
                G.add_edge(src, dst, weight=weight)

    plt.figure(figsize=(8, 6))
    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_nodes(G, pos, node_size=700, node_color="#00ffff")
    nx.draw_networkx_edges(G, pos, width=2, edge_color="#ff00ff")
    nx.draw_networkx_labels(G, pos, font_size=12, font_color="black")

    edge_labels = {(u, v): d["weight"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

    plt.title("Quantum Polymorphic Mesh Node Map (Weighted)", fontsize=16, color="#333333")
    plt.axis("off")
    plt.show()


# ============================================================
# === MAIN
# ============================================================

if __name__ == "__main__":
    qrng = QuantumRandom()
    router = QuantumGroverRouter()
    nodes, graph = generate_random_mesh()
    mesh = PolymorphicMesh(nodes, graph, qrng, router)
    rsa = RSAEncryptor()
    threat_classifier = QuantumThreatClassifier(MODEL, THREAT_DATA)
    channel = SecureChannel(rsa, mesh, threat_classifier)

    #Test 1:
    mesh_example_result = channel.send(nodes[0].name, nodes[-1].name, "HELLO QUANTUM WORLD", "RSA-2048")
    print_result("Example 1: Polymorphic Mesh (High Risk Algorithm)", mesh_example_result)

    #Test 2:
    result = channel.send(nodes[0].name, nodes[-1].name, "THIS MESSAGE USES RSA BACKEND", "AES-256")
    print_result("Example 2: RSA (Low Risk Algorithm)", result)

    #Final Example:
    print("\n=== Example 3: User Input ===")
    user_alg = input("Enter algorithm name (e.g., RSA-2048, Kyber, SPHINCS+): ")
    user_msg = input("Enter message to encrypt: ")
    result = channel.send(nodes[0].name, nodes[-1].name, user_msg, user_alg)
    print_result("Example 3: User Input Test", result)

    print_node_map(nodes, graph)
    show_node_map_popup(nodes, graph)

    # Weighted graph passed into animation; adapt mesh_animation to render weights if you like
    animate_transition(
        nodes,
        graph,
        rsa_route=["A", nodes[-1].name],
        mesh_route=mesh_example_result["route"],
        grover_steps=40
    )
