# Guía de Ejecución Remota

**Servidor**: nuwins-rack-2@10.188.61.195

---

## 🚀 Setup Inicial (Una Sola Vez)

### 1. Transferir Proyecto al Servidor

```bash
cd /Users/e.baena/CascadeProjects/llm-controlled-dynamics
./run_remote_experiments.sh
```

Esto:
- Empaqueta el proyecto
- Lo transfiere al servidor
- Instala dependencias
- Configura el entorno

**Tiempo**: ~5 minutos

---

## 🎯 Opciones de Ejecución

### Opción 1: Rigor Mínimo (n=30) ⭐ RECOMENDADO

**Para**: Workshop/ArXiv  
**Tiempo**: 2-3 horas  
**Costo**: ~$1.50

```bash
# Iniciar experimentos en background
ssh nuwins-rack-2@10.188.61.195 << 'EOF'
cd llm-controlled-dynamics
nohup ./run_rigorous_experiments.sh > experiments.log 2>&1 &
echo "Experiments started. PID: $!"
EOF
```

**Qué hace**:
- 5 experimentos × 2 modelos × 30 samples = 300 generaciones
- Análisis estadístico automático
- Visualizaciones
- Reporte comparativo

### Opción 2: Rigor Completo (n=50 + Modelo Grande)

**Para**: NeurIPS/ICML  
**Tiempo**: 4-6 horas  
**Costo**: ~$3.50-4.50

```bash
# Iniciar experimentos completos
ssh nuwins-rack-2@10.188.61.195 << 'EOF'
cd llm-controlled-dynamics
nohup ./run_full_rigorous_experiments.sh > experiments_full.log 2>&1 &
echo "Full experiments started. PID: $!"
EOF
```

**Qué hace**:
- 5 experimentos × 3 modelos × 50 samples = 750 generaciones
- Incluye Llama-3-70B
- Validación de atractores
- Análisis multi-escala completo

---

## 📊 Monitoreo

### Ver Progreso en Tiempo Real

```bash
# Opción 1 (rigor mínimo)
ssh nuwins-rack-2@10.188.61.195 'tail -f llm-controlled-dynamics/experiments.log'

# Opción 2 (rigor completo)
ssh nuwins-rack-2@10.188.61.195 'tail -f llm-controlled-dynamics/experiments_full.log'
```

**Salir**: Ctrl+C (los experimentos siguen corriendo)

### Verificar que Está Corriendo

```bash
ssh nuwins-rack-2@10.188.61.195 'ps aux | grep run_rigorous'
```

### Ver Últimas Líneas del Log

```bash
ssh nuwins-rack-2@10.188.61.195 'tail -50 llm-controlled-dynamics/experiments.log'
```

---

## 📥 Descargar Resultados

### Cuando Terminen los Experimentos

```bash
# Ver qué resultados hay
ssh nuwins-rack-2@10.188.61.195 'ls -lh llm-controlled-dynamics/results/rigorous/'

# Descargar todo
scp -r nuwins-rack-2@10.188.61.195:llm-controlled-dynamics/results/rigorous ./results_remote

# O descargar solo el último
LATEST=$(ssh nuwins-rack-2@10.188.61.195 'ls -t llm-controlled-dynamics/results/rigorous/ | head -1')
scp -r nuwins-rack-2@10.188.61.195:llm-controlled-dynamics/results/rigorous/$LATEST ./results_remote
```

---

## 🔍 Verificación Rápida

### Antes de Descargar Todo, Ver Resumen

```bash
ssh nuwins-rack-2@10.188.61.195 'cat llm-controlled-dynamics/results/rigorous/*/EXECUTION_SUMMARY.txt'
```

### Ver Cuántos Archivos Se Generaron

```bash
ssh nuwins-rack-2@10.188.61.195 'find llm-controlled-dynamics/results/rigorous -type f | wc -l'
```

### Ver Tamaño Total

```bash
ssh nuwins-rack-2@10.188.61.195 'du -sh llm-controlled-dynamics/results/rigorous'
```

---

## 🛠️ Troubleshooting

### Si los Experimentos Fallan

```bash
# Ver errores en el log
ssh nuwins-rack-2@10.188.61.195 'grep -i error llm-controlled-dynamics/experiments.log'

# Ver últimas 100 líneas
ssh nuwins-rack-2@10.188.61.195 'tail -100 llm-controlled-dynamics/experiments.log'
```

### Si Necesitas Parar los Experimentos

```bash
# Encontrar el PID
ssh nuwins-rack-2@10.188.61.195 'ps aux | grep run_rigorous'

# Matar el proceso (reemplaza PID con el número real)
ssh nuwins-rack-2@10.188.61.195 'kill PID'
```

