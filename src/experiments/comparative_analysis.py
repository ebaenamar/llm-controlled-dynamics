"""
Comparative Analysis Across Model Sizes

Analyzes how different model sizes respond to the same perturbations,
looking for:
- Scaling laws in robustness
- Phase transitions
- Attractor strength vs model capacity
"""

import os
import json
import sys
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.openrouter_client import OpenRouterClient


class ComparativeAnalysis:
    """
    Analyze and compare results across model sizes.
    """
    
    MODEL_CATEGORIES = {
        "small": [
            "meta-llama/llama-3-8b-instruct",
            "mistralai/mistral-7b-instruct",
            "google/gemma-7b-it",
        ],
        "medium": [
            "meta-llama/llama-3-70b-instruct",
            "anthropic/claude-3-sonnet",
            "google/gemini-pro",
        ],
        "large": [
            "openai/gpt-4-turbo",
            "anthropic/claude-3-opus",
            "meta-llama/llama-3-405b-instruct",
        ]
    }
    
    def __init__(self, results_file: str = None):
        """
        Initialize analysis.
        
        Args:
            results_file: Path to results JSON file
        """
        self.results_file = results_file
        self.results = None
        
        if results_file and os.path.exists(results_file):
            self.load_results(results_file)
    
    def load_results(self, filepath: str):
        """Load results from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        print(f"Loaded results from {filepath}")
    
    def categorize_model(self, model_name: str) -> str:
        """
        Categorize a model by size.
        
        Args:
            model_name: Model identifier
            
        Returns:
            Category: 'small', 'medium', 'large', or 'unknown'
        """
        for category, models in self.MODEL_CATEGORIES.items():
            if any(m in model_name for m in models):
                return category
        return "unknown"
    
    def extract_metrics_by_experiment(self) -> Dict[str, pd.DataFrame]:
        """
        Extract metrics organized by experiment type.
        
        Returns:
            Dictionary mapping experiment names to DataFrames
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        dfs = {}
        
        for exp_name, exp_results in self.results.items():
            rows = []
            
            for result in exp_results:
                model = result["model"]
                category = self.categorize_model(model)
                
                row = {
                    "model": model,
                    "category": category,
                    "experiment": exp_name,
                }
                
                # Extract metrics
                if "metrics" in result:
                    metrics = result["metrics"]
                    
                    # Control metrics
                    if "control" in metrics:
                        for key, val in metrics["control"].items():
                            row[f"control_{key}"] = val
                    
                    # Modified metrics
                    if "modified" in metrics:
                        for key, val in metrics["modified"].items():
                            row[f"modified_{key}"] = val
                    
                    # Delta metrics
                    for key in ["delta_memorization", "delta_kl"]:
                        if key in metrics:
                            row[key] = metrics[key]
                
                rows.append(row)
            
            dfs[exp_name] = pd.DataFrame(rows)
        
        return dfs
    
    def compute_summary_statistics(self) -> pd.DataFrame:
        """
        Compute summary statistics across all experiments.
        
        Returns:
            DataFrame with summary stats by model and experiment
        """
        dfs = self.extract_metrics_by_experiment()
        
        summary_rows = []
        
        for exp_name, df in dfs.items():
            for category in ["small", "medium", "large"]:
                cat_df = df[df["category"] == category]
                
                if len(cat_df) == 0:
                    continue
                
                row = {
                    "experiment": exp_name,
                    "category": category,
                    "n_models": len(cat_df),
                    "mean_delta_memorization": cat_df["delta_memorization"].mean(),
                    "std_delta_memorization": cat_df["delta_memorization"].std(),
                    "mean_delta_kl": cat_df["delta_kl"].mean(),
                    "std_delta_kl": cat_df["delta_kl"].std(),
                    "mean_control_memorization": cat_df["control_memorization"].mean(),
                    "mean_modified_memorization": cat_df["modified_memorization"].mean(),
                }
                
                summary_rows.append(row)
        
        return pd.DataFrame(summary_rows)
    
    def identify_phase_transitions(self, threshold: float = 0.5) -> Dict[str, List[str]]:
        """
        Identify experiments where perturbations cause large changes.
        
        A "phase transition" is when delta_memorization > threshold.
        
        Args:
            threshold: Threshold for significant change
            
        Returns:
            Dictionary mapping experiments to models showing transitions
        """
        dfs = self.extract_metrics_by_experiment()
        
        transitions = {}
        
        for exp_name, df in dfs.items():
            # Find models with large delta
            large_delta = df[df["delta_memorization"].abs() > threshold]
            
            if len(large_delta) > 0:
                transitions[exp_name] = large_delta["model"].tolist()
        
        return transitions
    
    def rank_experiments_by_impact(self) -> pd.DataFrame:
        """
        Rank experiments by average impact on memorization.
        
        Returns:
            DataFrame with experiments ranked by impact
        """
        dfs = self.extract_metrics_by_experiment()
        
        impacts = []
        
        for exp_name, df in dfs.items():
            mean_delta = df["delta_memorization"].abs().mean()
            std_delta = df["delta_memorization"].std()
            max_delta = df["delta_memorization"].abs().max()
            
            impacts.append({
                "experiment": exp_name,
                "mean_impact": mean_delta,
                "std_impact": std_delta,
                "max_impact": max_delta,
                "n_models": len(df)
            })
        
        impact_df = pd.DataFrame(impacts)
        impact_df = impact_df.sort_values("mean_impact", ascending=False)
        
        return impact_df
    
    def compare_model_robustness(self) -> pd.DataFrame:
        """
        Compare robustness across models.
        
        Robustness = average memorization retention across all experiments.
        
        Returns:
            DataFrame with robustness scores by model
        """
        dfs = self.extract_metrics_by_experiment()
        
        # Aggregate across experiments
        all_data = pd.concat(dfs.values(), ignore_index=True)
        
        robustness = all_data.groupby("model").agg({
            "delta_memorization": ["mean", "std", "min", "max"],
            "modified_memorization": "mean",
            "control_memorization": "mean"
        }).reset_index()
        
        robustness.columns = [
            "model",
            "mean_delta", "std_delta", "min_delta", "max_delta",
            "mean_modified_mem", "mean_control_mem"
        ]
        
        # Add category
        robustness["category"] = robustness["model"].apply(self.categorize_model)
        
        # Robustness score: lower delta = more robust
        robustness["robustness_score"] = 1.0 - robustness["mean_delta"].abs()
        
        robustness = robustness.sort_values("robustness_score", ascending=False)
        
        return robustness
    
    def generate_report(self, output_file: str = "analysis_report.txt"):
        """
        Generate a comprehensive analysis report.
        
        Args:
            output_file: Path to save report
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        report = []
        report.append("=" * 80)
        report.append("LLM CONTROLLED DYNAMICS: COMPARATIVE ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary statistics
        report.append("## Summary Statistics by Experiment and Model Size")
        report.append("")
        summary = self.compute_summary_statistics()
        report.append(summary.to_string(index=False))
        report.append("")
        
        # Experiment impact ranking
        report.append("## Experiments Ranked by Impact")
        report.append("")
        impact = self.rank_experiments_by_impact()
        report.append(impact.to_string(index=False))
        report.append("")
        
        # Phase transitions
        report.append("## Phase Transitions (delta > 0.5)")
        report.append("")
        transitions = self.identify_phase_transitions(threshold=0.5)
        for exp, models in transitions.items():
            report.append(f"Experiment {exp}:")
            for model in models:
                report.append(f"  - {model}")
        report.append("")
        
        # Model robustness
        report.append("## Model Robustness Ranking")
        report.append("")
        robustness = self.compare_model_robustness()
        report.append(robustness[["model", "category", "robustness_score", "mean_delta"]].to_string(index=False))
        report.append("")
        
        # Save report
        report_text = "\n".join(report)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"Report saved to {output_file}")
        print("\n" + report_text)
        
        return report_text


def get_recommended_models() -> Dict[str, List[str]]:
    """
    Get recommended models for each size category.
    
    Returns:
        Dictionary mapping categories to model lists
    """
    return {
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


if __name__ == "__main__":
    # Example usage
    import glob
    
    # Find latest results file
    results_files = glob.glob("results/quijote_experiments_*.json")
    
    if results_files:
        latest_file = max(results_files, key=os.path.getctime)
        print(f"Analyzing: {latest_file}\n")
        
        analyzer = ComparativeAnalysis(latest_file)
        analyzer.generate_report("results/analysis_report.txt")
    else:
        print("No results files found. Run experiments first.")
        print("\nRecommended models for testing:")
        models = get_recommended_models()
        for category, model_list in models.items():
            print(f"\n{category.upper()}:")
            for model in model_list:
                print(f"  - {model}")
