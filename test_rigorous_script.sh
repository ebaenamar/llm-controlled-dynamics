#!/bin/bash
#
# Test del script de experimentos rigurosos
# Versión reducida para verificar que todo funciona
#

set -e

echo "================================"
echo "TEST: Rigorous Experiments Script"
echo "Started: $(date)"
echo "================================"
echo ""

# Activar entorno
source venv/bin/activate

# Verificar API key
if [ -z "$OPENROUTER_API_KEY" ]; then
    if [ -f .env ]; then
        export $(cat .env | grep -v '^#' | xargs)
    else
        echo "ERROR: No API key found"
        exit 1
    fi
fi

echo "✓ API key loaded: ${OPENROUTER_API_KEY:0:20}..."
echo ""

# Crear directorio de resultados de test
mkdir -p results/test
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results/test/${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "Results will be saved to: $RESULTS_DIR"
echo ""

# Test con solo 2 samples para verificar que funciona
echo "================================"
echo "TEST PHASE 1: Small Experiment"
echo "n=2 (solo para probar)"
echo "================================"
echo ""

MODEL="meta-llama/llama-3-8b-instruct"

echo "Running test experiment with $MODEL (n=2)..."
echo "This should take ~2 minutes and cost ~$0.02"
echo ""

# Ejecutar solo experimento A con 2 samples
python run_experiments.py \
    --experiments A \
    --custom "$MODEL" \
    --output "$RESULTS_DIR/test_${MODEL//\//_}.json"

echo "✓ Test experiment completed"
echo ""

# Verificar que se generó el archivo
if [ -f "$RESULTS_DIR/test_${MODEL//\//_}.json" ]; then
    echo "✓ Results file created successfully"
    echo "  File: $RESULTS_DIR/test_${MODEL//\//_}.json"
    echo "  Size: $(ls -lh "$RESULTS_DIR/test_${MODEL//\//_}.json" | awk '{print $5}')"
else
    echo "✗ ERROR: Results file not created"
    exit 1
fi

echo ""
echo "================================"
echo "TEST PHASE 2: Statistical Analysis"
echo "================================"
echo ""

# Verificar que el módulo de análisis estadístico funciona
echo "Testing statistical analysis module..."
python -c "
from src.experiments.statistical_analysis import StatisticalAnalysis
import numpy as np

# Test básico
control = [0.1, 0.12, 0.11]
modified = [0.05, 0.06, 0.04]

result = StatisticalAnalysis.ttest_independent(control, modified)
print(f'✓ Statistical analysis works')
print(f'  p-value: {result[\"p_value\"]:.4f}')
print(f'  Cohen\\'s d: {result[\"cohens_d\"]:.3f}')
"

echo ""
echo "================================"
echo "TEST PHASE 3: Visualization"
echo "================================"
echo ""

echo "Testing visualization module..."
python -c "
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Test simple plot
fig, ax = plt.subplots()
ax.bar(['A', 'B'], [0.1, 0.2])
plt.savefig('$RESULTS_DIR/test_plot.png')
plt.close()

print('✓ Visualization works')
print('  Test plot saved to: $RESULTS_DIR/test_plot.png')
"

echo ""
echo "================================"
echo "TEST COMPLETED SUCCESSFULLY"
echo "================================"
echo ""

cat << EOF
✅ All components verified:
  ✓ Environment activation
  ✓ API key loading
  ✓ Experiment execution
  ✓ Results file generation
  ✓ Statistical analysis module
  ✓ Visualization module

📁 Test results saved to: $RESULTS_DIR

🚀 Ready to run full experiments!

Next steps:
1. Review test results in: $RESULTS_DIR
2. If everything looks good, run:
   ./run_rigorous_experiments.sh (n=30, local)
   OR
   Transfer to remote server and run there

Total test time: $SECONDS seconds
EOF

echo ""
echo "Finished: $(date)"
