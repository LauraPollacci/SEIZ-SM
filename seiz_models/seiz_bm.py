"""
SEIZ-BM (Basic Moderator) epidemic model.

This module implements the SEIZ model with a basic moderation mechanism
that can intervene on infected agents.
"""

import random
from typing import Any, Dict, Optional

import networkx as nx

from .base import BaseEpidemicModel


class Agent:
    """Simple agent with state information."""

    def __init__(self, state: str = "S"):
        self.state = state


class SEIZBMModel(BaseEpidemicModel):
    """
    SEIZ model with Basic Moderator.

    Extends the basic SEIZ model with a moderation mechanism that can
    intervene on infected agents with a certain probability.

    States:
        S - Susceptible
        E - Exposed
        I - Infected
        Z - Skeptic

    Parameters:
        beta: Contact rate between S and I
        b: Contact rate between S and Z
        rho: Contact rate between E and I
        p: Probability S -> I after contact with I
        epsilon: Incubation rate E -> I
        l: Probability S -> Z after contact with Z
        mu: Moderator intervention rate (probability I is moderated)
        m: Probability moderated I returns to S
    """

    def __init__(
        self,
        graph: nx.Graph,
        beta: float,
        b: float,
        rho: float,
        p: float,
        epsilon: float,
        l: float,
        mu: float,
        m: float,
    ):
        """
        Initialize the SEIZ-BM model.

        Args:
            graph: Social network (NetworkX graph)
            beta: S-I contact rate
            b: S-Z contact rate
            rho: E-I contact rate
            p: Probability S -> I after contact with I
            epsilon: Incubation rate E -> I
            l: Probability S -> Z after contact with Z
            mu: Moderator intervention rate
            m: Probability of successful moderation (I -> S)
        """
        params = {
            "beta": beta,
            "b": b,
            "rho": rho,
            "p": p,
            "epsilon": epsilon,
            "l": l,
            "mu": mu,
            "m": m,
        }
        super().__init__(graph, **params)

        self.beta = beta
        self.b = b
        self.rho = rho
        self.p = p
        self.epsilon = epsilon
        self.l = l
        self.mu = mu
        self.m = m

        # Initialize agents
        for node in self.graph.nodes():
            self.graph.nodes[node]["agent"] = Agent("S")

    def initialize_states(
        self, infected_frac: float = 0.05, skeptic_frac: float = 0.05, seed: Optional[int] = None
    ) -> None:
        """
        Initialize agent states.

        Args:
            infected_frac: Fraction of initially infected agents
            skeptic_frac: Fraction of initially skeptic agents
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

        nodes = list(self.graph.nodes())
        random.shuffle(nodes)
        n = len(nodes)

        # Reset all to susceptible
        for node in nodes:
            self.graph.nodes[node]["agent"].state = "S"

        # Set infected
        n_infected = int(n * infected_frac)
        for i in range(n_infected):
            self.graph.nodes[nodes[i]]["agent"].state = "I"

        # Set skeptics
        n_skeptic = int(n * skeptic_frac)
        for i in range(n_infected, n_infected + n_skeptic):
            self.graph.nodes[nodes[i]]["agent"].state = "Z"

    def step(self) -> None:
        """Execute one simulation step."""
        new_states = {}

        for node in self.graph.nodes():
            agent = self.graph.nodes[node]["agent"]
            state = agent.state

            if state == "S":
                # Check for contacts with infected or skeptic neighbors
                neighbors = list(self.graph.neighbors(node))
                for neighbor in neighbors:
                    nb_state = self.graph.nodes[neighbor]["agent"].state

                    if nb_state == "I" and random.random() < self.beta:
                        new_states[node] = "I" if random.random() < self.p else "E"
                        break
                    elif nb_state == "Z" and random.random() < self.b:
                        new_states[node] = "Z" if random.random() < self.l else "E"
                        break

            elif state == "E":
                # Transition to infected based on epsilon rate
                if random.random() < self.epsilon:
                    new_states[node] = "I"
                else:
                    # Or through contact with infected neighbors
                    neighbors = list(self.graph.neighbors(node))
                    for neighbor in neighbors:
                        if (
                            self.graph.nodes[neighbor]["agent"].state == "I"
                            and random.random() < self.rho
                        ):
                            new_states[node] = "I"
                            break

            elif state == "I":
                # Moderator intervention
                if random.random() < self.mu:
                    if random.random() < self.m:
                        new_states[node] = "S"
                    # else stays I (failed moderation)

        # Apply state changes
        for node, new_state in new_states.items():
            self.graph.nodes[node]["agent"].state = new_state

    def get_states(self) -> Dict[Any, str]:
        """
        Get current states of all agents.

        Returns:
            Dictionary mapping node -> state
        """
        states = {}
        for node in self.graph.nodes():
            states[node] = self.graph.nodes[node]["agent"].state
        return states
