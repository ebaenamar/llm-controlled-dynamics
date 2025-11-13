"""
Action Definitions for LLM Controlled Dynamics

Implements three levels of interventions:
1. Token-level: Insertion, substitution, segment shocks
2. Embedding-level: Directional perturbations (simulated via prompt engineering)
3. Logit-level: Bias towards rare tokens, tail amplification
"""

from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import random
import re


class ActionType(Enum):
    """Types of interventions on LLM dynamics."""
    TOKEN_INSERTION = "token_insertion"
    TOKEN_SUBSTITUTION = "token_substitution"
    SEGMENT_SHOCK = "segment_shock"
    EMBEDDING_PERTURBATION = "embedding_perturbation"
    LOGIT_BIAS = "logit_bias"
    TAIL_AMPLIFICATION = "tail_amplification"


@dataclass
class Action:
    """
    Represents a controlled intervention on LLM input/output.
    
    Attributes:
        action_type: Type of intervention
        magnitude: Strength of intervention (0.0 to 1.0)
        position: Where to apply (token index, layer, etc.)
        parameters: Additional action-specific parameters
    """
    action_type: ActionType
    magnitude: float
    position: Optional[int] = None
    parameters: Optional[Dict] = None
    
    def __repr__(self):
        return f"Action({self.action_type.value}, α={self.magnitude:.2f}, pos={self.position})"


class TokenActions:
    """
    Token-level interventions.
    
    These modify the input sequence directly by inserting unexpected tokens,
    substituting with rare tokens, or adding out-of-domain segments.
    """
    
    # Rare/unexpected tokens for insertion
    RARE_TOKENS = [
        "∮", "⊗", "∇", "≈", "∞", "⊕", "⊖", "⊙",
        "<ISO-2847>", "<X2F-ERROR>", "<ANOMALY>", 
        "⟨quantum⟩", "⟨void⟩", "⟨glitch⟩"
    ]
    
    # Out-of-domain segments for shock experiments
    SHOCK_SEGMENTS = {
        "technical": [
            "according to ISO-9001 specifications",
            "via quantum entanglement protocols",
            "through recursive neural pathways",
            "using Bayesian inference methods"
        ],
        "modern": [
            "in the metaverse",
            "through blockchain consensus",
            "via neural network optimization",
            "using machine learning algorithms"
        ],
        "absurd": [
            "with interdimensional portals",
            "through time-reversed causality",
            "via telepathic resonance",
            "using antimatter propulsion"
        ]
    }
    
    @staticmethod
    def insert_token(
        text: str,
        token: Optional[str] = None,
        position: Optional[int] = None
    ) -> Tuple[str, Action]:
        """
        Insert an unexpected token at a specific position.
        
        Args:
            text: Original text
            token: Token to insert (random if None)
            position: Character position (random if None)
            
        Returns:
            Modified text and Action object
        """
        if token is None:
            token = random.choice(TokenActions.RARE_TOKENS)
        
        if position is None:
            # Insert at a random word boundary
            words = text.split()
            word_pos = random.randint(0, len(words))
            words.insert(word_pos, token)
            modified = " ".join(words)
            position = word_pos
        else:
            modified = text[:position] + f" {token} " + text[position:]
        
        action = Action(
            action_type=ActionType.TOKEN_INSERTION,
            magnitude=1.0,  # Binary: token inserted or not
            position=position,
            parameters={"token": token}
        )
        
        return modified, action
    
    @staticmethod
    def substitute_token(
        text: str,
        target_word: Optional[str] = None,
        replacement: Optional[str] = None
    ) -> Tuple[str, Action]:
        """
        Substitute a token with a rare/unexpected one.
        
        Args:
            text: Original text
            target_word: Word to replace (random common word if None)
            replacement: Replacement token (random rare token if None)
            
        Returns:
            Modified text and Action object
        """
        if replacement is None:
            replacement = random.choice(TokenActions.RARE_TOKENS)
        
        words = text.split()
        
        if target_word is None:
            # Replace a random word
            if len(words) > 0:
                idx = random.randint(0, len(words) - 1)
                target_word = words[idx]
                words[idx] = replacement
        else:
            # Replace specific word
            words = [replacement if w == target_word else w for w in words]
        
        modified = " ".join(words)
        
        action = Action(
            action_type=ActionType.TOKEN_SUBSTITUTION,
            magnitude=1.0,
            parameters={"target": target_word, "replacement": replacement}
        )
        
        return modified, action
    
    @staticmethod
    def add_segment_shock(
        text: str,
        shock_type: str = "technical",
        position: Optional[int] = None
    ) -> Tuple[str, Action]:
        """
        Add an out-of-domain segment to the text.
        
        Args:
            text: Original text
            shock_type: Type of shock ('technical', 'modern', 'absurd')
            position: Word position to insert (random if None)
            
        Returns:
            Modified text and Action object
        """
        segment = random.choice(TokenActions.SHOCK_SEGMENTS.get(shock_type, []))
        
        words = text.split()
        if position is None:
            position = random.randint(0, len(words))
        
        words.insert(position, segment)
        modified = " ".join(words)
        
        action = Action(
            action_type=ActionType.SEGMENT_SHOCK,
            magnitude=1.0,
            position=position,
            parameters={"shock_type": shock_type, "segment": segment}
        )
        
        return modified, action


