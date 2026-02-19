"""
Unit tests for the basic SEIZ model.
"""

import json
import os
import tempfile
import unittest

import networkx as nx

from seiz_models import SEIZModel


class TestSEIZModel(unittest.TestCase):
    """Test cases for SEIZModel."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a small test network
        self.graph = nx.erdos_renyi_graph(50, 0.1, seed=42)

        # Standard parameters
        self.params = {"beta": 0.3, "b": 0.2, "rho": 0.2, "eps": 0.1, "p": 0.5, "l": 0.4, "dt": 1.0}

    def test_initialization(self):
        """Test model initialization."""
        model = SEIZModel(self.graph, **self.params)

        # Check parameters are stored
        self.assertEqual(model.beta, 0.3)
        self.assertEqual(model.b, 0.2)
        self.assertEqual(model.rho, 0.2)

        # Check all nodes are initialized to S
        states = model.get_states()
        self.assertEqual(len(states), 50)
        self.assertTrue(all(state == "S" for state in states.values()))

    def test_initialize_states(self):
        """Test state initialization with fractions."""
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        counts = model.count_states()

        # Check fractions are approximately correct
        self.assertAlmostEqual(counts["I"], 5, delta=1)
        self.assertAlmostEqual(counts["Z"], 5, delta=1)
        self.assertGreater(counts["S"], 0)
        self.assertEqual(sum(counts.values()), 50)

    def test_initialize_states_reproducibility(self):
        """Test that same seed produces same initialization."""
        model1 = SEIZModel(self.graph, **self.params)
        model1.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states1 = model1.get_states()

        model2 = SEIZModel(self.graph, **self.params)
        model2.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states2 = model2.get_states()

        self.assertEqual(states1, states2)

    def test_step(self):
        """Test that step executes without error."""
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        initial_counts = model.count_states()
        model.step()
        after_counts = model.count_states()

        # Total should remain constant
        self.assertEqual(sum(initial_counts.values()), sum(after_counts.values()))

    def test_run(self):
        """Test running simulation for multiple steps."""
        model = SEIZModel(self.graph, **self.params)
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
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        counts = model.count_states()

        self.assertIn("S", counts)
        self.assertIn("E", counts)
        self.assertIn("I", counts)
        self.assertIn("Z", counts)
        self.assertEqual(sum(counts.values()), 50)

    def test_to_json(self):
        """Test JSON export."""
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=10)

        json_str = model.to_json()
        data = json.loads(json_str)

        # Check structure
        self.assertIn("model_type", data)
        self.assertEqual(data["model_type"], "SEIZModel")
        self.assertIn("parameters", data)
        self.assertIn("network_info", data)
        self.assertIn("history", data)

        # Check parameters
        self.assertEqual(data["parameters"]["beta"], 0.3)

        # Check network info
        self.assertEqual(data["network_info"]["num_nodes"], 50)

        # Check history
        self.assertEqual(len(data["history"]), 11)

    def test_save_json(self):
        """Test saving JSON to file."""
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=5)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            model.save_json(filepath)

            # Read and verify
            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertEqual(data["model_type"], "SEIZModel")
            self.assertEqual(len(data["history"]), 6)
        finally:
            os.unlink(filepath)

    def test_get_states(self):
        """Test retrieving agent states."""
        model = SEIZModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        states = model.get_states()

        self.assertEqual(len(states), 50)
        self.assertTrue(all(s in ["S", "E", "I", "Z"] for s in states.values()))

    def test_empty_graph(self):
        """Test behavior with empty graph."""
        empty_graph = nx.Graph()
        model = SEIZModel(empty_graph, **self.params)

        counts = model.count_states()
        self.assertEqual(sum(counts.values()), 0)

        history = model.run(steps=5)
        self.assertEqual(len(history), 6)


if __name__ == "__main__":
    unittest.main()
