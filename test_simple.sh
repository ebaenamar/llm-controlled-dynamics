#!/bin/bash
#
# Test simple para verificar que todo funciona
#

set -e

echo "================================"
echo "SIMPLE TEST"
echo "================================"
echo ""

# Activar entorno
source venv/bin/activate

# Verificar API key
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

echo "✓ Environment activated"
echo "✓ API key loaded: ${OPENROUTER_API_KEY:0:20}..."
echo ""

# Test 1: Verificar que Python funciona
echo "Test 1: Python environment"
python -c "
import sys
print(f'  Python: {sys.version.split()[0]}')

import numpy as np
print(f'  NumPy: {np.__version__}')

import scipy
print(f'  SciPy: {scipy.__version__}')

import matplotlib
print(f'  Matplotlib: {matplotlib.__version__}')
"
echo "✓ Python environment OK"
echo ""

# Test 2: Verificar módulos del proyecto
echo "Test 2: Project modules"
python -c "
from src.core.openrouter_client import OpenRouterClient
from src.core.actions import TokenActions
from src.core.metrics import MetricSuite
from src.experiments.statistical_analysis import StatisticalAnalysis

print('  ✓ All modules import successfully')
"
echo ""

# Test 3: Verificar API connection
echo "Test 3: API connection (quick test)"
python -c "
from src.core.openrouter_client import OpenRouterClient, GenerationConfig

client = OpenRouterClient()
response = client.generate(
    'Say hello',
    'meta-llama/llama-3-8b-instruct',
    GenerationConfig(max_tokens=10, temperature=0.7)
)
print(f'  ✓ API works. Response: {response.text[:50]}...')
print(f'  ✓ Tokens used: {response.total_tokens}')
"
echo ""

# Test 4: Verificar statistical analysis
echo "Test 4: Statistical analysis"
python -c "
from src.experiments.statistical_analysis import StatisticalAnalysis
import numpy as np

control = [0.1, 0.12, 0.11, 0.13, 0.09]
modified = [0.05, 0.06, 0.04, 0.07, 0.05]

result = StatisticalAnalysis.ttest_independent(control, modified)
print(f'  ✓ t-test works')
print(f'    p-value: {result[\"p_value\"]:.4f}')
print(f'    Cohen\\'s d: {result[\"cohens_d\"]:.3f}')
print(f'    Significant: {result[\"significant\"]}')
"
echo ""

# Test 5: Verificar que run_experiments.py funciona
echo "Test 5: Run experiments script"
echo "  Running experiment A with small models..."
python run_experiments.py --experiment A --models small
echo "  ✓ Experiment completed"
echo ""

echo "================================"
echo "✅ ALL TESTS PASSED"
echo "================================"
echo ""
echo "System is ready for full experiments!"
echo ""
echo "Next steps:"
echo "1. Commit and push code (API key is in .gitignore)"
echo "2. Transfer to remote server: ./run_remote_experiments.sh"
echo "3. Run full experiments on server"
