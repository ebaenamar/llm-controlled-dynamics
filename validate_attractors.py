#!/usr/bin/env python3
"""
Validate Canonical Attractors

Tests which attractors are actually memorized by different models.
This helps select the best attractors for experiments.
"""

import os
import sys
from dotenv import load_dotenv
import json
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.canonical_attractors import CanonicalAttractors, Attractor
from core.openrouter_client import OpenRouterClient, GenerationConfig
from core.metrics import TextMetrics


def validate_attractor(
    attractor: Attractor,
    model: str,
    client: OpenRouterClient,
    prompt_length: int = 10
) -> dict:
    """
    Validate a single attractor with a model.
    
    Args:
        attractor: The attractor to test
        model: Model identifier
        client: OpenRouter client
        prompt_length: Number of words to use as prompt
        
    Returns:
        Dictionary with validation results
    """
    # Create prompt from first N words
    words = attractor.text.split()
    prompt = " ".join(words[:prompt_length])
    
    # Generate completion
    config = GenerationConfig(
        max_tokens=attractor.tokens_approx * 2,
        temperature=0.0  # Deterministic for memorization test
    )
    
    try:
        response = client.generate(prompt, model, config)
        
        # Compute memorization metrics
        mem_score = TextMetrics.memorization_score(
            response.text,
            attractor.text
        )
        
        prefix_match = TextMetrics.prefix_match_length(
            response.text,
            attractor.text
        )
        
        token_overlap = TextMetrics.token_overlap(
            response.text,
            attractor.text
        )
        
        exact_match = TextMetrics.exact_match(
            response.text,
            attractor.text
        )
        
        return {
            "success": True,
            "prompt": prompt,
            "response": response.text,
            "memorization_score": mem_score.value,
            "exact_match": exact_match.value,
            "token_overlap": token_overlap.value,
            "word_prefix_match": prefix_match.metadata["word_match"],
            "is_memorized": mem_score.value >= 0.8,
            "expected_memorization": attractor.expected_memorization,
            "delta_from_expected": mem_score.value - attractor.expected_memorization
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "memorization_score": 0.0,
            "is_memorized": False
        }


def validate_suite(
    models: list[str],
    suite_size: str = "minimal",
    output_file: str = None
):
    """
    Validate a suite of attractors across models.
    
    Args:
        models: List of model identifiers
        suite_size: "minimal", "standard", or "comprehensive"
        output_file: Path to save results JSON
    """
    load_dotenv()
    client = OpenRouterClient()
    attractors_cls = CanonicalAttractors()
    
    # Get attractor suite
    suite = attractors_cls.get_recommended_suite(suite_size)
    
    print(f"\n{'='*80}")
    print(f"VALIDATING {len(suite)} ATTRACTORS ON {len(models)} MODELS")
    print(f"{'='*80}\n")
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "suite_size": suite_size,
        "models": models,
        "attractors": {}
    }
    
    for attr_name, attractor in suite.items():
        print(f"\n{'='*80}")
        print(f"Attractor: {attr_name}")
        print(f"Source: {attractor.source}")
        print(f"Expected memorization: {attractor.expected_memorization:.2f}")
        print(f"Text: {attractor.text[:100]}...")
        print(f"{'='*80}\n")
        
        results["attractors"][attr_name] = {
            "source": attractor.source,
            "category": attractor.category,
            "language": attractor.language,
            "expected_memorization": attractor.expected_memorization,
            "text": attractor.text,
            "models": {}
        }
        
        for model in models:
            print(f"Testing {model}... ", end="", flush=True)
            
            result = validate_attractor(attractor, model, client)
            results["attractors"][attr_name]["models"][model] = result
            
            if result["success"]:
                mem = result["memorization_score"]
                is_mem = "✓" if result["is_memorized"] else "✗"
                print(f"{is_mem} Memorization: {mem:.3f}")
                
                if mem < 0.5:
                    print(f"  ⚠️  Low memorization! Response: {result['response'][:80]}...")
            else:
                print(f"✗ Error: {result['error']}")
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    
    for model in models:
        memorized_count = sum(
            1 for attr_data in results["attractors"].values()
            if attr_data["models"][model].get("is_memorized", False)
        )
        total = len(suite)
        pct = (memorized_count / total) * 100
        
        print(f"{model}:")
        print(f"  Memorized: {memorized_count}/{total} ({pct:.1f}%)")
        
        # Average memorization score
        avg_mem = sum(
            attr_data["models"][model].get("memorization_score", 0)
            for attr_data in results["attractors"].values()
        ) / total
        print(f"  Avg memorization score: {avg_mem:.3f}")
        print()
    
    # Best attractors (high memorization across all models)
    print("\nBEST ATTRACTORS (highest avg memorization):")
    attr_scores = []
    for attr_name, attr_data in results["attractors"].items():
        avg_score = sum(
            attr_data["models"][m].get("memorization_score", 0)
            for m in models
        ) / len(models)
        attr_scores.append((attr_name, avg_score, attr_data["source"]))
    
    attr_scores.sort(key=lambda x: x[1], reverse=True)
    for i, (name, score, source) in enumerate(attr_scores[:5], 1):
        print(f"{i}. {name} ({source[:40]}...): {score:.3f}")
    
    # Worst attractors
    print("\nWORST ATTRACTORS (lowest avg memorization):")
    for i, (name, score, source) in enumerate(attr_scores[-3:], 1):
        print(f"{i}. {name} ({source[:40]}...): {score:.3f}")
    
    # Save results
    if output_file is None:
        output_file = f"results/attractor_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate canonical attractors")
    parser.add_argument(
        "--models",
        nargs="+",
        default=["meta-llama/llama-3-8b-instruct", "mistralai/mistral-7b-instruct"],
        help="Models to test"
    )
    parser.add_argument(
        "--suite",
        choices=["minimal", "standard", "comprehensive"],
        default="minimal",
        help="Attractor suite size"
    )
    parser.add_argument(
        "--output",
        help="Output file path"
    )
    
    args = parser.parse_args()
    
    validate_suite(args.models, args.suite, args.output)


if __name__ == "__main__":
    main()
