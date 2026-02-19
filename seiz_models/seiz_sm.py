"""
SEIZ-SM (Smart Moderator) epidemic model.

This module implements the SEIZ model with a smart moderation mechanism
that uses agent profiles (Dark Triad traits) and message toxicity tracking.
"""

import random
from collections import defaultdict
from typing import Any, Dict, Optional

import networkx as nx

from .base import BaseEpidemicModel


class Agent:
    """Agent with Dark Triad profile and message tracking."""

    def __init__(self, state: str = "S"):
        self.state = state
        # Dark Triad profile: [Narcissism, Machiavellianism, Psychopathy]
        self.profile = [random.random(), random.random(), random.random()]
        self.toxic_messages = 0  # Count of toxic messages sent
        self.activity_level = 0  # Number of messages sent overall


class SEIZSMModel(BaseEpidemicModel):
    """
    SEIZ model with Smart Moderator.

    Extends SEIZ with a sophisticated moderation mechanism that:
    - Tracks agent behavior (toxic messages)
    - Uses Dark Triad personality profiles
    - Intervenes based on toxicity thresholds

    States:
        S - Susceptible
        E - Exposed
        I - Infected
        Z - Skeptic

    Parameters:
        beta: Contact rate S-I
        b: Contact rate S-Z
        rho: Contact rate E-I
        p: Probability S -> I after contact with I
        epsilon: Incubation rate E -> I
        l: Probability S -> Z after contact with Z
        n: Number of messages sent at each timestep
        theta: Toxic message threshold for moderator intervention
        T: Probability threshold to classify a message as toxic
        eta: Probability of I -> E after moderation
        lambd: Probability of E -> Z transition
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
        n: int,
        theta: int,
        T: float,
        eta: float,
        lambd: float,
    ):
        """
        Initialize the SEIZ-SM model.

        Args:
            graph: Social network (NetworkX graph)
            beta: S-I contact rate
            b: S-Z contact rate
            rho: E-I contact rate
            p: Probability S -> I after contact with I
            epsilon: Incubation rate E -> I
            l: Probability S -> Z after contact with Z
            n: Number of messages sent per timestep
            theta: Toxic message threshold for intervention
            T: Toxicity probability threshold
            eta: Probability I -> E after moderation
            lambd: Probability E -> Z
        """
        params = {
            "beta": beta,
            "b": b,
            "rho": rho,
            "p": p,
            "epsilon": epsilon,
            "l": l,
            "n": n,
            "theta": theta,
            "T": T,
            "eta": eta,
            "lambd": lambd,
        }
        super().__init__(graph, **params)

        self.beta = beta
        self.b = b
        self.rho = rho
        self.p = p
        self.epsilon = epsilon
        self.l = l
        self.n = n
        self.theta = theta
        self.T = T
        self.eta = eta
        self.lambd = lambd

        # Initialize agents with profiles
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

        # Reset all to susceptible and regenerate profiles
        for node in nodes:
            agent = self.graph.nodes[node]["agent"]
            agent.state = "S"
            agent.profile = [random.random(), random.random(), random.random()]
            agent.toxic_messages = 0
            agent.activity_level = 0

        # Set infected
        n_infected = int(n * infected_frac)
        for i in range(n_infected):
            self.graph.nodes[nodes[i]]["agent"].state = "I"

        # Set skeptics
        n_skeptic = int(n * skeptic_frac)
        for i in range(n_infected, n_infected + n_skeptic):
            self.graph.nodes[nodes[i]]["agent"].state = "Z"

    def compute_toxicity(self, agent: Agent) -> float:
        """
        Compute toxicity score based on Dark Triad profile.

        Args:
            agent: Agent to compute toxicity for

        Returns:
            Toxicity score (average of Dark Triad traits)
        """
        return sum(agent.profile) / 3.0

    def moderator_intervention(self, agent: Agent) -> None:
        """
        Smart moderator intervenes if threshold exceeded.

        Args:
            agent: Agent to potentially moderate
        """
        if agent.toxic_messages >= self.theta:
            # Probability of becoming exposed depends on Dark Triad traits
            dark_trait_factor = 1 - sum(agent.profile) / 3.0
            effective_eta = self.eta * dark_trait_factor

            if random.random() < effective_eta:
                agent.state = "E"
                agent.toxic_messages = 0  # Reset counter
            elif random.random() < self.lambd:
                agent.state = "Z"
                agent.toxic_messages = 0

    def send_messages(self) -> list:
        """
        Simulate message sending process with toxicity.

        Returns:
            List of nodes that sent toxic messages
        """
        nodes = list(self.graph.nodes())
        senders = random.sample(nodes, min(self.n, len(nodes)))
        toxic_senders = []

        for sender in senders:
            agent = self.graph.nodes[sender]["agent"]
            agent.activity_level += 1

            if agent.state == "I":
                toxicity = self.compute_toxicity(agent)
                if toxicity >= self.T:
                    agent.toxic_messages += 1
                    toxic_senders.append(sender)
                    self.moderator_intervention(agent)

        return toxic_senders

    def spread_toxicity(self, toxic_senders: list) -> None:
        """
        Neighbors of toxic senders may transition based on SEIZ logic.

        Args:
            toxic_senders: List of nodes that sent toxic messages
        """
        for sender in toxic_senders:
            for neighbor in self.graph.neighbors(sender):
                nb_agent = self.graph.nodes[neighbor]["agent"]

                if nb_agent.state == "S":
                    if random.random() < self.beta:
                        nb_agent.state = "I" if random.random() < self.p else "E"

                elif nb_agent.state == "E":
                    if random.random() < self.rho:
                        nb_agent.state = "I"

    def internal_transitions(self) -> None:
        """Handle E -> I and E -> Z transitions."""
        for node in self.graph.nodes():
            agent = self.graph.nodes[node]["agent"]

            if agent.state == "E":
                if random.random() < self.epsilon:
                    agent.state = "I"
                elif random.random() < self.lambd:
                    agent.state = "Z"

    def step(self) -> None:
        """Execute one simulation step."""
        toxic_senders = self.send_messages()
        self.spread_toxicity(toxic_senders)
        self.internal_transitions()

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
