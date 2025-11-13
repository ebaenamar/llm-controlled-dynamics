"""
Observable Metrics for LLM Controlled Dynamics

Implements measurements for:
1. Text-level similarity (exact match, edit distance, BLEU)
2. Distribution divergence (KL divergence approximation)
3. Semantic distance (embedding-based)
4. Trajectory analysis (state space geometry)
"""

from typing import List, Dict, Tuple, Optional
import numpy as np
from dataclasses import dataclass
from scipy.spatial.distance import cosine, euclidean
from scipy.stats import entropy
import re
from collections import Counter


@dataclass
class MetricResult:
    """Container for metric computation results."""
    metric_name: str
    value: float
    metadata: Optional[Dict] = None
    
    def __repr__(self):
        return f"{self.metric_name}: {self.value:.4f}"


class TextMetrics:
    """
    Text-level similarity and divergence metrics.
    
    These measure how much the output has changed from the
    expected/canonical text.
    """
    
    @staticmethod
    def exact_match(text1: str, text2: str, normalize: bool = True) -> MetricResult:
        """
        Compute exact match score.
        
        Args:
            text1: First text
            text2: Second text
            normalize: Whether to normalize whitespace
            
        Returns:
            MetricResult with binary match score
        """
        if normalize:
            text1 = " ".join(text1.split())
            text2 = " ".join(text2.split())
        
        match = 1.0 if text1 == text2 else 0.0
        
        return MetricResult(
            metric_name="exact_match",
            value=match,
            metadata={"length_diff": abs(len(text1) - len(text2))}
        )
    
    @staticmethod
    def token_overlap(text1: str, text2: str) -> MetricResult:
        """
        Compute token-level overlap (Jaccard similarity).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            MetricResult with overlap score (0.0 to 1.0)
        """
        tokens1 = set(text1.lower().split())
        tokens2 = set(text2.lower().split())
        
        if len(tokens1) == 0 and len(tokens2) == 0:
            overlap = 1.0
        elif len(tokens1) == 0 or len(tokens2) == 0:
            overlap = 0.0
        else:
            intersection = len(tokens1 & tokens2)
            union = len(tokens1 | tokens2)
            overlap = intersection / union if union > 0 else 0.0
        
        return MetricResult(
            metric_name="token_overlap",
            value=overlap,
            metadata={
                "unique_tokens_1": len(tokens1),
                "unique_tokens_2": len(tokens2),
                "shared_tokens": len(tokens1 & tokens2)
            }
        )
    
    @staticmethod
    def levenshtein_distance(text1: str, text2: str, normalize: bool = True) -> MetricResult:
        """
        Compute Levenshtein (edit) distance.
        
        Args:
            text1: First text
            text2: Second text
            normalize: Normalize by max length
            
        Returns:
            MetricResult with edit distance
        """
        m, n = len(text1), len(text2)
        dp = np.zeros((m + 1, n + 1))
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i-1] == text2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i-1][j],    # deletion
                        dp[i][j-1],    # insertion
                        dp[i-1][j-1]   # substitution
                    )
        
        distance = dp[m][n]
        
        if normalize and max(m, n) > 0:
            distance = distance / max(m, n)
        
        return MetricResult(
            metric_name="levenshtein_distance",
            value=distance,
            metadata={"length_1": m, "length_2": n}
        )
    
    @staticmethod
    def prefix_match_length(text1: str, text2: str) -> MetricResult:
        """
        Compute length of matching prefix.
        
        Useful for detecting when model "falls off" memorized text.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            MetricResult with prefix match length
        """
        min_len = min(len(text1), len(text2))
        match_len = 0
        
        for i in range(min_len):
            if text1[i] == text2[i]:
                match_len += 1
            else:
                break
        
        # Also compute word-level prefix match
        words1 = text1.split()
        words2 = text2.split()
        word_match = 0
        
        for i in range(min(len(words1), len(words2))):
            if words1[i] == words2[i]:
                word_match += 1
            else:
                break
        
        return MetricResult(
            metric_name="prefix_match_length",
            value=match_len,
            metadata={
                "char_match": match_len,
                "word_match": word_match,
                "total_chars": max(len(text1), len(text2))
            }
        )
    
    @staticmethod
    def memorization_score(
        generated: str,
        canonical: str,
        threshold: float = 0.8
    ) -> MetricResult:
        """
        Compute memorization retention score.
        
        Combines exact match, prefix match, and token overlap.
        
        Args:
            generated: Generated text
            canonical: Expected canonical text
            threshold: Threshold for "strong" memorization
            
        Returns:
            MetricResult with composite memorization score
        """
        exact = TextMetrics.exact_match(generated, canonical).value
        prefix = TextMetrics.prefix_match_length(generated, canonical)
        overlap = TextMetrics.token_overlap(generated, canonical).value
        
        # Weighted combination
        score = 0.4 * exact + 0.3 * (prefix.metadata["word_match"] / max(len(canonical.split()), 1)) + 0.3 * overlap
        
        return MetricResult(
            metric_name="memorization_score",
            value=score,
            metadata={
                "exact_match": exact,
                "prefix_words": prefix.metadata["word_match"],
                "token_overlap": overlap,
                "is_memorized": score >= threshold
            }
        )


