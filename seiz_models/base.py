"""
Base class for SEIZ epidemic models.

This module provides an abstract base class that defines the common interface
for all SEIZ epidemic models.
"""

import json
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt


class BaseEpidemicModel(ABC):
    """
    Abstract base class for SEIZ epidemic models.

    All models must implement the standard interface for:
    - Instantiation with parameters
    - Initialization of states
    - Step-wise execution
    - JSON output
    - Visualization
    """

    def __init__(self, graph, **params):
        """
        Initialize the model.

        Args:
            graph: networkx.Graph - Social network of agents
            **params: Model-specific parameters
        """
        self.graph = graph
        self.params = params
        self.history = []
        self._current_step = 0

    @abstractmethod
    def initialize_states(
        self, infected_frac: float = 0.05, skeptic_frac: float = 0.05, seed: Optional[int] = None
    ) -> None:
        """
        Initialize the states of agents in the network.

        Args:
            infected_frac: Fraction of initially infected agents
            skeptic_frac: Fraction of initially skeptic agents
            seed: Random seed for reproducibility
        """
        pass

    @abstractmethod
    def step(self) -> None:
        """Execute one simulation step."""
        pass

    @abstractmethod
    def get_states(self) -> Dict[Any, str]:
        """
        Get current states of all agents.

        Returns:
            Dictionary mapping node -> state
        """
        pass

    def count_states(self) -> Dict[str, int]:
        """
        Count the number of agents in each state.

        Returns:
            Dictionary with counts for each state (S, E, I, Z)
        """
        states = self.get_states()
        counts = Counter(states.values())
        # Ensure all states are present
        for state in ["S", "E", "I", "Z"]:
            if state not in counts:
                counts[state] = 0
        return dict(counts)

    def run(self, steps: int = 100) -> List[Dict[str, int]]:
        """
        Run the simulation for a specified number of steps.

        Args:
            steps: Number of simulation steps

        Returns:
            List of state count dictionaries for each step
        """
        self.history = []
        for step in range(steps):
            self._current_step = step
            counts = self.count_states()
            counts["step"] = step
            self.history.append(counts)
            self.step()

        # Record final state
        counts = self.count_states()
        counts["step"] = steps
        self.history.append(counts)

        return self.history

    def to_json(self, indent: int = 2) -> str:
        """
        Export simulation results to JSON format.

        Args:
            indent: JSON indentation level

        Returns:
            JSON string with model parameters and history
        """
        output = {
            "model_type": self.__class__.__name__,
            "parameters": self.params,
            "network_info": {
                "num_nodes": self.graph.number_of_nodes(),
                "num_edges": self.graph.number_of_edges(),
            },
            "history": self.history,
        }
        return json.dumps(output, indent=indent)

    def save_json(self, filepath: str) -> None:
        """
        Save simulation results to a JSON file.

        Args:
            filepath: Path to output JSON file
        """
        with open(filepath, "w") as f:
            f.write(self.to_json())

    def plot(self, title: Optional[str] = None, figsize: tuple = (10, 6)) -> None:
        """
        Plot the time series of state counts.

        Args:
            title: Plot title (uses model name if not provided)
            figsize: Figure size (width, height)
        """
        if not self.history:
            raise ValueError("No history to plot. Run the simulation first.")

        if title is None:
            title = f"{self.__class__.__name__} Dynamics"

        steps = [h["step"] for h in self.history]
        s_counts = [h["S"] for h in self.history]
        e_counts = [h["E"] for h in self.history]
        i_counts = [h["I"] for h in self.history]
        z_counts = [h["Z"] for h in self.history]

        plt.figure(figsize=figsize)
        plt.plot(steps, s_counts, label="Susceptible (S)", color="blue", linewidth=2)
        plt.plot(steps, e_counts, label="Exposed (E)", color="orange", linewidth=2)
        plt.plot(steps, i_counts, label="Infected (I)", color="red", linewidth=2)
        plt.plot(steps, z_counts, label="Skeptic (Z)", color="green", linewidth=2)

        plt.xlabel("Time Steps", fontsize=12)
        plt.ylabel("Number of Agents", fontsize=12)
        plt.title(title, fontsize=14, fontweight="bold")
        plt.legend(loc="best", fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def save_plot(
        self, filepath: str, title: Optional[str] = None, figsize: tuple = (10, 6), dpi: int = 300
    ) -> None:
        """
        Save the time series plot to a file.

        Args:
            filepath: Path to output image file
            title: Plot title (uses model name if not provided)
            figsize: Figure size (width, height)
            dpi: Resolution in dots per inch
        """
        if not self.history:
            raise ValueError("No history to plot. Run the simulation first.")

        if title is None:
            title = f"{self.__class__.__name__} Dynamics"

        steps = [h["step"] for h in self.history]
        s_counts = [h["S"] for h in self.history]
        e_counts = [h["E"] for h in self.history]
        i_counts = [h["I"] for h in self.history]
        z_counts = [h["Z"] for h in self.history]

        plt.figure(figsize=figsize)
        plt.plot(steps, s_counts, label="Susceptible (S)", color="blue", linewidth=2)
        plt.plot(steps, e_counts, label="Exposed (E)", color="orange", linewidth=2)
        plt.plot(steps, i_counts, label="Infected (I)", color="red", linewidth=2)
        plt.plot(steps, z_counts, label="Skeptic (Z)", color="green", linewidth=2)

        plt.xlabel("Time Steps", fontsize=12)
        plt.ylabel("Number of Agents", fontsize=12)
        plt.title(title, fontsize=14, fontweight="bold")
        plt.legend(loc="best", fontsize=10)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filepath, dpi=dpi, bbox_inches="tight")
        plt.close()

    def animate_network(
        self,
        steps: int = 50,
        interval: int = 200,
        repeat: bool = True,
        save_path: Optional[str] = None,
        figsize: tuple = (8, 8),
        node_size: int = 100,
        seed: Optional[int] = None,
    ) -> Any:
        """
        Generate an animation of the epidemic spreading over the network.

        This method creates an animated visualization showing how states change
        over time on the network structure. Nodes are colored according to their
        state: blue (S), orange (E), red (I), green (Z).

        Args:
            steps: Number of simulation steps to animate
            interval: Delay between frames in milliseconds
            repeat: Whether to loop the animation
            save_path: Optional path to save animation as MP4 or GIF file
                      (requires ffmpeg for MP4, pillow for GIF)
            figsize: Figure size (width, height)
            node_size: Size of nodes in the visualization
            seed: Random seed for layout reproducibility

        Returns:
            matplotlib.animation.FuncAnimation object

        Example:
            >>> model.initialize_states(infected_frac=0.05, seed=42)
            >>> anim = model.animate_network(steps=50, interval=200)
            >>> # To save: model.animate_network(steps=50, save_path='diffusion.mp4')
        """
        try:
            import networkx as nx
            from matplotlib.animation import FuncAnimation
        except ImportError as e:
            raise ImportError(
                "Animation requires networkx and matplotlib. "
                "Install with: pip install networkx matplotlib"
            ) from e

        # Check that initial states are set
        initial_states = self.get_states()
        if not initial_states:
            raise ValueError(
                "States must be initialized before animation. " "Call initialize_states() first."
            )

        # Store original history to restore after animation
        original_history = self.history.copy()

        # Compute layout once for consistency
        pos = nx.spring_layout(self.graph, seed=seed)

        # Create figure and axis
        fig, ax = plt.subplots(figsize=figsize)

        # State color mapping
        state_colors = {
            "S": "#1f77b4",  # blue
            "E": "#ff7f0e",  # orange
            "I": "#d62728",  # red
            "Z": "#2ca02c",  # green
        }

        def update(frame):
            """Update function for animation."""
            ax.clear()

            # Execute one simulation step
            if frame > 0:
                self.step()

            # Get current states and map to colors
            states = self.get_states()
            node_colors = [state_colors.get(states[node], "#cccccc") for node in self.graph.nodes()]

            # Count states for display
            counts = self.count_states()

            # Draw network
            nx.draw(
                self.graph,
                pos,
                node_color=node_colors,
                node_size=node_size,
                with_labels=False,
                ax=ax,
                edge_color="#cccccc",
                width=0.5,
            )

            # Add title with state counts
            title = f"{self.__class__.__name__} - Step {frame}\n"
            title += f"S: {counts['S']}, E: {counts['E']}, I: {counts['I']}, Z: {counts['Z']}"
            ax.set_title(title, fontsize=12, fontweight="bold")

            # Add legend
            from matplotlib.patches import Patch

            legend_elements = [
                Patch(facecolor=state_colors["S"], label="Susceptible"),
                Patch(facecolor=state_colors["E"], label="Exposed"),
                Patch(facecolor=state_colors["I"], label="Infected"),
                Patch(facecolor=state_colors["Z"], label="Skeptic"),
            ]
            ax.legend(handles=legend_elements, loc="upper right", fontsize=8)

            return (ax,)

        # Create animation
        anim = FuncAnimation(
            fig,
            update,
            frames=steps + 1,  # +1 to include initial state
            interval=interval,
            repeat=repeat,
            blit=False,
        )

        # Save animation if path provided
        if save_path:
            if save_path.endswith(".gif"):
                try:
                    anim.save(save_path, writer="pillow", fps=1000 // interval)
                    print(f"Animation saved to {save_path}")
                except Exception as e:
                    print(f"Warning: Could not save GIF. Error: {e}")
                    print("Install pillow with: pip install pillow")
            elif save_path.endswith(".mp4"):
                try:
                    anim.save(save_path, writer="ffmpeg", fps=1000 // interval, dpi=100)
                    print(f"Animation saved to {save_path}")
                except Exception as e:
                    print(f"Warning: Could not save MP4. Error: {e}")
                    print("Install ffmpeg or use .gif format instead")
            else:
                raise ValueError("save_path must end with .gif or .mp4")

        # Restore original history
        self.history = original_history

        plt.tight_layout()
        return anim
