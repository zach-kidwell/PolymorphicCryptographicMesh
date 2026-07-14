import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import random
import math

# ============================================================
# === ANIMATION: RSA → GROVER SEARCH → POLYMORPHIC MESH
# ============================================================

def animate_transition(nodes, graph, rsa_route=None, mesh_route=None, grover_steps=30):

    G = nx.Graph()
    for n in nodes:
        G.add_node(n.name)
    for src, neighbors in graph.items():
        for dst in neighbors:
            G.add_edge(src, dst)

    pos = nx.spring_layout(G, seed=42)

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    plt.axis("off")

    total_frames = 120 + grover_steps

    grover_pulse = [
        0.5 + 0.5 * math.sin((i / grover_steps) * math.pi)
        for i in range(grover_steps)
    ]

    def draw_graph(frame):
        ax.clear()
        ax.set_facecolor("black")
        plt.axis("off")

        # Draw nodes (fixed color)
        nx.draw_networkx_nodes(
            G, pos,
            node_size=700,
            node_color=["#00ffff"] * len(G.nodes),   # FIXED
            ax=ax
        )

        nx.draw_networkx_labels(
            G, pos,
            font_size=12,
            font_color="white",
            ax=ax
        )

        # Phase 1: RSA mode
        if frame < 40:
            nx.draw_networkx_edges(
                G, pos,
                edge_color=["#3399ff"] * len(G.edges),   # FIXED
                width=2,
                ax=ax
            )
            ax.set_title("RSA Mode — Classical Encryption", color="white")

            if rsa_route:
                route_edges = [(rsa_route[i], rsa_route[i+1]) for i in range(len(rsa_route)-1)]
                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=route_edges,
                    edge_color=["#66ccff"] * len(route_edges),   # FIXED
                    width=4,
                    ax=ax
                )

        # Phase 2: Grover amplification
        elif frame < 40 + grover_steps:
            step = frame - 40
            pulse = grover_pulse[step]

            pulse_color = [(pulse, 0, pulse)] * len(G.edges)

            nx.draw_networkx_edges(
                G, pos,
                edge_color=pulse_color,   # FIXED
                width=2 + 4 * pulse,
                ax=ax
            )

            if mesh_route:
                highlight_nodes = mesh_route
                pulse_node_color = [(pulse, 0, 1)] * len(highlight_nodes)

                nx.draw_networkx_nodes(
                    G, pos,
                    nodelist=highlight_nodes,
                    node_size=700 + 300 * pulse,
                    node_color=pulse_node_color,   # FIXED
                    ax=ax
                )

            ax.set_title("Grover's Algorithm — Quantum Search for Best Route", color="white")

        # Phase 3: Polymorphic Mesh mode
        else:
            nx.draw_networkx_edges(
                G, pos,
                edge_color=["#ff00ff"] * len(G.edges),   # FIXED
                width=2,
                ax=ax
            )
            ax.set_title("Polymorphic Mesh — Quantum Routing Active", color="white")

            if mesh_route:
                route_edges = [(mesh_route[i], mesh_route[i+1]) for i in range(len(mesh_route)-1)]
                pulse = 0.5 + 0.5 * random.random()
                pulse_color = [(pulse, 0, 1)] * len(route_edges)

                nx.draw_networkx_edges(
                    G, pos,
                    edgelist=route_edges,
                    edge_color=pulse_color,   # FIXED
                    width=4 + 2 * pulse,
                    ax=ax
                )

    ani = animation.FuncAnimation(
        fig,
        draw_graph,
        frames=total_frames,
        interval=80,
        repeat=False
    )

    plt.show()

    plt.close('all')
    plt.pause(0.001)


    #plt.close(fig)


# ============================================================
# === OPTIONAL TEST HARNESS
# ============================================================

if __name__ == "__main__":
    class N:
        def __init__(self, name): self.name = name

    nodes = [N(n) for n in ["A", "B", "C", "D"]]
    graph = {
        "A": ["B", "C"],
        "B": ["A", "D"],
        "C": ["A", "D"],
        "D": ["B", "C"]
    }

    rsa_route = ["A", "B", "D"]
    mesh_route = ["A", "C", "D"]

    animate_transition(nodes, graph, rsa_route, mesh_route)
