"""
SEIZ Epidemic Models Package

This package contains implementations of SEIZ (Susceptible-Exposed-Infected-Skeptic)
epidemic models for studying information spread on social networks.

Models:
    - SEIZModel: Basic SEIZ model
    - SEIZBMModel: SEIZ with Basic Moderator
    - SEIZSMModel: SEIZ with Smart Moderator
"""

from .base import BaseEpidemicModel
from .seiz import SEIZModel
from .seiz_bm import SEIZBMModel
from .seiz_sm import SEIZSMModel

__all__ = [
    "BaseEpidemicModel",
    "SEIZModel",
    "SEIZBMModel",
    "SEIZSMModel",
]

__version__ = "0.1.0"
