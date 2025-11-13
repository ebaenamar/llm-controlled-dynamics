#!/bin/bash
#
# Experimentos con rigor estadístico (n=30)
# Para ejecutar en servidor remoto en background
#

set -e

echo "================================"
echo "RIGOROUS EXPERIMENTS (n=30)"
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

echo "✓ API key loaded"
echo ""

# Crear directorio de resultados
mkdir -p results/rigorous
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="results/rigorous/${TIMESTAMP}"
mkdir -p "$RESULTS_DIR"

echo "Results will be saved to: $RESULTS_DIR"
echo ""

# Función para ejecutar experimentos con múltiples samples
run_experiment_batch() {
    local model=$1
    local n_samples=$2
    local exp_name=$3
    
    echo "Running $exp_name with $model (n=$n_samples)..."
    
    python run_experiments.py \
        --all \
        --custom "$model" \
        --samples "$n_samples" \
        --output "$RESULTS_DIR/${exp_name}_${model//\//_}.json"
    
    echo "✓ Completed $exp_name with $model"
    echo ""
}

# Modelos a probar
MODELS=(
    "meta-llama/llama-3-8b-instruct"
    "mistralai/mistral-7b-instruct"
)

echo "================================"
echo "PHASE 1: Small Models (n=30)"
echo "================================"
echo ""

for model in "${MODELS[@]}"; do
    echo "Model: $model"
    echo "Samples per condition: 30"
    echo "Estimated time: 45-60 minutes"
    echo "Estimated cost: $0.50"
    echo ""
    
    run_experiment_batch "$model" 30 "rigorous_small"
done

echo ""
echo "================================"
echo "PHASE 2: Statistical Analysis"
echo "================================"
echo ""

echo "Generating statistical reports..."

for result_file in "$RESULTS_DIR"/*.json; do
    echo "Analyzing: $result_file"
    python -m src.experiments.statistical_analysis "$result_file"
done

echo "✓ Statistical analysis completed"
echo ""

echo "================================"
echo "PHASE 3: Visualizations"
echo "================================"
echo ""

echo "Generating publication-quality figures..."
python -m src.visualization.plots "$RESULTS_DIR"

echo "✓ Visualizations completed"
echo ""

echo "================================"
echo "PHASE 4: Comparative Analysis"
echo "================================"
echo ""

echo "Generating comparative report..."
python run_experiments.py --analyze "$RESULTS_DIR"/*.json

echo "✓ Analysis completed"
echo ""

# Crear resumen
SUMMARY_FILE="$RESULTS_DIR/EXECUTION_SUMMARY.txt"

cat > "$SUMMARY_FILE" << EOF
LLM CONTROLLED DYNAMICS - RIGOROUS EXPERIMENTS
===============================================

Execution Date: $(date)
Samples per condition: 30
Models tested: ${#MODELS[@]}

Models:
$(printf '  - %s\n' "${MODELS[@]}")

Results Directory: $RESULTS_DIR

Files Generated:
$(ls -lh "$RESULTS_DIR" | tail -n +2)

Total Execution Time: $SECONDS seconds

Next Steps:
1. Review statistical reports (*_statistical_report.txt)
2. Check visualizations in figures/
3. Read comparative analysis (analysis_report.txt)
4. Download results to local machine:
   scp -r nuwins-rack-2@10.188.61.195:llm-controlled-dynamics/$RESULTS_DIR ./results_remote

EOF

echo ""
echo "================================"
echo "EXECUTION COMPLETED"
echo "================================"
echo ""
cat "$SUMMARY_FILE"
echo ""
echo "Total time: $SECONDS seconds"
echo "Finished: $(date)"
