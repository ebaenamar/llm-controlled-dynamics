"""
Don Quixote Experiments: Canonical Memorized Text as Attractor

Implements the five core experiments:
A. Token Insertion - Insert unexpected token before memorized text
B. Rare Token Substitution - Replace common token with rare symbol
C. Embedding Perturbation - Add directional vector (simulated)
D. Logit Tail Bias - Amplify low-probability tokens
E. Mid-sequence Shock - Insert error token in middle of generation
"""

import os
import json
import time
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.openrouter_client import OpenRouterClient, GenerationConfig, ModelResponse
from core.actions import (
    Action, ActionType, TokenActions, EmbeddingActions, 
    LogitActions, ActionFactory
)
from core.metrics import MetricSuite, MetricResult


@dataclass
class ExperimentResult:
    """Results from a single experiment run."""
    experiment_type: str
    model: str
    action: Action
    prompt_control: str
    prompt_modified: str
    response_control: ModelResponse
    response_modified: ModelResponse
    metrics: Dict[str, float]
    timestamp: str
    
    def to_dict(self):
        """Convert to dictionary for serialization."""
        return {
            "experiment_type": self.experiment_type,
            "model": self.model,
            "action": {
                "type": self.action.action_type.value,
                "magnitude": self.action.magnitude,
                "position": self.action.position,
                "parameters": self.action.parameters
            },
            "prompt_control": self.prompt_control,
            "prompt_modified": self.prompt_modified,
            "response_control": {
                "text": self.response_control.text,
                "tokens": self.response_control.total_tokens
            },
            "response_modified": {
                "text": self.response_modified.text,
                "tokens": self.response_modified.total_tokens
            },
            "metrics": self.metrics,
            "timestamp": self.timestamp
        }


