"""
Basic SEIZ (Susceptible-Exposed-Infected-Skeptic) epidemic model.

This module implements the basic SEIZ model without any moderation mechanisms.
"""

import math
import random
from collections import defaultdict
from typing import Any, Dict, Optional

import networkx as nx

from .base import BaseEpidemicModel


def rate_to_prob(rate: float, dt: float) -> float:
    """Convert a continuous-time rate to per-timestep probability."""
    return 1 - math.exp(-rate * dt)


class SEIZModel(BaseEpidemicModel):
    """
    Basic SEIZ epidemic model on a social network.

    States:
        S - Susceptible: Can be infected or become skeptic
        E - Exposed: Infected but not yet spreading
        I - Infected: Actively spreading
        Z - Skeptic: Resistant to infection

    Parameters:
        beta: Contact rate between S and I
        b: Contact rate between S and Z
        rho: Transition rate E -> I
        eps: Transition rate I -> E
        p: Probability S -> I after contact with I
        l: Probability S -> Z after contact with Z
        dt: Time step size for rate conversion (default: 1.0)
    """

    def __init__(
        self,
        graph: nx.Graph,
        beta: float,
        b: float,
        rho: float,
        eps: float,
        p: float,
        l: float,
        dt: float = 1.0,
    ):
        """
        Initialize the SEIZ model.

        Args:
            graph: Social network (NetworkX graph)
            beta: S-I contact rate
            b: S-Z contact rate
            rho: E -> I transition rate
            eps: I -> E transition rate
            p: Probability S -> I after contact with I
            l: Probability S -> Z after contact with Z
            dt: Time step size
        """
        params = {"beta": beta, "b": b, "rho": rho, "eps": eps, "p": p, "l": l, "dt": dt}
        super().__init__(graph, **params)

        self.beta = beta
        self.b = b
        self.rho = rho
        self.eps = eps
        self.p = p
        self.l = l
        self.dt = dt

        # Convert rates to probabilities
        self.prob_contact_I = rate_to_prob(beta, dt)
        self.prob_contact_Z = rate_to_prob(b, dt)
        self.prob_E_to_I = rate_to_prob(rho, dt)
        self.prob_I_to_E = rate_to_prob(eps, dt)

        # Initialize states dictionary
        self.states = {}
        for node in self.graph.nodes():
            self.states[node] = "S"

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
            self.states[node] = "S"

        # Set infected
        n_infected = int(n * infected_frac)
        for i in range(n_infected):
            self.states[nodes[i]] = "I"

        # Set skeptics
        n_skeptic = int(n * skeptic_frac)
        for i in range(n_infected, n_infected + n_skeptic):
            self.states[nodes[i]] = "Z"

    def step(self) -> None:
        """Execute one simulation step using synchronous update."""
        proposals = defaultdict(list)

        # --- Contact-based transitions ---
        for node, state in self.states.items():
            # Infectious contacts (S-I)
            if state == "I":
                for neighbor in self.graph.neighbors(node):
                    if self.states[neighbor] == "S" and random.random() < self.prob_contact_I:
                        if random.random() < self.p:
                            proposals[neighbor].append("I")
                        else:
                            proposals[neighbor].append("E")

            # Skeptic contacts (S-Z)
            elif state == "Z":
                for neighbor in self.graph.neighbors(node):
                    if self.states[neighbor] == "S" and random.random() < self.prob_contact_Z:
                        if random.random() < self.l:
                            proposals[neighbor].append("Z")
                        else:
                            proposals[neighbor].append("E")

        # --- Internal progressions (E <-> I) ---
        for node, state in self.states.items():
            if state == "E" and random.random() < self.prob_E_to_I:
                proposals[node].append("I")
            elif state == "I" and random.random() < self.prob_I_to_E:
                proposals[node].append("E")

        # --- Apply updates synchronously ---
        for node, plist in proposals.items():
            # If multiple proposals, choose one randomly
            chosen = random.choice(plist)
            self.states[node] = chosen

    def get_states(self) -> Dict[Any, str]:
        """
        Get current states of all agents.

        Returns:
            Dictionary mapping node -> state
        """
        return dict(self.states)
