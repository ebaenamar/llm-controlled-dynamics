# Quick Start Guide

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/e.baena/CascadeProjects/llm-controlled-dynamics
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure API Key

Your OpenRouter API key is already in `.env`:
```
OPENROUTER_API_KEY=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
```

### 3. Test the Framework

```bash
python quickstart.py
```

This runs a single experiment to verify everything works.

---

## Run Experiments

### Run All Experiments on Small Models (Recommended First)

```bash
python run_experiments.py --all --models small
```

**Models tested:**
- `meta-llama/llama-3-8b-instruct`
- `mistralai/mistral-7b-instruct`

**Time:** ~5-10 minutes  
**Cost:** ~$0.10-0.20

---

### Run Specific Experiment

```bash
# Experiment A: Token Insertion
python run_experiments.py --experiment A --models small

# Experiment B: Rare Token Substitution
python run_experiments.py --experiment B --models small

# Experiment C: Embedding Perturbation
python run_experiments.py --experiment C --models small

# Experiment D: Logit Tail Bias
python run_experiments.py --experiment D --models small

# Experiment E: Mid-sequence Shock
python run_experiments.py --experiment E --models small
```

---

### Compare Model Sizes

```bash
# Small models (7-8B parameters)
python run_experiments.py --all --models small

# Medium models (70B parameters, Claude Sonnet)
python run_experiments.py --all --models medium

# Large models (GPT-4, Claude Opus, Llama 405B)
python run_experiments.py --all --models large

# All models (comprehensive comparison)
python run_experiments.py --all --models all
```

**Warning:** Large models are expensive! Estimate ~$1-5 for full suite.

---

### Custom Models

```bash
python run_experiments.py --all --custom \
  "openai/gpt-4-turbo" \
  "anthropic/claude-3-opus" \
  "meta-llama/llama-3-70b-instruct"
```

---

## Analyze Results

### Generate Analysis Report

```bash
python run_experiments.py --analyze results/quijote_experiments_TIMESTAMP.json
```

This creates `results/analysis_report.txt` with:
- Summary statistics by experiment and model size
- Experiments ranked by impact
- Phase transitions (large perturbations)
- Model robustness ranking

---

### Generate Visualizations

```bash
python -m src.visualization.plots
```

Creates publication-quality figures in `results/figures/`:
- `memorization_delta_by_experiment.png` - Bar chart of memorization loss
- `kl_divergence_comparison.png` - KL divergence distributions
- `control_vs_modified_scatter.png` - Scatter plot showing perturbation effects
- `model_robustness_ranking.png` - Models ranked by robustness
- `heatmap_delta_memorization.png` - Experiment × Model heatmap
- `heatmap_delta_kl.png` - KL divergence heatmap

---

## Understanding the Experiments

### Experiment A: Token Insertion
**Prompt:** `En un lugar de la Mancha, <ISO-2847> de cuyo nombre...`

Tests how a single unexpected token disrupts memorized text.

### Experiment B: Rare Token Substitution
**Prompt:** `En un ∮ de la Mancha,`

Replaces common word with rare symbol to test sensitivity.

### Experiment C: Embedding Perturbation
**Prompt:** `(Rewrite in technical language:) En un lugar de la Mancha,`

Simulates directional perturbation in embedding space.

### Experiment D: Logit Tail Bias
**Prompt:** `(Use unusual words) En un lugar de la Mancha,`

Biases generation towards low-probability tokens.

### Experiment E: Mid-sequence Shock
**Prompt:** `En un lugar de la Mancha, ... <X2F-ERROR> ... hidalgo`

Inserts error token mid-sequence to test recovery.

---

## Key Metrics

- **Memorization Score** (0-1): How well the model reproduces canonical text
- **Δ Memorization**: Change in memorization (negative = loss of memorization)
- **KL Divergence**: Distribution shift between control and modified
- **Token Overlap**: Jaccard similarity of output tokens
- **Divergence Point**: Where generation deviates from canonical text

---

## Expected Results

### Robust Models
- Small Δ memorization (<0.2)
- Recovers canonical text despite perturbations
- Low KL divergence

### Fragile Models
- Large Δ memorization (>0.5)
- Generates creative/alternative text
- High KL divergence

### Phase Transitions
- Sudden shift from memorized → creative at certain perturbation strengths
- Different models have different transition points

---

## Troubleshooting

### API Errors
```bash
# Check your API key
echo $OPENROUTER_API_KEY

# Test connection
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer $OPENROUTER_API_KEY"
```

### Rate Limits
Add delays between requests in `src/core/openrouter_client.py`:
```python
time.sleep(1.0)  # Increase from 0.5 to 1.0
```

### Out of Memory
Use smaller models or reduce `max_tokens` in `.env`:
```
MAX_TOKENS=100
```

---

## Next Steps

1. **Run full comparison:** `python run_experiments.py --all --models all`
2. **Analyze results:** Check `results/analysis_report.txt`
3. **Create visualizations:** `python -m src.visualization.plots`
4. **Explore data:** Results are in JSON format for custom analysis
5. **Write paper:** Use results to support NeurIPS-style manuscript

---

## File Structure

```
results/
├── quijote_experiments_TIMESTAMP.json  # Raw experiment data
├── analysis_report.txt                 # Statistical analysis
└── figures/                            # Publication-quality plots
    ├── memorization_delta_by_experiment.png
    ├── kl_divergence_comparison.png
    ├── control_vs_modified_scatter.png
    ├── model_robustness_ranking.png
    ├── heatmap_delta_memorization.png
    └── heatmap_delta_kl.png
```

---

## Cost Estimates

| Model Size | Per Experiment | Full Suite (5 exp) |
|------------|----------------|-------------------|
| Small      | $0.01-0.02     | $0.05-0.10        |
| Medium     | $0.05-0.10     | $0.25-0.50        |
| Large      | $0.20-0.50     | $1.00-2.50        |

**Recommendation:** Start with small models, then scale up for final paper results.
