# LLM Controlled Dynamics: A NeurIPS-Style Framework

## Overview

This project implements a rigorous experimental framework to study Large Language Models as **controlled dynamical systems**. We define explicit interventions (actions) at token, embedding, and logit levels, and systematically measure how these perturbations affect internal trajectories and output distributions.

## Core Concept

We formalize an LLM as a dynamical system:

- **State**: `h_t^(ℓ) ∈ ℝ^d` (hidden states at layer ℓ, step t)
- **Dynamics**: `h_{t+1} = F_θ(h_{≤t}, x_{≤t})`
- **Control**: Actions `a_t` that modify states or inputs
- **Observables**: KL divergence, state distances, task metrics

## Experimental Design

### Action Types

1. **Token-level**: Insertion of unexpected tokens, substitution with rare tokens
2. **Embedding-level**: Directional perturbations, off-manifold noise
3. **Logit-level**: Bias towards low-probability tokens, tail distortion

### Canonical Test Case: "En un lugar de la Mancha..."

We use the opening of Don Quixote as a memorized attractor to study:
- Stability under perturbations
- Phase transitions in generation
- Layer-wise sensitivity
- Model size effects

## Project Structure

```
llm-controlled-dynamics/
├── src/
│   ├── core/
│   │   ├── openrouter_client.py    # Multi-model API client
│   │   ├── actions.py               # Action definitions
│   │   └── metrics.py               # Observable measurements
│   ├── experiments/
│   │   ├── quijote_experiments.py   # Specific experiments
│   │   └── comparative_analysis.py  # Multi-model comparison
│   └── visualization/
│       ├── trajectory_plots.py      # State space visualization
│       └── heatmaps.py              # Layer/magnitude impact maps
├── experiments/
│   └── configs/                     # Experiment configurations
├── results/                         # Output data and figures
└── notebooks/                       # Analysis notebooks
```

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```python
from src.experiments.quijote_experiments import QuijoteExperiments

# Initialize with OpenRouter API key
exp = QuijoteExperiments(api_key="your-key")

# Run token insertion experiment
results = exp.run_token_insertion_experiment(
    models=["gpt-4", "claude-3-opus", "llama-3-70b"]
)

# Analyze results
exp.analyze_stability_regimes(results)
```

## Key Experiments

1. **A: Token Insertion** - Insert `<ISO-2847>` before memorized text
2. **B: Rare Token Substitution** - Replace common token with `∮`
3. **C: Embedding Perturbation** - Add directional vector to embeddings
4. **D: Logit Tail Bias** - Amplify low-probability tokens
5. **E: Mid-sequence Shock** - Insert error token in middle of generation

## Metrics

- **State Distance**: `||h_t - h̃_t||_2` across layers
- **KL Divergence**: `KL(p(·|h_t) || p(·|h̃_t))`
- **Memorization Retention**: Exact match with canonical text
- **Trajectory Curvature**: Geometric properties in embedding space

## Citation

If you use this framework, please cite:

```bibtex
@article{llm_controlled_dynamics,
  title={Controlled Dynamics of Language Models: A Systematic Study of Interventions},
  author={},
  journal={},
  year={2025}
}
```

## License

MIT
