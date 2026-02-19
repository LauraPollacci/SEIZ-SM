"""
Animation example for SEIZ epidemic models.

This script demonstrates how to create animated visualizations of epidemic
spreading over network structures.
"""

import sys
from pathlib import Path

# Add parent directory to path to locate seiz_models package
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import networkx as nx

from seiz_models import SEIZBMModel, SEIZModel, SEIZSMModel


def animate_basic_seiz():
    """Create animation for basic SEIZ model."""
    print("Creating animation for Basic SEIZ Model...")

    # Create a small network for better visualization
    G = nx.watts_strogatz_graph(n=50, k=4, p=0.1, seed=42)

    # Initialize model
    model = SEIZModel(graph=G, beta=0.6, b=0.3, rho=0.2, eps=0.05, p=0.4, l=0.6, dt=1.0)

    # Initialize states
    model.initialize_states(infected_frac=0.1, skeptic_frac=0.05, seed=123)

    # Create animation
    anim = model.animate_network(steps=30, interval=300, figsize=(10, 10), node_size=200, seed=42)

    print("  Animation created. Displaying...")
    plt.show()

    return model


def animate_seiz_bm():
    """Create animation for SEIZ-BM model."""
    print("\nCreating animation for SEIZ-BM Model...")

    # Create network
    G = nx.erdos_renyi_graph(n=50, p=0.08, seed=42)

    # Initialize model with moderation
    model = SEIZBMModel(
        graph=G,
        beta=0.6,
        b=0.3,
        rho=0.2,
        p=0.4,
        epsilon=0.2,
        l=0.6,
        mu=0.2,  # Higher moderation rate
        m=0.7,
    )

    # Initialize states
    model.initialize_states(infected_frac=0.15, skeptic_frac=0.05, seed=123)

    # Create and save animation as GIF
    try:
        print("  Saving animation as GIF...")
        anim = model.animate_network(
            steps=30,
            interval=300,
            figsize=(10, 10),
            node_size=200,
            seed=42,
            save_path="seiz_bm_animation.gif",
        )
        print("  Animation saved to 'seiz_bm_animation.gif'")
    except Exception as e:
        print(f"  Could not save GIF: {e}")
        print("  Displaying animation instead...")
        anim = model.animate_network(
            steps=30, interval=300, figsize=(10, 10), node_size=200, seed=42
        )
        plt.show()

    return model


def animate_seiz_sm():
    """Create animation for SEIZ-SM model."""
    print("\nCreating animation for SEIZ-SM Model...")

    # Create network
    G = nx.watts_strogatz_graph(n=50, k=4, p=0.1, seed=42)

    # Initialize smart moderator model
    model = SEIZSMModel(
        graph=G,
        beta=0.6,
        b=0.3,
        rho=0.2,
        p=0.4,
        epsilon=0.2,
        l=0.6,
        n=10,
        theta=3,
        T=0.5,
        eta=0.6,
        lambd=0.2,
    )

    # Initialize states
    model.initialize_states(infected_frac=0.15, skeptic_frac=0.05, seed=123)

    # Create animation
    anim = model.animate_network(steps=30, interval=300, figsize=(10, 10), node_size=200, seed=42)

    print("  Animation created. Displaying...")
    plt.show()

    return model


def main():
    """Main execution."""
    print("=" * 60)
    print("SEIZ Epidemic Models - Animation Examples")
    print("=" * 60)
    print()
    print("This script demonstrates network animations for epidemic spreading.")
    print("Close each animation window to proceed to the next.")
    print()

    # Run animations
    model1 = animate_basic_seiz()

    # Uncomment to see other models
    # model2 = animate_seiz_bm()
    # model3 = animate_seiz_sm()

    print()
    print("=" * 60)
    print("Animation examples completed!")
    print()
    print("Tips:")
    print("  - Adjust 'steps' and 'interval' for different animation speeds")
    print("  - Use save_path='filename.gif' to save animations")
    print("  - Smaller networks (20-50 nodes) work best for visualization")
    print("=" * 60)


if __name__ == "__main__":
    main()