class DistributionMetrics:
    """
    Metrics for comparing probability distributions.
    
    Since we don't have direct access to logits, we approximate
    distributions using token frequencies and n-gram statistics.
    """
    
    @staticmethod
    def token_frequency_distribution(text: str, normalize: bool = True) -> np.ndarray:
        """
        Compute token frequency distribution.
        
        Args:
            text: Input text
            normalize: Whether to normalize to probabilities
            
        Returns:
            Frequency distribution as numpy array
        """
        tokens = text.lower().split()
        counter = Counter(tokens)
        
        # Sort by token for consistency
        sorted_tokens = sorted(counter.keys())
        freqs = np.array([counter[t] for t in sorted_tokens])
        
        if normalize and freqs.sum() > 0:
            freqs = freqs / freqs.sum()
        
        return freqs
    
    @staticmethod
    def kl_divergence_approx(text1: str, text2: str, smoothing: float = 1e-10) -> MetricResult:
        """
        Approximate KL divergence between two texts.
        
        Uses token frequency distributions as proxy for output distributions.
        
        Args:
            text1: First text (reference)
            text2: Second text (comparison)
            smoothing: Laplace smoothing parameter
            
        Returns:
            MetricResult with KL divergence estimate
        """
        # Get all unique tokens
        tokens1 = text1.lower().split()
        tokens2 = text2.lower().split()
        all_tokens = sorted(set(tokens1 + tokens2))
        
        if len(all_tokens) == 0:
            return MetricResult("kl_divergence", 0.0)
        
        # Build distributions
        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)
        
        p = np.array([counter1.get(t, 0) + smoothing for t in all_tokens])
        q = np.array([counter2.get(t, 0) + smoothing for t in all_tokens])
        
        # Normalize
        p = p / p.sum()
        q = q / q.sum()
        
        # Compute KL divergence
        kl = entropy(p, q)
        
        return MetricResult(
            metric_name="kl_divergence",
            value=kl,
            metadata={
                "vocab_size": len(all_tokens),
                "entropy_p": entropy(p),
                "entropy_q": entropy(q)
            }
        )
    
    @staticmethod
    def js_divergence(text1: str, text2: str) -> MetricResult:
        """
        Compute Jensen-Shannon divergence (symmetric version of KL).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            MetricResult with JS divergence
        """
        # Get distributions
        tokens1 = text1.lower().split()
        tokens2 = text2.lower().split()
        all_tokens = sorted(set(tokens1 + tokens2))
        
        if len(all_tokens) == 0:
            return MetricResult("js_divergence", 0.0)
        
        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)
        
        smoothing = 1e-10
        p = np.array([counter1.get(t, 0) + smoothing for t in all_tokens])
        q = np.array([counter2.get(t, 0) + smoothing for t in all_tokens])
        
        p = p / p.sum()
        q = q / q.sum()
        
        # Compute JS divergence
        m = 0.5 * (p + q)
        js = 0.5 * entropy(p, m) + 0.5 * entropy(q, m)
        
        return MetricResult(
            metric_name="js_divergence",
            value=js,
            metadata={"vocab_size": len(all_tokens)}
        )