class EmbeddingActions:
    """
    Embedding-level interventions (simulated).
    
    Since we don't have direct access to embeddings via OpenRouter,
    we simulate directional perturbations through carefully crafted
    prompt modifications that should shift the semantic space.
    """
    
    STYLE_VECTORS = {
        "technical": "Rewrite in highly technical, scientific language:",
        "poetic": "Rewrite in poetic, lyrical language:",
        "modern": "Rewrite in modern, contemporary language:",
        "archaic": "Rewrite in archaic, old-fashioned language:",
        "casual": "Rewrite in casual, informal language:",
        "formal": "Rewrite in formal, academic language:"
    }
    
    @staticmethod
    def apply_directional_perturbation(
        text: str,
        direction: str = "technical",
        magnitude: float = 0.5
    ) -> Tuple[str, Action]:
        """
        Apply a directional perturbation in embedding space.
        
        Simulated by prepending a style instruction with varying strength.
        
        Args:
            text: Original text
            direction: Direction in style space
            magnitude: Strength of perturbation (0.0 to 1.0)
            
        Returns:
            Modified prompt and Action object
        """
        if magnitude < 0.3:
            # Weak perturbation: subtle hint
            prefix = f"(Slightly {direction}:) "
        elif magnitude < 0.7:
            # Medium perturbation: clear instruction
            prefix = EmbeddingActions.STYLE_VECTORS.get(
                direction, 
                f"Rewrite in {direction} style:"
            ) + " "
        else:
            # Strong perturbation: emphatic instruction
            prefix = f"IMPORTANT: {EmbeddingActions.STYLE_VECTORS.get(direction, '')} "
        
        modified = prefix + text
        
        action = Action(
            action_type=ActionType.EMBEDDING_PERTURBATION,
            magnitude=magnitude,
            parameters={"direction": direction, "prefix": prefix}
        )
        
        return modified, action
    
    @staticmethod
    def add_gaussian_noise(
        text: str,
        magnitude: float = 0.5
    ) -> Tuple[str, Action]:
        """
        Simulate isotropic Gaussian noise in embedding space.
        
        Implemented by adding random, semantically unrelated words.
        
        Args:
            text: Original text
            magnitude: Noise level (0.0 to 1.0)
            
        Returns:
            Modified text and Action object
        """
        noise_words = [
            "quantum", "recursive", "asymptotic", "stochastic",
            "ephemeral", "liminal", "fractal", "entropic"
        ]
        
        num_noise = int(magnitude * 3)  # 0-3 noise words
        if num_noise > 0:
            noise = " ".join(random.sample(noise_words, num_noise))
            modified = f"{text} [{noise}]"
        else:
            modified = text
        
        action = Action(
            action_type=ActionType.EMBEDDING_PERTURBATION,
            magnitude=magnitude,
            parameters={"noise_type": "gaussian", "noise_words": num_noise}
        )
        
        return modified, action


