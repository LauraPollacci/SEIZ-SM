"""
Basic usage example for SEIZ epidemic models.

This script demonstrates how to use all three models and compare their results.
"""

import sys
from pathlib import Path

# Add parent directory to path to locate seiz_models package
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import networkx as nx

from seiz_models import SEIZBMModel, SEIZModel, SEIZSMModel


def run_basic_seiz():
    """Run basic SEIZ model."""
    print("Running Basic SEIZ Model...")

    # Create network
    G = nx.watts_strogatz_graph(n=200, k=6, p=0.1, seed=42)

    # Initialize model
    model = SEIZModel(graph=G, beta=0.6, b=0.3, rho=0.2, eps=0.05, p=0.4, l=0.6, dt=1.0)

    # Run simulation
    model.initialize_states(infected_frac=0.05, skeptic_frac=0.05, seed=123)
    history = model.run(steps=100)

    # Save results
    model.save_json("seiz_basic_results.json")
    print(f"  Final state: {model.count_states()}")

    return history


def run_seiz_bm():
    """Run SEIZ-BM (Basic Moderator) model."""
    print("Running SEIZ-BM Model...")

    # Create network
    G = nx.watts_strogatz_graph(n=200, k=6, p=0.1, seed=42)

    # Initialize model
    model = SEIZBMModel(
        graph=G, beta=0.6, b=0.3, rho=0.2, p=0.4, epsilon=0.2, l=0.6, mu=0.15, m=0.6
    )

    # Run simulation
    model.initialize_states(infected_frac=0.05, skeptic_frac=0.05, seed=123)
    history = model.run(steps=100)

    # Save results
    model.save_json("seiz_bm_results.json")
    print(f"  Final state: {model.count_states()}")

    return history


def run_seiz_sm():
    """Run SEIZ-SM (Smart Moderator) model."""
    print("Running SEIZ-SM Model...")

    # Create network
    G = nx.watts_strogatz_graph(n=200, k=6, p=0.1, seed=42)

    # Initialize model
    model = SEIZSMModel(
        graph=G,
        beta=0.6,
        b=0.3,
        rho=0.2,
        p=0.4,
        epsilon=0.2,
        l=0.6,
        n=40,
        theta=3,
        T=0.5,
        eta=0.6,
        lambd=0.2,
    )

    # Run simulation
    model.initialize_states(infected_frac=0.05, skeptic_frac=0.05, seed=123)
    history = model.run(steps=100)

    # Save results
    model.save_json("seiz_sm_results.json")
    print(f"  Final state: {model.count_states()}")

    return history


def compare_models(hist_basic, hist_bm, hist_sm):
    """Compare results from all three models."""
    print("\nGenerating comparison plot...")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot infected counts for each model
    models = [
        (hist_basic, "Basic SEIZ", axes[0, 0]),
        (hist_bm, "SEIZ-BM", axes[0, 1]),
        (hist_sm, "SEIZ-SM", axes[1, 0]),
    ]

    for history, title, ax in models:
        steps = [h["step"] for h in history]
        s_counts = [h["S"] for h in history]
        e_counts = [h["E"] for h in history]
        i_counts = [h["I"] for h in history]
        z_counts = [h["Z"] for h in history]

        ax.plot(steps, s_counts, label="S", color="blue", linewidth=2)
        ax.plot(steps, e_counts, label="E", color="orange", linewidth=2)
        ax.plot(steps, i_counts, label="I", color="red", linewidth=2)
        ax.plot(steps, z_counts, label="Z", color="green", linewidth=2)

        ax.set_xlabel("Time Steps")
        ax.set_ylabel("Number of Agents")
        ax.set_title(title, fontweight="bold")
        ax.legend()
        ax.grid(True, alpha=0.3)

    # Comparison of infected over time
    ax = axes[1, 1]
    steps = [h["step"] for h in hist_basic]

    ax.plot(
        steps,
        [h["I"] for h in hist_basic],
        label="Basic SEIZ",
        color="red",
        linewidth=2,
        linestyle="-",
    )
    ax.plot(
        steps,
        [h["I"] for h in hist_bm],
        label="SEIZ-BM",
        color="orange",
        linewidth=2,
        linestyle="--",
    )
    ax.plot(
        steps,
        [h["I"] for h in hist_sm],
        label="SEIZ-SM",
        color="purple",
        linewidth=2,
        linestyle=":",
    )

    ax.set_xlabel("Time Steps")
    ax.set_ylabel("Number of Infected (I)")
    ax.set_title("Comparison: Infected Agents", fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("model_comparison.png", dpi=300, bbox_inches="tight")
    print("  Saved comparison plot to 'model_comparison.png'")
    plt.show()


def main():
    """Main execution."""
    print("=" * 60)
    print("SEIZ Epidemic Models - Basic Usage Example")
    print("=" * 60)
    print()

    # Run all three models
    hist_basic = run_basic_seiz()
    hist_bm = run_seiz_bm()
    hist_sm = run_seiz_sm()

    # Compare results
    compare_models(hist_basic, hist_bm, hist_sm)

    print()
    print("=" * 60)
    print("Example completed successfully!")
    print("Check the generated JSON files and comparison plot.")
    print("=" * 60)


if __name__ == "__main__":
    main()
