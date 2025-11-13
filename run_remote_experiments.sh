#!/bin/bash
#
# Script para ejecutar experimentos en servidor remoto
# Uso: ./run_remote_experiments.sh
#

set -e

echo "================================"
echo "LLM CONTROLLED DYNAMICS"
echo "Remote Experiment Execution"
echo "================================"
echo ""

# Configuración
REMOTE_USER="nuwins-rack-2"
REMOTE_HOST="10.188.61.195"
REMOTE_DIR="/home/nuwins-rack-2/llm-controlled-dynamics"
LOCAL_DIR="/Users/e.baena/CascadeProjects/llm-controlled-dynamics"

echo "📦 Preparando archivos..."

# Crear tarball con el proyecto (excluyendo venv y resultados)
tar -czf /tmp/llm-dynamics.tar.gz \
    --exclude='venv' \
    --exclude='results' \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -C "$LOCAL_DIR/.." \
    llm-controlled-dynamics

echo "✓ Tarball creado"

echo ""
echo "📤 Transfiriendo a servidor remoto..."

# Transferir al servidor
scp /tmp/llm-dynamics.tar.gz ${REMOTE_USER}@${REMOTE_HOST}:/tmp/

echo "✓ Transferencia completada"

echo ""
echo "🚀 Configurando en servidor remoto..."

# Ejecutar setup en remoto
ssh ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
set -e

echo "Descomprimiendo proyecto..."
cd ~
rm -rf llm-controlled-dynamics
tar -xzf /tmp/llm-dynamics.tar.gz
cd llm-controlled-dynamics

echo "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Verificando instalación..."
python -c "import numpy; import scipy; print('✓ Dependencias OK')"

echo "✓ Setup completado"
ENDSSH

echo ""
echo "✅ Servidor configurado correctamente"
echo ""
echo "Opciones de ejecución:"
echo ""
echo "1. Experimentos con n=30 (rigor mínimo):"
echo "   ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd llm-controlled-dynamics && nohup ./run_rigorous_experiments.sh > experiments.log 2>&1 &'"
echo ""
echo "2. Experimentos con n=50 (rigor completo):"
echo "   ssh ${REMOTE_USER}@${REMOTE_HOST} 'cd llm-controlled-dynamics && nohup ./run_full_rigorous_experiments.sh > experiments.log 2>&1 &'"
echo ""
echo "3. Monitorear progreso:"
echo "   ssh ${REMOTE_USER}@${REMOTE_HOST} 'tail -f llm-controlled-dynamics/experiments.log'"
echo ""
echo "4. Descargar resultados:"
echo "   scp -r ${REMOTE_USER}@${REMOTE_HOST}:llm-controlled-dynamics/results ./results_remote"
echo ""

# Limpiar
rm /tmp/llm-dynamics.tar.gz

echo "🎯 Listo para ejecutar!"
