"""
Visualization tools for LLM dynamics experiments.

Creates publication-quality figures for NeurIPS-style papers:
- Heatmaps of impact vs layer/magnitude
- Trajectory plots in state space
- Comparative bar charts across models
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import Dict, List, Optional
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_palette("husl")


class ExperimentVisualizer:
    """Create visualizations from experiment results."""
    
    def __init__(self, results_file: str = None):
        """
        Initialize visualizer.
        
        Args:
            results_file: Path to results JSON
        """
        self.results = None
        self.figures_dir = "results/figures"
        os.makedirs(self.figures_dir, exist_ok=True)
        
        if results_file:
            self.load_results(results_file)
    
    def load_results(self, filepath: str):
        """Load results from JSON."""
        with open(filepath, 'r', encoding='utf-8') as f:
            self.results = json.load(f)
        print(f"Loaded results from {filepath}")
    
    def plot_memorization_delta_by_experiment(
        self,
        save_path: Optional[str] = None
    ):
        """
        Plot memorization delta for each experiment type.
        
        Args:
            save_path: Path to save figure
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        # Extract data
        data = []
        for exp_name, exp_results in self.results.items():
            for result in exp_results:
                data.append({
                    "Experiment": exp_name,
                    "Model": result["model"].split("/")[-1][:20],
                    "Δ Memorization": result["metrics"].get("delta_memorization", 0)
                })
        
        df = pd.DataFrame(data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.barplot(
            data=df,
            x="Experiment",
            y="Δ Memorization",
            hue="Model",
            ax=ax
        )
        
        ax.set_title("Memorization Loss by Experiment Type", fontsize=14, fontweight='bold')
        ax.set_xlabel("Experiment", fontsize=12)
        ax.set_ylabel("Δ Memorization Score", fontsize=12)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        ax.legend(title="Model", bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f"{self.figures_dir}/memorization_delta_by_experiment.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved figure: {save_path}")
        plt.close()
    
    def plot_kl_divergence_comparison(
        self,
        save_path: Optional[str] = None
    ):
        """
        Plot KL divergence across experiments.
        
        Args:
            save_path: Path to save figure
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        # Extract data
        data = []
        for exp_name, exp_results in self.results.items():
            for result in exp_results:
                data.append({
                    "Experiment": exp_name,
                    "Model": result["model"].split("/")[-1][:20],
                    "KL Divergence": result["metrics"].get("delta_kl", 0)
                })
        
        df = pd.DataFrame(data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 6))
        
        sns.boxplot(
            data=df,
            x="Experiment",
            y="KL Divergence",
            ax=ax
        )
        
        ax.set_title("KL Divergence by Experiment Type", fontsize=14, fontweight='bold')
        ax.set_xlabel("Experiment", fontsize=12)
        ax.set_ylabel("Δ KL Divergence", fontsize=12)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f"{self.figures_dir}/kl_divergence_comparison.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved figure: {save_path}")
        plt.close()
    
    def plot_control_vs_modified_scatter(
        self,
        save_path: Optional[str] = None
    ):
        """
        Scatter plot: control memorization vs modified memorization.
        
        Args:
            save_path: Path to save figure
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        # Extract data
        data = []
        for exp_name, exp_results in self.results.items():
            for result in exp_results:
                metrics = result["metrics"]
                data.append({
                    "Experiment": exp_name,
                    "Control Memorization": metrics.get("control", {}).get("memorization", 0),
                    "Modified Memorization": metrics.get("modified", {}).get("memorization", 0)
                })
        
        df = pd.DataFrame(data)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(8, 8))
        
        for exp in df["Experiment"].unique():
            exp_df = df[df["Experiment"] == exp]
            ax.scatter(
                exp_df["Control Memorization"],
                exp_df["Modified Memorization"],
                label=exp,
                alpha=0.7,
                s=100
            )
        
        # Diagonal line (no change)
        lims = [0, 1]
        ax.plot(lims, lims, 'k--', alpha=0.3, zorder=0)
        
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_xlabel("Control Memorization", fontsize=12)
        ax.set_ylabel("Modified Memorization", fontsize=12)
        ax.set_title("Control vs Modified Memorization", fontsize=14, fontweight='bold')
        ax.legend(title="Experiment")
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f"{self.figures_dir}/control_vs_modified_scatter.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved figure: {save_path}")
        plt.close()
    
    def plot_model_robustness_ranking(
        self,
        save_path: Optional[str] = None
    ):
        """
        Bar chart ranking models by robustness.
        
        Args:
            save_path: Path to save figure
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        # Compute robustness per model
        model_deltas = {}
        
        for exp_name, exp_results in self.results.items():
            for result in exp_results:
                model = result["model"].split("/")[-1][:30]
                delta = abs(result["metrics"].get("delta_memorization", 0))
                
                if model not in model_deltas:
                    model_deltas[model] = []
                model_deltas[model].append(delta)
        
        # Average delta per model
        model_robustness = {
            model: 1.0 - np.mean(deltas)
            for model, deltas in model_deltas.items()
        }
        
        # Sort by robustness
        sorted_models = sorted(
            model_robustness.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        models = [m for m, _ in sorted_models]
        scores = [s for _, s in sorted_models]
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        bars = ax.barh(models, scores, color=sns.color_palette("viridis", len(models)))
        
        ax.set_xlabel("Robustness Score", fontsize=12)
        ax.set_ylabel("Model", fontsize=12)
        ax.set_title("Model Robustness Ranking", fontsize=14, fontweight='bold')
        ax.set_xlim([0, 1])
        
        # Add value labels
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(
                score + 0.02,
                i,
                f"{score:.3f}",
                va='center',
                fontsize=9
            )
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = f"{self.figures_dir}/model_robustness_ranking.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved figure: {save_path}")
        plt.close()
    
    def plot_heatmap_experiment_vs_model(
        self,
        metric: str = "delta_memorization",
        save_path: Optional[str] = None
    ):
        """
        Heatmap: experiments vs models.
        
        Args:
            metric: Metric to visualize
            save_path: Path to save figure
        """
        if not self.results:
            raise ValueError("No results loaded")
        
        # Build matrix
        experiments = sorted(self.results.keys())
        models = set()
        
        for exp_results in self.results.values():
            for result in exp_results:
                models.add(result["model"].split("/")[-1][:25])
        
        models = sorted(models)
        
        # Create matrix
        matrix = np.zeros((len(experiments), len(models)))
        
        for i, exp_name in enumerate(experiments):
            for result in self.results[exp_name]:
                model = result["model"].split("/")[-1][:25]
                j = models.index(model)
                matrix[i, j] = result["metrics"].get(metric, 0)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        sns.heatmap(
            matrix,
            xticklabels=models,
            yticklabels=experiments,
            annot=True,
            fmt=".3f",
            cmap="RdYlGn_r",
            center=0,
            ax=ax,
            cbar_kws={"label": metric.replace("_", " ").title()}
        )
        
        ax.set_title(f"{metric.replace('_', ' ').title()} Heatmap", fontsize=14, fontweight='bold')
        ax.set_xlabel("Model", fontsize=12)
        ax.set_ylabel("Experiment", fontsize=12)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if save_path is None:
            save_path = f"{self.figures_dir}/heatmap_{metric}.png"
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved figure: {save_path}")
        plt.close()
    
    def generate_all_plots(self):
        """Generate all standard plots."""
        print("\nGenerating all visualizations...\n")
        
        self.plot_memorization_delta_by_experiment()
        self.plot_kl_divergence_comparison()
        self.plot_control_vs_modified_scatter()
        self.plot_model_robustness_ranking()
        self.plot_heatmap_experiment_vs_model("delta_memorization")
        self.plot_heatmap_experiment_vs_model("delta_kl")
        
        print(f"\nAll figures saved to {self.figures_dir}/")


if __name__ == "__main__":
    import glob
    
    # Find latest results
    results_files = glob.glob("results/quijote_experiments_*.json")
    
    if results_files:
        latest_file = max(results_files, key=os.path.getctime)
        print(f"Visualizing: {latest_file}\n")
        
        viz = ExperimentVisualizer(latest_file)
        viz.generate_all_plots()
    else:
        print("No results files found. Run experiments first.")
