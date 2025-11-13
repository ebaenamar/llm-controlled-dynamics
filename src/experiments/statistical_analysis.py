"""
Statistical Analysis for LLM Controlled Dynamics

Provides rigorous statistical tests for experimental results.
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
import pandas as pd


class StatisticalAnalysis:
    """Rigorous statistical analysis for experiments."""
    
    @staticmethod
    def compute_confidence_interval(
        data: List[float],
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Compute mean and confidence interval.
        
        Returns:
            (mean, lower_bound, upper_bound)
        """
        data = np.array(data)
        mean = np.mean(data)
        sem = stats.sem(data)
        ci = sem * stats.t.ppf((1 + confidence) / 2, len(data) - 1)
        
        return mean, mean - ci, mean + ci
    
    @staticmethod
    def ttest_independent(
        group1: List[float],
        group2: List[float],
        alternative: str = 'two-sided'
    ) -> Dict:
        """
        Independent samples t-test.
        
        Args:
            group1: First group of measurements
            group2: Second group of measurements
            alternative: 'two-sided', 'less', or 'greater'
            
        Returns:
            Dictionary with test results
        """
        t_stat, p_value = stats.ttest_ind(group1, group2, alternative=alternative)
        
        # Effect size (Cohen's d)
        mean1, mean2 = np.mean(group1), np.mean(group2)
        std1, std2 = np.std(group1, ddof=1), np.std(group2, ddof=1)
        n1, n2 = len(group1), len(group2)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
        
        # Confidence intervals
        ci1 = StatisticalAnalysis.compute_confidence_interval(group1)
        ci2 = StatisticalAnalysis.compute_confidence_interval(group2)
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size_interpretation': StatisticalAnalysis._interpret_cohens_d(cohens_d),
            'significant': p_value < 0.05,
            'group1_mean': mean1,
            'group1_ci': ci1,
            'group2_mean': mean2,
            'group2_ci': ci2,
            'mean_difference': mean1 - mean2
        }
    
    @staticmethod
    def _interpret_cohens_d(d: float) -> str:
        """Interpret Cohen's d effect size."""
        abs_d = abs(d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"
    
    @staticmethod
    def anova_oneway(
        groups: Dict[str, List[float]]
    ) -> Dict:
        """
        One-way ANOVA for multiple groups.
        
        Args:
            groups: Dictionary mapping group names to measurements
            
        Returns:
            Dictionary with ANOVA results
        """
        group_data = list(groups.values())
        f_stat, p_value = stats.f_oneway(*group_data)
        
        # Eta-squared (effect size for ANOVA)
        all_data = np.concatenate(group_data)
        grand_mean = np.mean(all_data)
        
        ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in group_data)
        ss_total = np.sum((all_data - grand_mean)**2)
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'eta_squared': eta_squared,
            'significant': p_value < 0.05,
            'group_means': {name: np.mean(data) for name, data in groups.items()}
        }
    
    @staticmethod
    def bonferroni_correction(
        p_values: List[float],
        alpha: float = 0.05
    ) -> Dict:
        """
        Bonferroni correction for multiple comparisons.
        
        Args:
            p_values: List of p-values from multiple tests
            alpha: Significance level
            
        Returns:
            Dictionary with corrected results
        """
        n_tests = len(p_values)
        corrected_alpha = alpha / n_tests
        
        return {
            'original_alpha': alpha,
            'corrected_alpha': corrected_alpha,
            'n_tests': n_tests,
            'significant_tests': sum(p < corrected_alpha for p in p_values),
            'corrected_significant': [p < corrected_alpha for p in p_values]
        }
    
    @staticmethod
    def bootstrap_ci(
        data: List[float],
        statistic=np.mean,
        n_bootstrap: int = 10000,
        confidence: float = 0.95
    ) -> Tuple[float, float, float]:
        """
        Bootstrap confidence interval.
        
        Args:
            data: Data to bootstrap
            statistic: Function to compute (default: mean)
            n_bootstrap: Number of bootstrap samples
            confidence: Confidence level
            
        Returns:
            (statistic, lower_bound, upper_bound)
        """
        data = np.array(data)
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_stats.append(statistic(sample))
        
        bootstrap_stats = np.array(bootstrap_stats)
        alpha = 1 - confidence
        
        lower = np.percentile(bootstrap_stats, 100 * alpha / 2)
        upper = np.percentile(bootstrap_stats, 100 * (1 - alpha / 2))
        stat = statistic(data)
        
        return stat, lower, upper
    
    @staticmethod
    def power_analysis(
        effect_size: float,
        alpha: float = 0.05,
        power: float = 0.8
    ) -> int:
        """
        Compute required sample size for desired power.
        
        Args:
            effect_size: Expected Cohen's d
            alpha: Significance level
            power: Desired statistical power
            
        Returns:
            Required sample size per group
        """
        from statsmodels.stats.power import TTestIndPower
        
        analysis = TTestIndPower()
        n = analysis.solve_power(
            effect_size=effect_size,
            alpha=alpha,
            power=power,
            alternative='two-sided'
        )
        
        return int(np.ceil(n))
    
    @staticmethod
    def analyze_experiment_results(
        control_scores: List[float],
        modified_scores: List[float],
        experiment_name: str = "Experiment"
    ) -> Dict:
        """
        Complete statistical analysis for one experiment.
        
        Args:
            control_scores: Scores from control condition
            modified_scores: Scores from modified condition
            experiment_name: Name for reporting
            
        Returns:
            Complete analysis dictionary
        """
        # Basic statistics
        control_mean, control_lower, control_upper = \
            StatisticalAnalysis.compute_confidence_interval(control_scores)
        modified_mean, modified_lower, modified_upper = \
            StatisticalAnalysis.compute_confidence_interval(modified_scores)
        
        # T-test
        ttest_results = StatisticalAnalysis.ttest_independent(
            control_scores,
            modified_scores
        )
        
        # Bootstrap CI for difference
        differences = np.array(control_scores) - np.array(modified_scores)
        diff_mean, diff_lower, diff_upper = \
            StatisticalAnalysis.bootstrap_ci(differences)
        
        return {
            'experiment': experiment_name,
            'control': {
                'mean': control_mean,
                'ci_lower': control_lower,
                'ci_upper': control_upper,
                'n': len(control_scores)
            },
            'modified': {
                'mean': modified_mean,
                'ci_lower': modified_lower,
                'ci_upper': modified_upper,
                'n': len(modified_scores)
            },
            'difference': {
                'mean': diff_mean,
                'ci_lower': diff_lower,
                'ci_upper': diff_upper
            },
            'statistical_test': ttest_results,
            'interpretation': StatisticalAnalysis._interpret_results(ttest_results)
        }
    
    @staticmethod
    def _interpret_results(ttest_results: Dict) -> str:
        """Generate human-readable interpretation."""
        p = ttest_results['p_value']
        d = ttest_results['cohens_d']
        effect = ttest_results['effect_size_interpretation']
        
        if p < 0.001:
            sig_str = "highly significant (p < 0.001)"
        elif p < 0.01:
            sig_str = "very significant (p < 0.01)"
        elif p < 0.05:
            sig_str = "significant (p < 0.05)"
        else:
            sig_str = "not significant (p ≥ 0.05)"
        
        return f"The difference is {sig_str} with a {effect} effect size (d = {d:.3f})."


