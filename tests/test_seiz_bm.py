"""
Unit tests for the SEIZ-BM (Basic Moderator) model.
"""

import json
import os
import tempfile
import unittest

import networkx as nx

from seiz_models import SEIZBMModel


class TestSEIZBMModel(unittest.TestCase):
    """Test cases for SEIZBMModel."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a small test network
        self.graph = nx.erdos_renyi_graph(50, 0.1, seed=42)

        # Standard parameters
        self.params = {
            "beta": 0.3,
            "b": 0.2,
            "rho": 0.2,
            "p": 0.5,
            "epsilon": 0.2,
            "l": 0.4,
            "mu": 0.1,
            "m": 0.5,
        }

    def test_initialization(self):
        """Test model initialization."""
        model = SEIZBMModel(self.graph, **self.params)

        # Check parameters are stored
        self.assertEqual(model.beta, 0.3)
        self.assertEqual(model.mu, 0.1)
        self.assertEqual(model.m, 0.5)

        # Check all nodes have agents initialized to S
        states = model.get_states()
        self.assertEqual(len(states), 50)
        self.assertTrue(all(state == "S" for state in states.values()))

    def test_initialize_states(self):
        """Test state initialization with fractions."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        counts = model.count_states()

        # Check fractions are approximately correct
        self.assertAlmostEqual(counts["I"], 5, delta=1)
        self.assertAlmostEqual(counts["Z"], 5, delta=1)
        self.assertGreater(counts["S"], 0)
        self.assertEqual(sum(counts.values()), 50)

    def test_initialize_states_reproducibility(self):
        """Test that same seed produces same initialization."""
        model1 = SEIZBMModel(self.graph, **self.params)
        model1.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states1 = model1.get_states()

        model2 = SEIZBMModel(self.graph, **self.params)
        model2.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states2 = model2.get_states()

        self.assertEqual(states1, states2)

    def test_step(self):
        """Test that step executes without error."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        initial_counts = model.count_states()
        model.step()
        after_counts = model.count_states()

        # Total should remain constant
        self.assertEqual(sum(initial_counts.values()), sum(after_counts.values()))

    def test_moderation_effect(self):
        """Test that moderation can convert infected to susceptible."""
        # Use high moderation rate
        high_mod_params = self.params.copy()
        high_mod_params["mu"] = 1.0  # Always moderate
        high_mod_params["m"] = 1.0  # Always succeed

        model = SEIZBMModel(self.graph, **high_mod_params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        # Run a few steps - infected should decrease
        initial_infected = model.count_states()["I"]

        for _ in range(10):
            model.step()

        final_infected = model.count_states()["I"]

        # With perfect moderation, infected should decrease or stay same
        self.assertLessEqual(final_infected, initial_infected)

    def test_run(self):
        """Test running simulation for multiple steps."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        history = model.run(steps=20)

        # Check history length (includes initial state)
        self.assertEqual(len(history), 21)

        # Check each history entry has required fields
        for h in history:
            self.assertIn("step", h)
            self.assertIn("S", h)
            self.assertIn("E", h)
            self.assertIn("I", h)
            self.assertIn("Z", h)

            # Total should be constant
            total = h["S"] + h["E"] + h["I"] + h["Z"]
            self.assertEqual(total, 50)

    def test_count_states(self):
        """Test state counting."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        counts = model.count_states()

        self.assertIn("S", counts)
        self.assertIn("E", counts)
        self.assertIn("I", counts)
        self.assertIn("Z", counts)
        self.assertEqual(sum(counts.values()), 50)

    def test_to_json(self):
        """Test JSON export."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=10)

        json_str = model.to_json()
        data = json.loads(json_str)

        # Check structure
        self.assertIn("model_type", data)
        self.assertEqual(data["model_type"], "SEIZBMModel")
        self.assertIn("parameters", data)
        self.assertIn("network_info", data)
        self.assertIn("history", data)

        # Check BM-specific parameters
        self.assertEqual(data["parameters"]["mu"], 0.1)
        self.assertEqual(data["parameters"]["m"], 0.5)

        # Check history
        self.assertEqual(len(data["history"]), 11)

    def test_save_json(self):
        """Test saving JSON to file."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=5)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            model.save_json(filepath)

            # Read and verify
            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertEqual(data["model_type"], "SEIZBMModel")
            self.assertEqual(len(data["history"]), 6)
        finally:
            os.unlink(filepath)

    def test_get_states(self):
        """Test retrieving agent states."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        states = model.get_states()

        self.assertEqual(len(states), 50)
        self.assertTrue(all(s in ["S", "E", "I", "Z"] for s in states.values()))

    def test_agent_attributes(self):
        """Test that agents have correct attributes."""
        model = SEIZBMModel(self.graph, **self.params)
        model.initialize_states(seed=123)

        # Check that all nodes have agents
        for node in self.graph.nodes():
            self.assertIn("agent", self.graph.nodes[node])
            agent = self.graph.nodes[node]["agent"]
            self.assertIn(agent.state, ["S", "E", "I", "Z"])


if __name__ == "__main__":
    unittest.main()
