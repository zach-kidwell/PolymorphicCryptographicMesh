import math
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ============================================================
# === Mesh topology
# ============================================================

NODES = {
    "A": (0.1, 0.5),
    "B": (0.4, 0.8),
    "C": (0.9, 0.5),
    "D": (0.4, 0.2),
}

PATHS = [
    ["A", "B", "C"],
    ["A", "C"],
    ["A", "D", "C"],
    ["A", "B", "D", "C"],
]

GOOD_PATH_INDEX = 1  # pretend Grover likes path ["A","C"]


# ============================================================
# === Grover-style path selection (mocked)
# ============================================================

def choose_best_path(num_paths, good_index):
    # Simple biased choice: mostly good_index, sometimes others
    if random.random() < 0.8:
        return good_index
    else:
        return random.randint(0, num_paths - 1)


# ============================================================
# === Animation setup
# ============================================================

fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor("black")
ax.set_facecolor("black")
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis("off")

# Precompute node scatter
node_x = [NODES[n][0] for n in NODES]
node_y = [NODES[n][1] for n in NODES]
node_labels = list(NODES.keys())

# Base node style
node_scatter = ax.scatter(
    node_x,
    node_y,
    s=300,
    c="#00ffff",
    edgecolors="#00ffff",
    linewidths=2,
    alpha=0.8,
)

# Label nodes
for name, (x, y) in NODES.items():
    ax.text(
        x,
        y + 0.06,
        name,
        color="#00ffff",
        fontsize=12,
        ha="center",
        va="center",
        fontweight="bold",
    )

# RSA / Mesh text
mode_text = ax.text(
    0.5,
    0.95,
    "Mode: RSA",
    color="#00ff00",
    fontsize=14,
    ha="center",
    va="center",
    fontweight="bold",
)

status_text = ax.text(
    0.5,
    0.05,
    "",
    color="#ff00ff",
    fontsize=12,
    ha="center",
    va="center",
)

# Line objects for edges
edge_lines = []
for path in PATHS:
    xs = [NODES[n][0] for n in path]
    ys = [NODES[n][1] for n in path]
    line, = ax.plot(
        xs,
        ys,
        color="#003366",
        linewidth=2,
        alpha=0.3,
    )
    edge_lines.append(line)

# Active path line (neon)
active_line, = ax.plot(
    [],
    [],
    color="#ff00ff",
    linewidth=4,
    alpha=0.9,
)


# ============================================================
# === Animation function
# ============================================================

frames_total = 200

def update(frame):
    # Phase 0–50: RSA mode
    if frame < 50:
        mode_text.set_text("Mode: RSA")
        mode_text.set_color("#00ff00")
        status_text.set_text("Traffic is low-risk. Using classical RSA.")
        # Dim all edges
        for line in edge_lines:
            line.set_alpha(0.1)
            line.set_color("#003366")
        active_line.set_data([], [])
        return

    # Phase 50–80: risk rising
    if 50 <= frame < 80:
        mode_text.set_text("Mode: RSA")
        mode_text.set_color("#ffff00")
        status_text.set_text("Risk rising... evaluating quantum mesh.")
        # Slight glow on all edges
        for line in edge_lines:
            line.set_alpha(0.3)
            line.set_color("#004488")
        active_line.set_data([], [])
        return

    # Phase 80–110: switch to mesh
    if 80 <= frame < 110:
        mode_text.set_text("Mode: Switching...")
        mode_text.set_color("#ff8800")
        status_text.set_text("Failover: RSA → Polymorphic Quantum Mesh.")
        # Glow edges more
        for line in edge_lines:
            line.set_alpha(0.5)
            line.set_color("#0066aa")
        active_line.set_data([], [])
        return

    # Phase 110–frames_total: mesh active, animate path + key mutation
    mode_text.set_text("Mode: Polymorphic Mesh")
    mode_text.set_color("#ff00ff")
    status_text.set_text("Quantum Grover router selecting path; keys mutating per hop.")

    # Choose path index based on frame (mock Grover)
    path_index = choose_best_path(len(PATHS), GOOD_PATH_INDEX)
    path = PATHS[path_index]

    xs = [NODES[n][0] for n in path]
    ys = [NODES[n][1] for n in path]

    # Animate a "pulse" along the path
    t = (frame - 110) / (frames_total - 110)
    # Neon color oscillation
    color_phase = 0.5 + 0.5 * math.sin(10 * t)
    neon_color = (
        color_phase,
        0.0,
        1.0,
    )  # RGB in [0,1], purple-ish

    active_line.set_data(xs, ys)
    active_line.set_color(neon_color)
    active_line.set_linewidth(4 + 2 * math.sin(20 * t))

    # Dim non-active edges
    for i, line in enumerate(edge_lines):
        if i == path_index:
            line.set_alpha(0.2)
            line.set_color("#004466")
        else:
            line.set_alpha(0.05)
            line.set_color("#001122")

    return


# ============================================================
# === Run animation
# ============================================================

ani = animation.FuncAnimation(
    fig,
    update,
    frames=frames_total,
    interval=80,
    blit=False,
)

plt.show()
