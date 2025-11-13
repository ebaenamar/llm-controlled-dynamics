#!/usr/bin/env python3
"""
Main script to run LLM Controlled Dynamics experiments.

Usage:
    python run_experiments.py --all                    # Run all experiments on default models
    python run_experiments.py --experiment A           # Run specific experiment
    python run_experiments.py --models small           # Run on small models only
    python run_experiments.py --custom model1 model2   # Run on custom models
"""

import argparse
import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from experiments.quijote_experiments import QuijoteExperiments
from experiments.comparative_analysis import ComparativeAnalysis, get_recommended_models


def main():
    parser = argparse.ArgumentParser(
        description="Run LLM Controlled Dynamics experiments"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all experiments (A-E)"
    )
    
    parser.add_argument(
        "--experiment",
        type=str,
        choices=["A", "B", "C", "D", "E"],
        help="Run specific experiment (A: token insertion, B: rare token, C: embedding, D: logit bias, E: mid-sequence)"
    )
    
    parser.add_argument(
        "--models",
        type=str,
        choices=["small", "medium", "large", "all"],
        default="small",
        help="Model size category to test"
    )
    
    parser.add_argument(
        "--custom",
        nargs="+",
        help="Custom list of model identifiers"
    )
    
    parser.add_argument(
        "--analyze",
        type=str,
        help="Analyze existing results file"
    )
    
    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save results to disk"
    )
    
    args = parser.parse_args()
    
    # Load environment
    load_dotenv()
    
    # Check API key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY not found in environment")
        print("Please set it in .env file or export it")
        sys.exit(1)
    
    # Analysis mode
    if args.analyze:
        print(f"Analyzing results from: {args.analyze}\n")
        analyzer = ComparativeAnalysis(args.analyze)
        analyzer.generate_report("results/analysis_report.txt")
        return
    
    # Determine models to test
    if args.custom:
        models = args.custom
        print(f"Testing custom models: {models}\n")
    else:
        recommended = get_recommended_models()
        
        if args.models == "all":
            models = []
            for category_models in recommended.values():
                models.extend(category_models)
        else:
            models = recommended.get(args.models, [])
        
        print(f"Testing {args.models} models: {models}\n")
    
    if not models:
        print("No models selected. Use --models or --custom")
        sys.exit(1)
    
    # Initialize experiments
    exp = QuijoteExperiments()
    
    # Run experiments
    if args.all:
        print("\n" + "="*80)
        print("RUNNING ALL EXPERIMENTS (A-E)")
        print("="*80 + "\n")
        
        results = exp.run_all_experiments(models, save_results=not args.no_save)
        
        # Print summary
        print("\n" + "="*80)
        print("EXPERIMENT SUMMARY")
        print("="*80 + "\n")
        
        for exp_name, exp_results in results.items():
            print(f"\nExperiment {exp_name}:")
            for result in exp_results:
                delta = result.metrics.get("delta_memorization", 0)
                print(f"  {result.model}: Δmem = {delta:.3f}")
    
    elif args.experiment:
        exp_name = args.experiment
        
        print(f"\n{'='*80}")
        print(f"RUNNING EXPERIMENT {exp_name}")
        print("="*80 + "\n")
        
        # Map experiment letter to method
        experiment_methods = {
            "A": exp.experiment_a_token_insertion,
            "B": exp.experiment_b_rare_token_substitution,
            "C": exp.experiment_c_embedding_perturbation,
            "D": exp.experiment_d_logit_tail_bias,
            "E": exp.experiment_e_midsequence_shock,
        }
        
        method = experiment_methods[exp_name]
        results = method(models)
        
        # Save if requested
        if not args.no_save:
            exp.save_results({exp_name: results})
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"EXPERIMENT {exp_name} SUMMARY")
        print("="*80 + "\n")
        
        for result in results:
            delta = result.metrics.get("delta_memorization", 0)
            print(f"{result.model}:")
            print(f"  Δ memorization: {delta:.3f}")
            print(f"  Control text: {result.response_control.text[:80]}...")
            print(f"  Modified text: {result.response_modified.text[:80]}...")
            print()
    
    else:
        print("Please specify --all or --experiment <A-E>")
        parser.print_help()


if __name__ == "__main__":
    main()