def generate_statistical_report(results_file: str) -> str:
    """
    Generate a comprehensive statistical report from experiment results.
    
    Args:
        results_file: Path to JSON results file
        
    Returns:
        Formatted statistical report
    """
    import json
    
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    report = []
    report.append("="*80)
    report.append("STATISTICAL ANALYSIS REPORT")
    report.append("="*80)
    report.append("")
    
    # Analyze each experiment
    for exp_name, exp_data in data.items():
        if not isinstance(exp_data, list):
            continue
        
        report.append(f"\n{'='*80}")
        report.append(f"Experiment {exp_name}")
        report.append(f"{'='*80}\n")
        
        # Group by model
        by_model = {}
        for result in exp_data:
            model = result['model']
            if model not in by_model:
                by_model[model] = {'control': [], 'modified': []}
            
            by_model[model]['control'].append(
                result['metrics']['memorization_control']
            )
            by_model[model]['modified'].append(
                result['metrics']['memorization_modified']
            )
        
        # Analyze each model
        for model, scores in by_model.items():
            if len(scores['control']) < 2 or len(scores['modified']) < 2:
                continue
            
            analysis = StatisticalAnalysis.analyze_experiment_results(
                scores['control'],
                scores['modified'],
                f"{exp_name} - {model}"
            )
            
            report.append(f"Model: {model}")
            report.append(f"  Control: {analysis['control']['mean']:.3f} "
                         f"[{analysis['control']['ci_lower']:.3f}, "
                         f"{analysis['control']['ci_upper']:.3f}]")
            report.append(f"  Modified: {analysis['modified']['mean']:.3f} "
                         f"[{analysis['modified']['ci_lower']:.3f}, "
                         f"{analysis['modified']['ci_upper']:.3f}]")
            report.append(f"  Difference: {analysis['difference']['mean']:.3f} "
                         f"[{analysis['difference']['ci_lower']:.3f}, "
                         f"{analysis['difference']['ci_upper']:.3f}]")
            report.append(f"  {analysis['interpretation']}")
            report.append("")
    
    return "\n".join(report)


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        report = generate_statistical_report(sys.argv[1])
        print(report)
        
        # Save report
        output_file = sys.argv[1].replace('.json', '_statistical_report.txt')
        with open(output_file, 'w') as f:
            f.write(report)
        print(f"\nReport saved to: {output_file}")
