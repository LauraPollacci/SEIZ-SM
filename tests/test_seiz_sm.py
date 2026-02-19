"""
Unit tests for the SEIZ-SM (Smart Moderator) model.
"""

import json
import os
import tempfile
import unittest

import networkx as nx

from seiz_models import SEIZSMModel


class TestSEIZSMModel(unittest.TestCase):
    """Test cases for SEIZSMModel."""

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
            "n": 10,
            "theta": 3,
            "T": 0.5,
            "eta": 0.5,
            "lambd": 0.2,
        }

    def test_initialization(self):
        """Test model initialization."""
        model = SEIZSMModel(self.graph, **self.params)

        # Check parameters are stored
        self.assertEqual(model.beta, 0.3)
        self.assertEqual(model.n, 10)
        self.assertEqual(model.theta, 3)
        self.assertEqual(model.T, 0.5)

        # Check all nodes have agents initialized to S
        states = model.get_states()
        self.assertEqual(len(states), 50)
        self.assertTrue(all(state == "S" for state in states.values()))

    def test_agent_profiles(self):
        """Test that agents have Dark Triad profiles."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(seed=123)

        # Check that all agents have profiles
        for node in self.graph.nodes():
            agent = self.graph.nodes[node]["agent"]
            self.assertEqual(len(agent.profile), 3)
            self.assertTrue(all(0 <= trait <= 1 for trait in agent.profile))
            self.assertEqual(agent.toxic_messages, 0)
            self.assertEqual(agent.activity_level, 0)

    def test_initialize_states(self):
        """Test state initialization with fractions."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        counts = model.count_states()

        # Check fractions are approximately correct
        self.assertAlmostEqual(counts["I"], 5, delta=1)
        self.assertAlmostEqual(counts["Z"], 5, delta=1)
        self.assertGreater(counts["S"], 0)
        self.assertEqual(sum(counts.values()), 50)

    def test_initialize_states_reproducibility(self):
        """Test that same seed produces same initialization."""
        model1 = SEIZSMModel(self.graph, **self.params)
        model1.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states1 = model1.get_states()

        model2 = SEIZSMModel(self.graph, **self.params)
        model2.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=42)
        states2 = model2.get_states()

        self.assertEqual(states1, states2)

    def test_compute_toxicity(self):
        """Test toxicity computation."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(seed=123)

        # Get an agent and compute toxicity
        node = list(self.graph.nodes())[0]
        agent = self.graph.nodes[node]["agent"]

        toxicity = model.compute_toxicity(agent)

        # Toxicity should be between 0 and 1 (average of profile)
        self.assertGreaterEqual(toxicity, 0.0)
        self.assertLessEqual(toxicity, 1.0)

        # Check it matches manual calculation
        expected = sum(agent.profile) / 3.0
        self.assertAlmostEqual(toxicity, expected)

    def test_step(self):
        """Test that step executes without error."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        initial_counts = model.count_states()
        model.step()
        after_counts = model.count_states()

        # Total should remain constant
        self.assertEqual(sum(initial_counts.values()), sum(after_counts.values()))

    def test_send_messages(self):
        """Test message sending functionality."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        # Send messages
        toxic_senders = model.send_messages()

        # Should be a list
        self.assertIsInstance(toxic_senders, list)

        # At least some agents should have increased activity
        total_activity = sum(
            self.graph.nodes[node]["agent"].activity_level for node in self.graph.nodes()
        )
        self.assertGreater(total_activity, 0)

    def test_toxic_message_tracking(self):
        """Test that toxic messages are tracked."""
        # Use high toxicity threshold to ensure tracking
        high_tox_params = self.params.copy()
        high_tox_params["T"] = 0.0  # Everything is toxic
        high_tox_params["theta"] = 100  # High threshold for intervention

        model = SEIZSMModel(self.graph, **high_tox_params)
        model.initialize_states(infected_frac=0.4, skeptic_frac=0.0, seed=123)

        # Run a few steps
        for _ in range(5):
            model.step()

        # Check that some infected agents have toxic messages
        total_toxic = sum(
            self.graph.nodes[node]["agent"].toxic_messages
            for node in self.graph.nodes()
            if self.graph.nodes[node]["agent"].state == "I"
        )

        # With T=0, all messages from infected should be toxic
        self.assertGreater(total_toxic, 0)

    def test_run(self):
        """Test running simulation for multiple steps."""
        model = SEIZSMModel(self.graph, **self.params)
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
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        counts = model.count_states()

        self.assertIn("S", counts)
        self.assertIn("E", counts)
        self.assertIn("I", counts)
        self.assertIn("Z", counts)
        self.assertEqual(sum(counts.values()), 50)

    def test_to_json(self):
        """Test JSON export."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=10)

        json_str = model.to_json()
        data = json.loads(json_str)

        # Check structure
        self.assertIn("model_type", data)
        self.assertEqual(data["model_type"], "SEIZSMModel")
        self.assertIn("parameters", data)
        self.assertIn("network_info", data)
        self.assertIn("history", data)

        # Check SM-specific parameters
        self.assertEqual(data["parameters"]["n"], 10)
        self.assertEqual(data["parameters"]["theta"], 3)
        self.assertEqual(data["parameters"]["T"], 0.5)

        # Check history
        self.assertEqual(len(data["history"]), 11)

    def test_save_json(self):
        """Test saving JSON to file."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)
        model.run(steps=5)

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            model.save_json(filepath)

            # Read and verify
            with open(filepath, "r") as f:
                data = json.load(f)

            self.assertEqual(data["model_type"], "SEIZSMModel")
            self.assertEqual(len(data["history"]), 6)
        finally:
            os.unlink(filepath)

    def test_get_states(self):
        """Test retrieving agent states."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.1, skeptic_frac=0.1, seed=123)

        states = model.get_states()

        self.assertEqual(len(states), 50)
        self.assertTrue(all(s in ["S", "E", "I", "Z"] for s in states.values()))

    def test_moderator_intervention(self):
        """Test smart moderator intervention."""
        model = SEIZSMModel(self.graph, **self.params)
        model.initialize_states(infected_frac=0.2, skeptic_frac=0.0, seed=123)

        # Get an infected agent and set high toxic messages
        infected_node = None
        for node in self.graph.nodes():
            if self.graph.nodes[node]["agent"].state == "I":
                infected_node = node
                break

        if infected_node is not None:
            agent = self.graph.nodes[infected_node]["agent"]
            agent.toxic_messages = 10  # Above threshold

            initial_state = agent.state
            model.moderator_intervention(agent)

            # State might change or toxic messages reset
            # (depends on probability, but at least no error)
            self.assertIn(agent.state, ["S", "E", "I", "Z"])


if __name__ == "__main__":
    unittest.main()
