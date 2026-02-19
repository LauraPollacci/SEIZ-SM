# Evaluating Moderation in Online Social Networks

[![CI](https://github.com/GiulioRossetti/Eval_Moderation_OSN/actions/workflows/ci.yml/badge.svg)](https://github.com/GiulioRossetti/Eval_Moderation_OSN/actions/workflows/ci.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/badge/License-BSD_2--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

This package provides implementations of SEIZ (Susceptible-Exposed-Infected-Skeptic) epidemic models for studying information spread and content moderation on social networks.

## Models

The package includes three epidemic models:

1. **SEIZModel**: Basic SEIZ model without moderation
2. **SEIZBMModel**: SEIZ with Basic Moderator
3. **SEIZSMModel**: SEIZ with Smart Moderator (using Dark Triad personality profiles)

All models share a common interface for:
- Instantiation with parameters
- State initialization
- Step-wise execution
- JSON output
- Visualization (trend plots and network animations)

## Installation
### From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/GiulioRossetti/Eval_Moderation_OSN.git
cd Eval_Moderation_OSN
pip install -r requirements.txt
```

## Quick Start

The following examples demonstrate how to use each model.

### Basic SEIZ Model

```python
import networkx as nx
from seiz_models import SEIZModel

# Create a social network
G = nx.erdos_renyi_graph(200, 0.05, seed=42)

# Initialize the model
model = SEIZModel(
    graph=G,
    beta=0.6,   # S-I contact rate
    b=0.3,      # S-Z contact rate
    rho=0.2,    # E->I transition rate
    eps=0.05,   # I->E transition rate
    p=0.4,      # Probability S->I after contact
    l=0.6,      # Probability S->Z after contact
    dt=1.0      # Time step
)

# Initialize states (10% infected, 5% skeptic)
model.initialize_states(infected_frac=0.1, skeptic_frac=0.05, seed=123)

# Run simulation for 100 steps
history = model.run(steps=100)

# Visualize results
model.plot()

# Create an animated visualization of epidemic spreading
anim = model.animate_network(steps=50, interval=200)

# Save animation (requires ffmpeg for MP4 or pillow for GIF)
# model.animate_network(steps=50, save_path='epidemic_spread.gif')

# Export to JSON
model.save_json('results.json')
```

### SEIZ-BM Model (Basic Moderator)

```python
import networkx as nx
from seiz_models import SEIZBMModel

# Create a social network
G = nx.erdos_renyi_graph(150, 0.04, seed=42)

# Initialize the model with moderation
model = SEIZBMModel(
    graph=G,
    beta=0.3,      # S-I contact rate
    b=0.1,         # S-Z contact rate
    rho=0.2,       # E-I contact rate
    p=0.5,         # Probability S->I
    epsilon=0.2,   # Incubation rate E->I
    l=0.3,         # Probability S->Z
    mu=0.1,        # Moderator intervention rate
    m=0.5          # Successful moderation probability
)

# Initialize and run
model.initialize_states(infected_frac=0.05, skeptic_frac=0.05, seed=42)
history = model.run(steps=100)

# Visualize and save
model.plot(title="SEIZ-BM with Moderation")
model.save_json('seiz_bm_results.json')
```

### SEIZ-SM Model (Smart Moderator)

```python
import networkx as nx
from seiz_models import SEIZSMModel

# Create a social network
G = nx.erdos_renyi_graph(200, 0.03, seed=42)

# Initialize smart moderator model
model = SEIZSMModel(
    graph=G,
    beta=0.3,      # S-I contact rate
    b=0.1,         # S-Z contact rate
    rho=0.2,       # E-I contact rate
    p=0.5,         # Probability S->I
    epsilon=0.2,   # Incubation rate
    l=0.3,         # Probability S->Z
    n=30,          # Messages per timestep
    theta=3,       # Toxic message threshold
    T=0.5,         # Toxicity threshold
    eta=0.5,       # Probability I->E after moderation
    lambd=0.2      # Probability E->Z
)

# Initialize and run
model.initialize_states(infected_frac=0.05, skeptic_frac=0.05, seed=42)
history = model.run(steps=100)

# Visualize and export
model.plot(title="SEIZ-SM with Smart Moderation")
model.save_json('seiz_sm_results.json')
```

## JSON Output Format

All models export results in a standardized JSON format:

```json
{
  "model_type": "SEIZModel",
  "parameters": {
    "beta": 0.6,
    "b": 0.3,
    ...
  },
  "network_info": {
    "num_nodes": 200,
    "num_edges": 975
  },
  "history": [
    {
      "step": 0,
      "S": 170,
      "E": 0,
      "I": 20,
      "Z": 10
    },
    ...
  ]
}
```

## Visualization

### Static Plots

Generate time series plots of state evolution:

```python
model.plot()  # Display plot
model.save_plot('epidemic_dynamics.png')  # Save to file
```

### Network Animation

Visualize epidemic spreading over the network structure:

```python
# Generate animation
anim = model.animate_network(
    steps=50,          # Number of simulation steps
    interval=200,      # Delay between frames (ms)
    figsize=(10, 10),  # Figure size
    node_size=100,     # Node size
    seed=42            # Layout seed for reproducibility
)

# Save animation as GIF (requires pillow)
model.animate_network(steps=50, save_path='spread.gif')

# Save as MP4 (requires ffmpeg)
model.animate_network(steps=50, save_path='spread.mp4')
```

The animation shows nodes colored by state:
- **Blue**: Susceptible (S)
- **Orange**: Exposed (E)
- **Red**: Infected (I)
- **Green**: Skeptic (Z)

## Running Tests

Run all unit tests:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## Model States

All models use the SEIZ framework with four states:

- **S (Susceptible)**: Can be infected or become skeptic
- **E (Exposed)**: Infected but not yet spreading
- **I (Infected)**: Actively spreading information/misinformation
- **Z (Skeptic)**: Resistant to infection, can spread skepticism

## Development

### Setting up Development Environment

To contribute to this project, install development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Code Formatting

This project uses `black` and `isort` for code formatting. To set up pre-commit hooks:

```bash
pre-commit install
```

This will automatically format your code on each commit. To manually format all files:

```bash
black seiz_models tests examples
isort seiz_models tests examples
```

### CI/CD Pipeline

The project uses GitHub Actions for continuous integration and deployment:

- **CI Workflow**: Runs on every push and pull request
  - Linting with black and isort
  - Tests across Python 3.8-3.12
  - Code coverage reporting
  - Distribution build validation

- **PyPI Publishing**: Automated publishing to PyPI
  - Triggered on release creation
  - Manual dispatch for testing on TestPyPI
  - Uses API token authentication

#### Setting up PyPI Secrets

To enable PyPI publishing, configure the following GitHub secrets:
- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your TestPyPI API token (optional, for testing)

Generate tokens at:
- PyPI: https://pypi.org/manage/account/token/
- TestPyPI: https://test.pypi.org/manage/account/token/

#### Publishing a Release

To publish a new release:
1. Update version in `setup.py`
2. Create a new release on GitHub with a version tag (e.g., `v0.1.0`)
3. The workflow automatically builds and publishes to PyPI

For manual publishing to TestPyPI:
1. Go to Actions → Publish to PyPI → Run workflow
2. Select "testpypi" and run

## License

See LICENSE file for details.

## Citation 
If you use this package in your research, please cite:

```
@article{your2024seiz,
  title={Evaluating Moderation in Online Social Networks},
  author={Milli Letizia and Pollacci Laura and Guidotti Riccardo},
  journal={ },
  year={2025},
}
```

Models implementations by: [Giulio Rossetti](https://giuliorossetti.github.io/)

## Acknowledgements

This work is supported by:
- PRIN 2022 framework project PIANO, under CUP B53D23013290006; 
- Italian Project Fondo Italiano per la Scienza FIS00001966 MIMOSA;  
- NextGenerationEU – National Recovery and Resilience Plan (Piano Nazionale  di Ripresa e Resilienza, PNRR) – Project: “SoBigData.it - Strengthening the Italian RI for Social Mining and Big Data Analytics” – Prot. IR0000013 – Avviso n. 3264 del 28/12/2021.