"""Setup script for SEIZ epidemic models package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="seiz-models",
    version="0.1.0",
    author="Giulio Rossetti",
    author_email="giulio.rossetti@gmail.com",
    description="SEIZ epidemic models for information spread on social networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GiulioRossetti/Eval_Moderation_OSN",
    project_urls={
        "Bug Tracker": "https://github.com/GiulioRossetti/Eval_Moderation_OSN/issues",
        "Documentation": "https://github.com/GiulioRossetti/Eval_Moderation_OSN#readme",
        "Source Code": "https://github.com/GiulioRossetti/Eval_Moderation_OSN",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="epidemic-models, information-spread, social-networks, moderation, seiz",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=24.0.0",
            "isort>=5.13.0",
            "pre-commit>=3.5.0",
        ],
        "animation": [
            "pillow>=9.0.0",
        ],
    },
)
