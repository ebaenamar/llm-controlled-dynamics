#!/usr/bin/env python3
"""
Quick start script to test the framework with a single experiment.

This runs Experiment A (token insertion) on a small model to verify setup.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from experiments.quijote_experiments import QuijoteExperiments


def main():
    print("\n" + "="*80)
    print("LLM CONTROLLED DYNAMICS - QUICK START")
    print("="*80 + "\n")
    
    # Load environment
    load_dotenv()
    
    # Check API key
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenRouter API key to .env")
        print("3. Run this script again")
        sys.exit(1)
    
    print("✓ API key found")
    print(f"✓ Key: {api_key[:20]}...{api_key[-10:]}\n")
    
    # Initialize experiments
    print("Initializing experiment framework...")
    exp = QuijoteExperiments(api_key=api_key)
    print("✓ Framework initialized\n")
    
    # Test with a small, fast model
    test_model = "meta-llama/llama-3-8b-instruct"
    
    print(f"Running Experiment A (Token Insertion) on {test_model}")
    print("This will take ~10-15 seconds...\n")
    
    try:
        results = exp.experiment_a_token_insertion([test_model])
        
        if results:
            result = results[0]
            
            print("\n" + "="*80)
            print("RESULTS")
            print("="*80 + "\n")
            
            print(f"Model: {result.model}")
            print(f"\nPrompt (control):")
            print(f"  {result.prompt_control}")
            print(f"\nPrompt (modified):")
            print(f"  {result.prompt_modified}")
            print(f"\nResponse (control):")
            print(f"  {result.response_control.text}")
            print(f"\nResponse (modified):")
            print(f"  {result.response_modified.text}")
            print(f"\nMetrics:")
            print(f"  Control memorization: {result.metrics['control']['memorization']:.3f}")
            print(f"  Modified memorization: {result.metrics['modified']['memorization']:.3f}")
            print(f"  Δ Memorization: {result.metrics['delta_memorization']:.3f}")
            print(f"  Δ KL Divergence: {result.metrics['delta_kl']:.3f}")
            
            print("\n" + "="*80)
            print("SUCCESS! Framework is working correctly.")
            print("="*80 + "\n")
            
            print("Next steps:")
            print("1. Run all experiments: python run_experiments.py --all --models small")
            print("2. Compare models: python run_experiments.py --all --models all")
            print("3. Analyze results: python run_experiments.py --analyze results/quijote_experiments_*.json")
            print("4. Generate plots: python -m src.visualization.plots")
            
        else:
            print("❌ No results returned. Check API connection.")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your API key is valid")
        print("2. Verify you have internet connection")
        print("3. Check OpenRouter status: https://openrouter.ai/status")
        sys.exit(1)


if __name__ == "__main__":
    main()
