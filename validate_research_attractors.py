#!/usr/bin/env python3
"""
Validate Research-Based Attractors

Tests attractors that have published evidence of memorization.
Quick validation to confirm which ones work with our models.
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from core.openrouter_client import OpenRouterClient, GenerationConfig
from core.metrics import TextMetrics


# Research-backed attractors
RESEARCH_ATTRACTORS = {
    "harry_potter": {
        "prompt": "Mr. and Mrs. Dursley, of number four",
        "expected": "Privet Drive, were proud to say that they were perfectly normal, thank you very much",
        "full_text": "Mr. and Mrs. Dursley, of number four Privet Drive, were proud to say that they were perfectly normal, thank you very much.",
        "evidence": "ArXiv 2505.12546 - Llama 3.1 70B",
        "min_model_size": "70B"
    },
    
    "lorem_ipsum": {
        "prompt": "Lorem ipsum dolor",
        "expected": "sit amet, consectetur adipiscing elit",
        "full_text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
        "evidence": "High frequency placeholder text",
        "min_model_size": "7B"
    },
    
    "hello_world_python": {
        "prompt": 'print("Hello,',
        "expected": 'World!")',
        "full_text": 'print("Hello, World!")',
        "evidence": "Most common code snippet",
        "min_model_size": "7B"
    },
    
    "html_doctype": {
        "prompt": "<!DOCTYPE",
        "expected": "html>",
        "full_text": "<!DOCTYPE html>",
        "evidence": "Billions of web pages",
        "min_model_size": "7B"
    },
    
    "alphabet": {
        "prompt": "A B C D E",
        "expected": "F G H I J K L M N O P Q R S T U V W X Y Z",
        "full_text": "A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
        "evidence": "Universal sequence",
        "min_model_size": "1B"
    },
    
    "counting_1_10": {
        "prompt": "1 2 3 4",
        "expected": "5 6 7 8 9 10",
        "full_text": "1 2 3 4 5 6 7 8 9 10",
        "evidence": "Basic counting",
        "min_model_size": "1B"
    },
    
    "python_imports": {
        "prompt": "import numpy as",
        "expected": "np",
        "full_text": "import numpy as np\nimport pandas as pd",
        "evidence": "Common Python imports",
        "min_model_size": "7B"
    }
}


def quick_validate(attractor_name, attractor_data, model, client):
    """Quick validation of a single attractor."""
    
    prompt = attractor_data["prompt"]
    expected = attractor_data["expected"]
    full_text = attractor_data["full_text"]
    
    config = GenerationConfig(
        max_tokens=100,
        temperature=0.0  # Deterministic
    )
    
    try:
        response = client.generate(prompt, model, config)
        
        # Check if expected text appears in response
        contains_expected = expected.lower() in response.text.lower()
        
        # Compute memorization score
        mem_score = TextMetrics.memorization_score(
            response.text,
            full_text
        )
        
        return {
            "success": True,
            "response": response.text,
            "contains_expected": contains_expected,
            "memorization_score": mem_score.value,
            "is_memorized": mem_score.value >= 0.7
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def main():
    load_dotenv()
    client = OpenRouterClient()
    
    # Test models
    models = [
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct"
    ]
    
    print("\n" + "="*80)
    print("QUICK VALIDATION OF RESEARCH-BASED ATTRACTORS")
    print("="*80 + "\n")
    
    results = {}
    
    for model in models:
        print(f"\n{'='*80}")
        print(f"Model: {model}")
        print(f"{'='*80}\n")
        
        results[model] = {}
        
        for name, data in RESEARCH_ATTRACTORS.items():
            print(f"{name:25} ", end="", flush=True)
            
            result = quick_validate(name, data, model, client)
            results[model][name] = result
            
            if result["success"]:
                mem = result["memorization_score"]
                check = "✓" if result["is_memorized"] else "✗"
                expected_check = "✓" if result["contains_expected"] else "✗"
                
                print(f"{check} Mem: {mem:.3f} | Expected: {expected_check}")
                
                if not result["is_memorized"]:
                    print(f"  Response: {result['response'][:60]}...")
            else:
                print(f"✗ Error: {result['error']}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80 + "\n")
    
    for model in models:
        memorized = sum(1 for r in results[model].values() if r.get("is_memorized", False))
        total = len(RESEARCH_ATTRACTORS)
        
        print(f"{model}:")
        print(f"  Memorized: {memorized}/{total} ({100*memorized/total:.0f}%)")
        
        # Best attractors
        best = sorted(
            [(name, r.get("memorization_score", 0)) for name, r in results[model].items()],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        print(f"  Top 3:")
        for name, score in best:
            print(f"    - {name}: {score:.3f}")
        print()
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDATIONS FOR EXPERIMENTS")
    print("="*80 + "\n")
    
    # Find attractors that work on both models
    working_on_both = []
    for name in RESEARCH_ATTRACTORS:
        if all(results[m][name].get("is_memorized", False) for m in models):
            avg_score = sum(results[m][name].get("memorization_score", 0) for m in models) / len(models)
            working_on_both.append((name, avg_score))
    
    if working_on_both:
        working_on_both.sort(key=lambda x: x[1], reverse=True)
        print("✅ Attractors working on ALL tested models:")
        for name, score in working_on_both:
            print(f"  - {name}: avg {score:.3f}")
    else:
        print("⚠️  No attractors work reliably on all models")
        print("\nBest alternatives:")
        
        # Find best per model
        for model in models:
            best = max(
                results[model].items(),
                key=lambda x: x[1].get("memorization_score", 0)
            )
            print(f"  {model}: {best[0]} ({best[1].get('memorization_score', 0):.3f})")


if __name__ == "__main__":
    main()