class LogitActions:
    """
    Logit-level interventions.
    
    These modify the output distribution by biasing towards/against
    specific tokens or amplifying the probability tail.
    """
    
    @staticmethod
    def create_logit_bias(
        token_ids: List[int],
        bias_value: float = 1.0
    ) -> Dict[str, float]:
        """
        Create a logit bias dictionary.
        
        Args:
            token_ids: List of token IDs to bias
            bias_value: Bias strength (-100 to 100)
            
        Returns:
            Logit bias dictionary for API
        """
        return {str(tid): bias_value for tid in token_ids}
    
    @staticmethod
    def bias_towards_rare_tokens(
        magnitude: float = 0.5
    ) -> Tuple[Dict[str, float], Action]:
        """
        Create bias favoring rare/uncommon tokens.
        
        Note: This is a simplified version. In practice, you'd need
        to identify rare token IDs from the model's vocabulary.
        
        Args:
            magnitude: Bias strength (0.0 to 1.0)
            
        Returns:
            Logit bias dict and Action object
        """
        # Placeholder: would need actual rare token IDs
        # For now, return empty dict (to be implemented with tokenizer)
        bias_value = magnitude * 10  # Scale to -100 to 100 range
        
        action = Action(
            action_type=ActionType.LOGIT_BIAS,
            magnitude=magnitude,
            parameters={"bias_type": "rare_tokens", "bias_value": bias_value}
        )
        
        return {}, action
    
    @staticmethod
    def amplify_tail(
        magnitude: float = 0.5
    ) -> Tuple[str, Action]:
        """
        Simulate tail amplification via prompt instruction.
        
        Since we can't directly modify logits, we instruct the model
        to use more unusual/creative language.
        
        Args:
            magnitude: Amplification strength (0.0 to 1.0)
            
        Returns:
            Prompt modifier and Action object
        """
        if magnitude < 0.3:
            modifier = "(Use slightly unusual words) "
        elif magnitude < 0.7:
            modifier = "Use creative, uncommon vocabulary: "
        else:
            modifier = "IMPORTANT: Use highly unusual, rare, and creative words: "
        
        action = Action(
            action_type=ActionType.TAIL_AMPLIFICATION,
            magnitude=magnitude,
            parameters={"modifier": modifier}
        )
        
        return modifier, action


class ActionFactory:
    """Factory for creating and applying actions."""
    
    @staticmethod
    def apply_action(text: str, action: Action) -> str:
        """
        Apply an action to text.
        
        Args:
            text: Original text
            action: Action to apply
            
        Returns:
            Modified text
        """
        if action.action_type == ActionType.TOKEN_INSERTION:
            modified, _ = TokenActions.insert_token(
                text,
                token=action.parameters.get("token"),
                position=action.position
            )
            return modified
        
        elif action.action_type == ActionType.TOKEN_SUBSTITUTION:
            modified, _ = TokenActions.substitute_token(
                text,
                target_word=action.parameters.get("target"),
                replacement=action.parameters.get("replacement")
            )
            return modified
        
        elif action.action_type == ActionType.SEGMENT_SHOCK:
            modified, _ = TokenActions.add_segment_shock(
                text,
                shock_type=action.parameters.get("shock_type", "technical"),
                position=action.position
            )
            return modified
        
        elif action.action_type == ActionType.EMBEDDING_PERTURBATION:
            if "direction" in action.parameters:
                modified, _ = EmbeddingActions.apply_directional_perturbation(
                    text,
                    direction=action.parameters["direction"],
                    magnitude=action.magnitude
                )
            else:
                modified, _ = EmbeddingActions.add_gaussian_noise(
                    text,
                    magnitude=action.magnitude
                )
            return modified
        
        elif action.action_type == ActionType.TAIL_AMPLIFICATION:
            modifier, _ = LogitActions.amplify_tail(action.magnitude)
            return modifier + text
        
        else:
            return text
    
    @staticmethod
    def create_action_sequence(
        action_types: List[ActionType],
        magnitudes: Optional[List[float]] = None
    ) -> List[Action]:
        """
        Create a sequence of actions.
        
        Args:
            action_types: List of action types
            magnitudes: List of magnitudes (default 0.5 for all)
            
        Returns:
            List of Action objects
        """
        if magnitudes is None:
            magnitudes = [0.5] * len(action_types)
        
        return [
            Action(action_type=at, magnitude=mag)
            for at, mag in zip(action_types, magnitudes)
        ]


if __name__ == "__main__":
    # Test actions
    text = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme"
    
    print("Original:", text)
    print()
    
    # Token insertion
    modified, action = TokenActions.insert_token(text, token="<ISO-2847>", position=25)
    print(f"Action: {action}")
    print(f"Modified: {modified}")
    print()
    
    # Embedding perturbation
    modified, action = EmbeddingActions.apply_directional_perturbation(
        text, direction="technical", magnitude=0.7
    )
    print(f"Action: {action}")
    print(f"Modified: {modified}")
    print()
    
    # Tail amplification
    modifier, action = LogitActions.amplify_tail(magnitude=0.8)
    print(f"Action: {action}")
    print(f"Modified: {modifier + text}")
