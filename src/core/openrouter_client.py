"""
OpenRouter API Client for Multi-Model LLM Experiments

Provides a unified interface to query multiple LLM providers through OpenRouter,
with support for logit bias and other experimental controls.
"""

import os
import time
from typing import Dict, List, Optional, Any, Tuple
import requests
from dataclasses import dataclass
import json


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 200
    temperature: float = 0.7
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    n: int = 1  # Number of completions


@dataclass
class ModelResponse:
    """Structured response from model."""
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    raw_response: Dict[str, Any]


class OpenRouterClient:
    """
    Client for OpenRouter API with experimental controls.
    
    Supports multiple models and provides hooks for:
    - Logit biasing
    - Token-level interventions
    - Response analysis
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Model size categories for comparative analysis
    SMALL_MODELS = [
        "meta-llama/llama-3-8b-instruct",
        "mistralai/mistral-7b-instruct",
        "google/gemma-7b-it",
    ]
    
    MEDIUM_MODELS = [
        "meta-llama/llama-3-70b-instruct",
        "anthropic/claude-3-sonnet",
        "google/gemini-pro",
    ]
    
    LARGE_MODELS = [
        "openai/gpt-4-turbo",
        "anthropic/claude-3-opus",
        "meta-llama/llama-3-405b-instruct",
    ]
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (defaults to env var)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key required")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/ebaenamar/llm-controlled-dynamics",
            "X-Title": "LLM Controlled Dynamics Research"
        }
    
    def generate(
        self,
        prompt: str,
        model: str,
        config: Optional[GenerationConfig] = None
    ) -> ModelResponse:
        """
        Generate text from a model.
        
        Args:
            prompt: Input prompt
            model: Model identifier (e.g., "openai/gpt-4")
            config: Generation configuration
            
        Returns:
            ModelResponse with generated text and metadata
        """
        if config is None:
            config = GenerationConfig()
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
            "n": config.n,
        }
        
        # Add logit bias if specified
        if config.logit_bias:
            payload["logit_bias"] = config.logit_bias
        
        response = requests.post(
            f"{self.BASE_URL}/chat/completions",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        data = response.json()
        choice = data["choices"][0]
        usage = data.get("usage", {})
        
        return ModelResponse(
            text=choice["message"]["content"],
            model=data.get("model", model),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
            finish_reason=choice.get("finish_reason", "unknown"),
            raw_response=data
        )
    
    def generate_batch(
        self,
        prompts: List[str],
        model: str,
        config: Optional[GenerationConfig] = None,
        delay: float = 0.5
    ) -> List[ModelResponse]:
        """
        Generate text for multiple prompts.
        
        Args:
            prompts: List of input prompts
            model: Model identifier
            config: Generation configuration
            delay: Delay between requests (seconds)
            
        Returns:
            List of ModelResponse objects
        """
        responses = []
        for prompt in prompts:
            response = self.generate(prompt, model, config)
            responses.append(response)
            time.sleep(delay)
        return responses
    
    def compare_models(
        self,
        prompt: str,
        models: List[str],
        config: Optional[GenerationConfig] = None,
        delay: float = 0.5
    ) -> Dict[str, ModelResponse]:
        """
        Generate text from multiple models for comparison.
        
        Args:
            prompt: Input prompt
            models: List of model identifiers
            config: Generation configuration
            delay: Delay between requests
            
        Returns:
            Dictionary mapping model names to responses
        """
        results = {}
        for model in models:
            try:
                response = self.generate(prompt, model, config)
                results[model] = response
                time.sleep(delay)
            except Exception as e:
                print(f"Error with model {model}: {e}")
                results[model] = None
        return results
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Fetch list of available models from OpenRouter.
        
        Returns:
            List of model metadata dictionaries
        """
        response = requests.get(
            f"{self.BASE_URL}/models",
            headers=self.headers
        )
        
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}")
        
        return response.json().get("data", [])
    
    def get_model_sizes(self) -> Dict[str, List[str]]:
        """
        Get categorized models by size.
        
        Returns:
            Dictionary with 'small', 'medium', 'large' model lists
        """
        return {
            "small": self.SMALL_MODELS,
            "medium": self.MEDIUM_MODELS,
            "large": self.LARGE_MODELS
        }
    
    def estimate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ) -> float:
        """
        Estimate cost for a generation (rough approximation).
        
        Args:
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            model: Model identifier
            
        Returns:
            Estimated cost in USD
        """
        # Rough pricing estimates (as of 2024)
        pricing = {
            "gpt-4": (0.03, 0.06),  # (input, output) per 1K tokens
            "gpt-3.5": (0.0005, 0.0015),
            "claude-3-opus": (0.015, 0.075),
            "claude-3-sonnet": (0.003, 0.015),
            "llama-3-70b": (0.0007, 0.0009),
            "llama-3-8b": (0.0001, 0.0002),
        }
        
        # Match model to pricing category
        for key, (input_price, output_price) in pricing.items():
            if key in model.lower():
                input_cost = (prompt_tokens / 1000) * input_price
                output_cost = (completion_tokens / 1000) * output_price
                return input_cost + output_cost
        
        # Default estimate
        return ((prompt_tokens + completion_tokens) / 1000) * 0.001


if __name__ == "__main__":
    # Test the client
    client = OpenRouterClient()
    
    # Simple test
    response = client.generate(
        "Complete this: En un lugar de la Mancha,",
        "meta-llama/llama-3-8b-instruct",
        GenerationConfig(max_tokens=50, temperature=0.7)
    )
    
    print(f"Model: {response.model}")
    print(f"Text: {response.text}")
    print(f"Tokens: {response.total_tokens}")
