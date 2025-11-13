#!/usr/bin/env python3
"""
Run full model size comparison across all experiments.

This script runs all 5 experiments on models of different sizes
and generates comprehensive analysis and visualizations.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from experiments.quijote_experiments import QuijoteExperiments
from experiments.comparative_analysis import ComparativeAnalysis
from visualization.plots import ExperimentVisualizer


def main():
    print("\n" + "="*80)
    print("LLM CONTROLLED DYNAMICS - FULL MODEL COMPARISON")
    print("="*80 + "\n")
    
    load_dotenv()
    
    # Define model sets
    model_sets = {
        "small": [
            "meta-llama/llama-3-8b-instruct",
            "mistralai/mistral-7b-instruct",
        ],
        "medium": [
            "meta-llama/llama-3-70b-instruct",
            "anthropic/claude-3-sonnet",
        ],
        "large": [
            "openai/gpt-4-turbo",
            "anthropic/claude-3-opus",
        ]
    }
    
    # Ask user which sets to run
    print("Available model sets:")
    print("1. Small models (7-8B) - Fast, cheap (~$0.10)")
    print("2. Medium models (70B, Claude Sonnet) - Moderate (~$0.50)")
    print("3. Large models (GPT-4, Claude Opus) - Expensive (~$2-5)")
    print("4. All models - Comprehensive comparison (~$5-10)")
    print()
    
    choice = input("Select option (1-4) or press Enter for small models: ").strip()
    
    if choice == "2":
        models = model_sets["medium"]
        set_name = "medium"
    elif choice == "3":
        models = model_sets["large"]
        set_name = "large"
    elif choice == "4":
        models = []
        for model_list in model_sets.values():
            models.extend(model_list)
        set_name = "all"
    else:
        models = model_sets["small"]
        set_name = "small"
    
    print(f"\nRunning experiments on {set_name} models:")
    for model in models:
        print(f"  - {model}")
    print()
    
    # Estimate cost and time
    num_experiments = 5
    num_models = len(models)
    total_calls = num_experiments * num_models * 2  # control + modified
    
    if set_name == "small":
        est_cost = total_calls * 0.01
        est_time = total_calls * 3
    elif set_name == "medium":
        est_cost = total_calls * 0.05
        est_time = total_calls * 5
    else:
        est_cost = total_calls * 0.20
        est_time = total_calls * 8
    
    print(f"Estimated cost: ${est_cost:.2f}")
    print(f"Estimated time: {est_time/60:.1f} minutes")
    print()
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        return
    
    # Run experiments
    print("\n" + "="*80)
    print("RUNNING EXPERIMENTS")
    print("="*80 + "\n")
    
    exp = QuijoteExperiments()
    results = exp.run_all_experiments(models, save_results=True)
    
    # Find the results file
    import glob
    results_files = glob.glob("results/quijote_experiments_*.json")
    latest_file = max(results_files, key=os.path.getctime)
    
    print("\n" + "="*80)
    print("GENERATING ANALYSIS")
    print("="*80 + "\n")
    
    # Generate analysis
    analyzer = ComparativeAnalysis(latest_file)
    analyzer.generate_report("results/analysis_report.txt")
    
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80 + "\n")
    
    # Generate plots
    viz = ExperimentVisualizer(latest_file)
    viz.generate_all_plots()
    
    print("\n" + "="*80)
    print("COMPLETE!")
    print("="*80 + "\n")
    
    print("Results saved to:")
    print(f"  - Raw data: {latest_file}")
    print(f"  - Analysis: results/analysis_report.txt")
    print(f"  - Figures: results/figures/")
    print()
    
    print("Next steps:")
    print("1. Review analysis_report.txt for key findings")
    print("2. Check figures/ for publication-quality plots")
    print("3. Use data for NeurIPS paper manuscript")


if __name__ == "__main__":
    main()