class SemanticMetrics:
    """
    Semantic similarity metrics.
    
    These would ideally use embeddings, but we approximate using
    lexical and structural features.
    """
    
    @staticmethod
    def cosine_similarity_bow(text1: str, text2: str) -> MetricResult:
        """
        Compute cosine similarity using bag-of-words vectors.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            MetricResult with cosine similarity
        """
        tokens1 = text1.lower().split()
        tokens2 = text2.lower().split()
        all_tokens = sorted(set(tokens1 + tokens2))
        
        if len(all_tokens) == 0:
            return MetricResult("cosine_similarity", 1.0)
        
        # Build vectors
        counter1 = Counter(tokens1)
        counter2 = Counter(tokens2)
        
        vec1 = np.array([counter1.get(t, 0) for t in all_tokens])
        vec2 = np.array([counter2.get(t, 0) for t in all_tokens])
        
        # Compute cosine similarity
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            similarity = 0.0
        else:
            similarity = 1.0 - cosine(vec1, vec2)
        
        return MetricResult(
            metric_name="cosine_similarity",
            value=similarity,
            metadata={"vocab_size": len(all_tokens)}
        )
    
    @staticmethod
    def structural_similarity(text1: str, text2: str) -> MetricResult:
        """
        Measure structural similarity (sentence length, punctuation, etc.).
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            MetricResult with structural similarity score
        """
        # Extract features
        def extract_features(text):
            return {
                "num_sentences": len(re.split(r'[.!?]+', text)),
                "num_words": len(text.split()),
                "num_commas": text.count(','),
                "num_periods": text.count('.'),
                "avg_word_len": np.mean([len(w) for w in text.split()]) if text.split() else 0
            }
        
        feat1 = extract_features(text1)
        feat2 = extract_features(text2)
        
        # Compute normalized differences
        diffs = []
        for key in feat1:
            val1, val2 = feat1[key], feat2[key]
            max_val = max(val1, val2, 1)
            diff = 1.0 - abs(val1 - val2) / max_val
            diffs.append(diff)
        
        similarity = np.mean(diffs)
        
        return MetricResult(
            metric_name="structural_similarity",
            value=similarity,
            metadata={"features_1": feat1, "features_2": feat2}
        )


class TrajectoryMetrics:
    """
    Metrics for analyzing state space trajectories.
    
    These are more abstract since we don't have direct access to
    hidden states, but we can analyze text-level "trajectories".
    """
    
    @staticmethod
    def divergence_point(
        generated: str,
        canonical: str
    ) -> MetricResult:
        """
        Find the point where generated text diverges from canonical.
        
        Args:
            generated: Generated text
            canonical: Canonical text
            
        Returns:
            MetricResult with divergence point (character and word index)
        """
        # Character-level divergence
        char_div = 0
        for i in range(min(len(generated), len(canonical))):
            if generated[i] != canonical[i]:
                char_div = i
                break
        else:
            char_div = min(len(generated), len(canonical))
        
        # Word-level divergence
        words_gen = generated.split()
        words_can = canonical.split()
        word_div = 0
        
        for i in range(min(len(words_gen), len(words_can))):
            if words_gen[i] != words_can[i]:
                word_div = i
                break
        else:
            word_div = min(len(words_gen), len(words_can))
        
        # Compute relative position
        rel_pos = word_div / max(len(words_can), 1)
        
        return MetricResult(
            metric_name="divergence_point",
            value=rel_pos,
            metadata={
                "char_index": char_div,
                "word_index": word_div,
                "total_words": len(words_can)
            }
        )
    
    @staticmethod
    def stability_score(
        responses: List[str],
        reference: str
    ) -> MetricResult:
        """
        Measure stability across multiple generations.
        
        Args:
            responses: List of generated responses
            reference: Reference text
            
        Returns:
            MetricResult with stability score
        """
        if len(responses) == 0:
            return MetricResult("stability_score", 0.0)
        
        # Compute average similarity to reference
        similarities = []
        for resp in responses:
            sim = TextMetrics.token_overlap(resp, reference).value
            similarities.append(sim)
        
        # Stability = mean similarity, variance
        mean_sim = np.mean(similarities)
        var_sim = np.var(similarities)
        
        # High stability = high mean, low variance
        stability = mean_sim * (1.0 - min(var_sim, 1.0))
        
        return MetricResult(
            metric_name="stability_score",
            value=stability,
            metadata={
                "mean_similarity": mean_sim,
                "variance": var_sim,
                "num_samples": len(responses)
            }
        )