class QuijoteExperiments:
    """
    Experimental framework for studying LLM dynamics using Don Quixote.
    
    The opening line "En un lugar de la Mancha..." is a canonical memorized
    text that serves as a stable attractor for testing perturbations.
    """
    
    # Canonical text - the expected continuation
    CANONICAL_TEXT = (
        "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, "
        "no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, "
        "adarga antigua, rocín flaco y galgo corredor."
    )
    
    # Base prompt
    BASE_PROMPT = "En un lugar de la Mancha,"
    
    # Extended prompt for mid-sequence experiments
    EXTENDED_PROMPT = (
        "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, "
        "no ha mucho tiempo que vivía un hidalgo"
    )
    
    def __init__(self, api_key: Optional[str] = None, results_dir: str = "results"):
        """
        Initialize experiment framework.
        
        Args:
            api_key: OpenRouter API key
            results_dir: Directory to save results
        """
        self.client = OpenRouterClient(api_key)
        self.results_dir = results_dir
        os.makedirs(results_dir, exist_ok=True)
    
    def _run_control_and_modified(
        self,
        prompt_control: str,
        prompt_modified: str,
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> Tuple[ModelResponse, ModelResponse]:
        """
        Run both control and modified prompts.
        
        Args:
            prompt_control: Control prompt
            prompt_modified: Modified prompt
            model: Model identifier
            config: Generation config
            
        Returns:
            Tuple of (control_response, modified_response)
        """
        if config is None:
            config = GenerationConfig(max_tokens=150, temperature=0.7)
        
        # Control
        response_control = self.client.generate(prompt_control, model, config)
        time.sleep(0.5)
        
        # Modified
        response_modified = self.client.generate(prompt_modified, model, config)
        time.sleep(0.5)
        
        return response_control, response_modified
    
    def _compute_metrics(
        self,
        generated: str,
        canonical: str = None
    ) -> Dict[str, float]:
        """
        Compute all metrics for a generation.
        
        Args:
            generated: Generated text
            canonical: Canonical text (defaults to CANONICAL_TEXT)
            
        Returns:
            Dictionary of metric values
        """
        if canonical is None:
            canonical = self.CANONICAL_TEXT
        
        metrics = MetricSuite.compute_all_metrics(generated, canonical)
        return MetricSuite.summarize_metrics(metrics)
    
    def experiment_a_token_insertion(
        self,
        models: List[str],
        token: str = "<ISO-2847>",
        position: Optional[int] = None
    ) -> List[ExperimentResult]:
        """
        Experiment A: Insert unexpected token before memorized text.
        
        Tests how a single rare token disrupts the memorized attractor.
        
        Args:
            models: List of model identifiers
            token: Token to insert
            position: Position to insert (None = after base prompt)
            
        Returns:
            List of ExperimentResult objects
        """
        results = []
        
        prompt_control = self.BASE_PROMPT
        prompt_modified, action = TokenActions.insert_token(
            self.BASE_PROMPT,
            token=token,
            position=position
        )
        
        print(f"\n=== Experiment A: Token Insertion ===")
        print(f"Control: {prompt_control}")
        print(f"Modified: {prompt_modified}")
        print(f"Action: {action}\n")
        
        for model in models:
            print(f"Testing model: {model}")
            
            try:
                resp_control, resp_modified = self._run_control_and_modified(
                    prompt_control, prompt_modified, model
                )
                
                # Compute metrics
                metrics_control = self._compute_metrics(resp_control.text)
                metrics_modified = self._compute_metrics(resp_modified.text)
                
                # Create result
                result = ExperimentResult(
                    experiment_type="A_token_insertion",
                    model=model,
                    action=action,
                    prompt_control=prompt_control,
                    prompt_modified=prompt_modified,
                    response_control=resp_control,
                    response_modified=resp_modified,
                    metrics={
                        "control": metrics_control,
                        "modified": metrics_modified,
                        "delta_memorization": metrics_control["memorization"] - metrics_modified["memorization"],
                        "delta_kl": metrics_modified["kl_divergence"] - metrics_control["kl_divergence"]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
                
                print(f"  Control memorization: {metrics_control['memorization']:.3f}")
                print(f"  Modified memorization: {metrics_modified['memorization']:.3f}")
                print(f"  Delta: {result.metrics['delta_memorization']:.3f}\n")
                
            except Exception as e:
                print(f"  Error: {e}\n")
        
        return results
    
    def experiment_b_rare_token_substitution(
        self,
        models: List[str],
        target_word: str = "lugar",
        replacement: str = "∮"
    ) -> List[ExperimentResult]:
        """
        Experiment B: Substitute common token with rare symbol.
        
        Tests sensitivity to low-frequency token substitution.
        
        Args:
            models: List of model identifiers
            target_word: Word to replace
            replacement: Replacement token
            
        Returns:
            List of ExperimentResult objects
        """
        results = []
        
        prompt_control = self.BASE_PROMPT
        prompt_modified, action = TokenActions.substitute_token(
            self.BASE_PROMPT,
            target_word=target_word,
            replacement=replacement
        )
        
        print(f"\n=== Experiment B: Rare Token Substitution ===")
        print(f"Control: {prompt_control}")
        print(f"Modified: {prompt_modified}")
        print(f"Action: {action}\n")
        
        for model in models:
            print(f"Testing model: {model}")
            
            try:
                resp_control, resp_modified = self._run_control_and_modified(
                    prompt_control, prompt_modified, model
                )
                
                metrics_control = self._compute_metrics(resp_control.text)
                metrics_modified = self._compute_metrics(resp_modified.text)
                
                result = ExperimentResult(
                    experiment_type="B_rare_token_substitution",
                    model=model,
                    action=action,
                    prompt_control=prompt_control,
                    prompt_modified=prompt_modified,
                    response_control=resp_control,
                    response_modified=resp_modified,
                    metrics={
                        "control": metrics_control,
                        "modified": metrics_modified,
                        "delta_memorization": metrics_control["memorization"] - metrics_modified["memorization"],
                        "delta_kl": metrics_modified["kl_divergence"] - metrics_control["kl_divergence"]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
                
                print(f"  Control memorization: {metrics_control['memorization']:.3f}")
                print(f"  Modified memorization: {metrics_modified['memorization']:.3f}")
                print(f"  Delta: {result.metrics['delta_memorization']:.3f}\n")
                
            except Exception as e:
                print(f"  Error: {e}\n")
        
        return results
    
    def experiment_c_embedding_perturbation(
        self,
        models: List[str],
        direction: str = "technical",
        magnitude: float = 0.7
    ) -> List[ExperimentResult]:
        """
        Experiment C: Apply directional perturbation in embedding space.
        
        Simulated via style instructions that shift semantic direction.
        
        Args:
            models: List of model identifiers
            direction: Direction vector ('technical', 'poetic', etc.)
            magnitude: Perturbation strength (0.0 to 1.0)
            
        Returns:
            List of ExperimentResult objects
        """
        results = []
        
        prompt_control = self.BASE_PROMPT
        prompt_modified, action = EmbeddingActions.apply_directional_perturbation(
            self.BASE_PROMPT,
            direction=direction,
            magnitude=magnitude
        )
        
        print(f"\n=== Experiment C: Embedding Perturbation ===")
        print(f"Control: {prompt_control}")
        print(f"Modified: {prompt_modified}")
        print(f"Action: {action}\n")
        
        for model in models:
            print(f"Testing model: {model}")
            
            try:
                resp_control, resp_modified = self._run_control_and_modified(
                    prompt_control, prompt_modified, model
                )
                
                metrics_control = self._compute_metrics(resp_control.text)
                metrics_modified = self._compute_metrics(resp_modified.text)
                
                result = ExperimentResult(
                    experiment_type="C_embedding_perturbation",
                    model=model,
                    action=action,
                    prompt_control=prompt_control,
                    prompt_modified=prompt_modified,
                    response_control=resp_control,
                    response_modified=resp_modified,
                    metrics={
                        "control": metrics_control,
                        "modified": metrics_modified,
                        "delta_memorization": metrics_control["memorization"] - metrics_modified["memorization"],
                        "delta_kl": metrics_modified["kl_divergence"] - metrics_control["kl_divergence"]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
                
                print(f"  Control memorization: {metrics_control['memorization']:.3f}")
                print(f"  Modified memorization: {metrics_modified['memorization']:.3f}")
                print(f"  Delta: {result.metrics['delta_memorization']:.3f}\n")
                
            except Exception as e:
                print(f"  Error: {e}\n")
        
        return results
    
    def experiment_d_logit_tail_bias(
        self,
        models: List[str],
        magnitude: float = 0.8
    ) -> List[ExperimentResult]:
        """
        Experiment D: Bias towards low-probability tokens.
        
        Simulated via instruction to use unusual vocabulary.
        
        Args:
            models: List of model identifiers
            magnitude: Bias strength (0.0 to 1.0)
            
        Returns:
            List of ExperimentResult objects
        """
        results = []
        
        prompt_control = self.BASE_PROMPT
        modifier, action = LogitActions.amplify_tail(magnitude=magnitude)
        prompt_modified = modifier + prompt_control
        
        print(f"\n=== Experiment D: Logit Tail Bias ===")
        print(f"Control: {prompt_control}")
        print(f"Modified: {prompt_modified}")
        print(f"Action: {action}\n")
        
        for model in models:
            print(f"Testing model: {model}")
            
            try:
                resp_control, resp_modified = self._run_control_and_modified(
                    prompt_control, prompt_modified, model
                )
                
                metrics_control = self._compute_metrics(resp_control.text)
                metrics_modified = self._compute_metrics(resp_modified.text)
                
                result = ExperimentResult(
                    experiment_type="D_logit_tail_bias",
                    model=model,
                    action=action,
                    prompt_control=prompt_control,
                    prompt_modified=prompt_modified,
                    response_control=resp_control,
                    response_modified=resp_modified,
                    metrics={
                        "control": metrics_control,
                        "modified": metrics_modified,
                        "delta_memorization": metrics_control["memorization"] - metrics_modified["memorization"],
                        "delta_kl": metrics_modified["kl_divergence"] - metrics_control["kl_divergence"]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
                
                print(f"  Control memorization: {metrics_control['memorization']:.3f}")
                print(f"  Modified memorization: {metrics_modified['memorization']:.3f}")
                print(f"  Delta: {result.metrics['delta_memorization']:.3f}\n")
                
            except Exception as e:
                print(f"  Error: {e}\n")
        
        return results
    
    def experiment_e_midsequence_shock(
        self,
        models: List[str],
        token: str = "<X2F-ERROR>",
        position: Optional[int] = None
    ) -> List[ExperimentResult]:
        """
        Experiment E: Insert error token in middle of memorized sequence.
        
        Tests layer-wise sensitivity and recovery from perturbations.
        
        Args:
            models: List of model identifiers
            token: Token to insert
            position: Position in extended prompt
            
        Returns:
            List of ExperimentResult objects
        """
        results = []
        
        prompt_control = self.EXTENDED_PROMPT
        prompt_modified, action = TokenActions.insert_token(
            self.EXTENDED_PROMPT,
            token=token,
            position=position
        )
        
        print(f"\n=== Experiment E: Mid-sequence Shock ===")
        print(f"Control: {prompt_control}")
        print(f"Modified: {prompt_modified}")
        print(f"Action: {action}\n")
        
        for model in models:
            print(f"Testing model: {model}")
            
            try:
                resp_control, resp_modified = self._run_control_and_modified(
                    prompt_control, prompt_modified, model
                )
                
                metrics_control = self._compute_metrics(resp_control.text)
                metrics_modified = self._compute_metrics(resp_modified.text)
                
                result = ExperimentResult(
                    experiment_type="E_midsequence_shock",
                    model=model,
                    action=action,
                    prompt_control=prompt_control,
                    prompt_modified=prompt_modified,
                    response_control=resp_control,
                    response_modified=resp_modified,
                    metrics={
                        "control": metrics_control,
                        "modified": metrics_modified,
                        "delta_memorization": metrics_control["memorization"] - metrics_modified["memorization"],
                        "delta_kl": metrics_modified["kl_divergence"] - metrics_control["kl_divergence"]
                    },
                    timestamp=datetime.now().isoformat()
                )
                
                results.append(result)
                
                print(f"  Control memorization: {metrics_control['memorization']:.3f}")
                print(f"  Modified memorization: {metrics_modified['memorization']:.3f}")
                print(f"  Delta: {result.metrics['delta_memorization']:.3f}\n")
                
            except Exception as e:
                print(f"  Error: {e}\n")
        
        return results
    
    def run_all_experiments(
        self,
        models: List[str],
        save_results: bool = True
    ) -> Dict[str, List[ExperimentResult]]:
        """
        Run all five experiments on specified models.
        
        Args:
            models: List of model identifiers
            save_results: Whether to save results to disk
            
        Returns:
            Dictionary mapping experiment names to results
        """
        all_results = {}
        
        print(f"\n{'='*60}")
        print(f"Running all experiments on {len(models)} models")
        print(f"{'='*60}")
        
        all_results["A"] = self.experiment_a_token_insertion(models)
        all_results["B"] = self.experiment_b_rare_token_substitution(models)
        all_results["C"] = self.experiment_c_embedding_perturbation(models)
        all_results["D"] = self.experiment_d_logit_tail_bias(models)
        all_results["E"] = self.experiment_e_midsequence_shock(models)
        
        if save_results:
            self.save_results(all_results)
        
        return all_results
    
    def save_results(self, results: Dict[str, List[ExperimentResult]]):
        """
        Save experiment results to JSON.
        
        Args:
            results: Dictionary of experiment results
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_dir}/quijote_experiments_{timestamp}.json"
        
        # Convert to serializable format
        serializable = {}
        for exp_name, exp_results in results.items():
            serializable[exp_name] = [r.to_dict() for r in exp_results]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filename}")


if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize experiments
    exp = QuijoteExperiments()
    
    # Test with a few models
    test_models = [
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct"
    ]
    
    # Run single experiment
    results = exp.experiment_a_token_insertion(test_models)
    
    # Print results
    for result in results:
        print(f"\nModel: {result.model}")
        print(f"Control: {result.response_control.text[:100]}...")
        print(f"Modified: {result.response_modified.text[:100]}...")
        print(f"Memorization delta: {result.metrics['delta_memorization']:.3f}")