### Re-transferir Proyecto (si hiciste cambios)

```bash
# Desde tu máquina local
cd /Users/e.baena/CascadeProjects/llm-controlled-dynamics
./run_remote_experiments.sh
```

---

## 📋 Checklist de Ejecución

### Antes de Empezar

- [ ] Verificar que .env tiene la API key correcta
- [ ] Decidir nivel de rigor (Opción 1 o 2)
- [ ] Estimar tiempo disponible
- [ ] Confirmar presupuesto

### Durante la Ejecución

- [ ] Verificar que inició correctamente (primeros 5 min)
- [ ] Monitorear progreso ocasionalmente
- [ ] Verificar que no hay errores

### Después de Terminar

- [ ] Descargar resultados
- [ ] Verificar que todos los archivos están
- [ ] Revisar EXECUTION_SUMMARY.txt
- [ ] Generar análisis estadístico local (si necesario)

---

## 🎯 Comandos Rápidos (Copy-Paste)

### Setup + Iniciar Rigor Mínimo (Todo en Uno)

```bash
cd /Users/e.baena/CascadeProjects/llm-controlled-dynamics && \
./run_remote_experiments.sh && \
ssh nuwins-rack-2@10.188.61.195 << 'EOF'
cd llm-controlled-dynamics
nohup ./run_rigorous_experiments.sh > experiments.log 2>&1 &
echo "✓ Experiments started in background"
echo "Monitor with: ssh nuwins-rack-2@10.188.61.195 'tail -f llm-controlled-dynamics/experiments.log'"
EOF
```

### Monitorear + Descargar Cuando Termine

```bash
# Terminal 1: Monitorear
ssh nuwins-rack-2@10.188.61.195 'tail -f llm-controlled-dynamics/experiments.log'

# Cuando veas "EXECUTION COMPLETED", en Terminal 2:
LATEST=$(ssh nuwins-rack-2@10.188.61.195 'ls -t llm-controlled-dynamics/results/rigorous/ | head -1')
scp -r nuwins-rack-2@10.188.61.195:llm-controlled-dynamics/results/rigorous/$LATEST ./results_remote
echo "✓ Results downloaded to ./results_remote"
```

---

## 💡 Tips

1. **Usa `screen` o `tmux`** en el servidor para sesiones persistentes:
   ```bash
   ssh nuwins-rack-2@10.188.61.195
   screen -S experiments
   cd llm-controlled-dynamics
   ./run_rigorous_experiments.sh
   # Ctrl+A, D para detach
   # screen -r experiments para reattach
   ```

2. **Notificación cuando termine** (si tienes telegram/email configurado):
   ```bash
   ./run_rigorous_experiments.sh && echo "Experiments done!" | mail -s "LLM Dynamics" tu@email.com
   ```

3. **Backup automático**:
   ```bash
   # Añadir al final del script
   tar -czf results_backup_$(date +%Y%m%d).tar.gz results/
   ```

---

## 📊 Resultados Esperados

### Opción 1 (n=30)

```
results/rigorous/YYYYMMDD_HHMMSS/
├── rigorous_small_meta-llama_llama-3-8b-instruct.json
├── rigorous_small_meta-llama_llama-3-8b-instruct_statistical_report.txt
├── rigorous_small_mistralai_mistral-7b-instruct.json
├── rigorous_small_mistralai_mistral-7b-instruct_statistical_report.txt
├── analysis_report.txt
├── figures/
│   ├── memorization_delta_by_experiment.png
│   ├── kl_divergence_comparison.png
│   ├── control_vs_modified_scatter.png
│   ├── model_robustness_ranking.png
│   ├── heatmap_delta_memorization.png
│   └── heatmap_delta_kl.png
└── EXECUTION_SUMMARY.txt
```

### Opción 2 (n=50 + Large)

Todo lo anterior + :
```
├── full_rigorous_large_meta-llama_llama-3-70b-instruct.json
├── full_rigorous_large_meta-llama_llama-3-70b-instruct_statistical_report.txt
├── attractor_validation_*.json
├── multi_scale_comparison.txt
└── EXECUTIVE_SUMMARY.txt
```

---

## ✅ Listo para Ejecutar

**Comando recomendado para empezar AHORA**:

```bash
cd /Users/e.baena/CascadeProjects/llm-controlled-dynamics
./run_remote_experiments.sh
```

Luego elige Opción 1 (n=30) o Opción 2 (n=50 + large) según tu presupuesto y timeline.