class MetricSuite:
    """Comprehensive metric computation suite."""
    
    @staticmethod
    def compute_all_metrics(
        generated: str,
        canonical: str,
        additional_samples: Optional[List[str]] = None
    ) -> Dict[str, MetricResult]:
        """
        Compute all available metrics.
        
        Args:
            generated: Generated text
            canonical: Canonical/expected text
            additional_samples: Additional samples for stability analysis
            
        Returns:
            Dictionary of metric results
        """
        results = {}
        
        # Text metrics
        results["exact_match"] = TextMetrics.exact_match(generated, canonical)
        results["token_overlap"] = TextMetrics.token_overlap(generated, canonical)
        results["levenshtein"] = TextMetrics.levenshtein_distance(generated, canonical)
        results["prefix_match"] = TextMetrics.prefix_match_length(generated, canonical)
        results["memorization"] = TextMetrics.memorization_score(generated, canonical)
        
        # Distribution metrics
        results["kl_divergence"] = DistributionMetrics.kl_divergence_approx(canonical, generated)
        results["js_divergence"] = DistributionMetrics.js_divergence(canonical, generated)
        
        # Semantic metrics
        results["cosine_similarity"] = SemanticMetrics.cosine_similarity_bow(generated, canonical)
        results["structural_similarity"] = SemanticMetrics.structural_similarity(generated, canonical)
        
        # Trajectory metrics
        results["divergence_point"] = TrajectoryMetrics.divergence_point(generated, canonical)
        
        if additional_samples:
            results["stability"] = TrajectoryMetrics.stability_score(
                additional_samples + [generated],
                canonical
            )
        
        return results
    
    @staticmethod
    def summarize_metrics(metrics: Dict[str, MetricResult]) -> Dict[str, float]:
        """
        Extract summary statistics from metrics.
        
        Args:
            metrics: Dictionary of MetricResult objects
            
        Returns:
            Dictionary of metric values
        """
        return {name: result.value for name, result in metrics.items()}


if __name__ == "__main__":
    # Test metrics
    canonical = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme"
    generated1 = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme"  # Exact match
    generated2 = "En un lugar de la Mancha, <ISO-2847> de cuyo nombre no quiero"  # Perturbed
    generated3 = "In a place in La Mancha, whose name I do not wish to remember"  # Translation
    
    print("=== Exact Match ===")
    metrics = MetricSuite.compute_all_metrics(generated1, canonical)
    for name, result in metrics.items():
        print(result)
    
    print("\n=== Perturbed ===")
    metrics = MetricSuite.compute_all_metrics(generated2, canonical)
    for name, result in metrics.items():
        print(result)
    
    print("\n=== Translation ===")
    metrics = MetricSuite.compute_all_metrics(generated3, canonical)
    for name, result in metrics.items():
        print(result)
