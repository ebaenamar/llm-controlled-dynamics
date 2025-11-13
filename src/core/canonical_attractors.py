"""
Canonical Attractors: Guaranteed Memorized Texts

This module provides a curated collection of texts that are highly likely
to be memorized by LLMs, serving as stable attractors for perturbation experiments.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class Attractor:
    """A canonical text attractor."""
    text: str
    language: str
    source: str
    expected_memorization: float  # 0.0 to 1.0
    tokens_approx: int
    category: str
    
    def __repr__(self):
        return f"Attractor('{self.source[:30]}...', mem={self.expected_memorization:.2f})"


class CanonicalAttractors:
    """Collection of canonical memorized texts."""
    
    # Tier 1: Maximum Guarantee (>97% expected memorization)
    TIER1_LITERATURE = {
        "hamlet_to_be": Attractor(
            text="To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them.",
            language="en",
            source="Hamlet, Act III, Scene 1 - William Shakespeare",
            expected_memorization=0.98,
            tokens_approx=50,
            category="literature"
        ),
        
        "dickens_two_cities": Attractor(
            text="It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness.",
            language="en",
            source="A Tale of Two Cities - Charles Dickens",
            expected_memorization=0.97,
            tokens_approx=60,
            category="literature"
        ),
        
        "moby_dick": Attractor(
            text="Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.",
            language="en",
            source="Moby-Dick - Herman Melville",
            expected_memorization=0.96,
            tokens_approx=50,
            category="literature"
        ),
        
        "pride_prejudice": Attractor(
            text="It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
            language="en",
            source="Pride and Prejudice - Jane Austen",
            expected_memorization=0.97,
            tokens_approx=30,
            category="literature"
        ),
        
        "romeo_juliet": Attractor(
            text="But, soft! what light through yonder window breaks? It is the east, and Juliet is the sun.",
            language="en",
            source="Romeo and Juliet - William Shakespeare",
            expected_memorization=0.95,
            tokens_approx=25,
            category="literature"
        ),
    }
    
    TIER1_HISTORICAL = {
        "us_constitution": Attractor(
            text="We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.",
            language="en",
            source="US Constitution Preamble (1787)",
            expected_memorization=0.99,
            tokens_approx=60,
            category="legal"
        ),
        
        "declaration_independence": Attractor(
            text="We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.",
            language="en",
            source="Declaration of Independence (1776)",
            expected_memorization=0.99,
            tokens_approx=45,
            category="legal"
        ),
        
        "gettysburg_address": Attractor(
            text="Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.",
            language="en",
            source="Gettysburg Address - Abraham Lincoln",
            expected_memorization=0.98,
            tokens_approx=40,
            category="speech"
        ),
        
        "mlk_dream": Attractor(
            text="I have a dream that one day this nation will rise up and live out the true meaning of its creed: We hold these truths to be self-evident, that all men are created equal.",
            language="en",
            source="I Have a Dream - Martin Luther King Jr.",
            expected_memorization=0.97,
            tokens_approx=40,
            category="speech"
        ),
        
        "jfk_inaugural": Attractor(
            text="And so, my fellow Americans: ask not what your country can do for you—ask what you can do for your country.",
            language="en",
            source="JFK Inaugural Address (1961)",
            expected_memorization=0.96,
            tokens_approx=25,
            category="speech"
        ),
    }
    
    TIER1_RELIGIOUS = {
        "genesis_1_1": Attractor(
            text="In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
            language="en",
            source="Genesis 1:1-2 (King James Version)",
            expected_memorization=0.98,
            tokens_approx=50,
            category="religious"
        ),
        
        "john_1_1": Attractor(
            text="In the beginning was the Word, and the Word was with God, and the Word was God.",
            language="en",
            source="John 1:1 (King James Version)",
            expected_memorization=0.97,
            tokens_approx=20,
            category="religious"
        ),
        
        "psalm_23": Attractor(
            text="The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
            language="en",
            source="Psalm 23:1-2 (King James Version)",
            expected_memorization=0.95,
            tokens_approx=30,
            category="religious"
        ),
    }
    
    # Tier 2: High Guarantee (>90% expected memorization)
    TIER2_POETRY = {
        "frost_road": Attractor(
            text="Two roads diverged in a yellow wood, And sorry I could not travel both And be one traveler, long I stood And looked down one as far as I could To where it bent in the undergrowth;",
            language="en",
            source="The Road Not Taken - Robert Frost",
            expected_memorization=0.95,
            tokens_approx=50,
            category="poetry"
        ),
        
        "poe_raven": Attractor(
            text="Once upon a midnight dreary, while I pondered, weak and weary, Over many a quaint and curious volume of forgotten lore—",
            language="en",
            source="The Raven - Edgar Allan Poe",
            expected_memorization=0.94,
            tokens_approx=30,
            category="poetry"
        ),
    }
    
    TIER2_SCIENCE = {
        "newton_first_law": Attractor(
            text="Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impressed thereon.",
            language="en",
            source="Principia Mathematica - Isaac Newton",
            expected_memorization=0.93,
            tokens_approx=30,
            category="science"
        ),
        
        "darwin_origin": Attractor(
            text="There is grandeur in this view of life, with its several powers, having been originally breathed into a few forms or into one; and that, whilst this planet has gone cycling on according to the fixed law of gravity, from so simple a beginning endless forms most beautiful and most wonderful have been, and are being, evolved.",
            language="en",
            source="On the Origin of Species - Charles Darwin",
            expected_memorization=0.90,
            tokens_approx=70,
            category="science"
        ),
    }
    
    # Multilingual
    MULTILINGUAL = {
        "quijote_spanish": Attractor(
            text="En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor.",
            language="es",
            source="Don Quijote - Miguel de Cervantes",
            expected_memorization=0.90,
            tokens_approx=40,
            category="literature"
        ),
        
        "dante_inferno": Attractor(
            text="Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, ché la diritta via era smarrita.",
            language="it",
            source="Divina Commedia - Dante Alighieri",
            expected_memorization=0.85,
            tokens_approx=25,
            category="literature"
        ),
    }
    
    @classmethod
    def get_all_attractors(cls) -> Dict[str, Attractor]:
        """Get all attractors as a single dictionary."""
        all_attractors = {}
        
        for tier_dict in [
            cls.TIER1_LITERATURE,
            cls.TIER1_HISTORICAL,
            cls.TIER1_RELIGIOUS,
            cls.TIER2_POETRY,
            cls.TIER2_SCIENCE,
            cls.MULTILINGUAL
        ]:
            all_attractors.update(tier_dict)
        
        return all_attractors
    
    @classmethod
    def get_tier1(cls) -> Dict[str, Attractor]:
        """Get only Tier 1 attractors (highest guarantee)."""
        tier1 = {}
        tier1.update(cls.TIER1_LITERATURE)
        tier1.update(cls.TIER1_HISTORICAL)
        tier1.update(cls.TIER1_RELIGIOUS)
        return tier1
    
    @classmethod
    def get_by_category(cls, category: str) -> Dict[str, Attractor]:
        """Get attractors by category."""
        all_attractors = cls.get_all_attractors()
        return {
            name: attr for name, attr in all_attractors.items()
            if attr.category == category
        }
    
    @classmethod
    def get_by_language(cls, language: str) -> Dict[str, Attractor]:
        """Get attractors by language."""
        all_attractors = cls.get_all_attractors()
        return {
            name: attr for name, attr in all_attractors.items()
            if attr.language == language
        }
    
    @classmethod
    def get_recommended_suite(cls, size: str = "minimal") -> Dict[str, Attractor]:
        """
        Get recommended suite for experiments.
        
        Args:
            size: "minimal" (5), "standard" (10), or "comprehensive" (15+)
        """
        if size == "minimal":
            # Top 5 for quick validation
            return {
                "hamlet_to_be": cls.TIER1_LITERATURE["hamlet_to_be"],
                "dickens_two_cities": cls.TIER1_LITERATURE["dickens_two_cities"],
                "us_constitution": cls.TIER1_HISTORICAL["us_constitution"],
                "gettysburg_address": cls.TIER1_HISTORICAL["gettysburg_address"],
                "genesis_1_1": cls.TIER1_RELIGIOUS["genesis_1_1"],
            }
        
        elif size == "standard":
            # Top 10 for standard experiments
            suite = cls.get_recommended_suite("minimal")
            suite.update({
                "moby_dick": cls.TIER1_LITERATURE["moby_dick"],
                "pride_prejudice": cls.TIER1_LITERATURE["pride_prejudice"],
                "mlk_dream": cls.TIER1_HISTORICAL["mlk_dream"],
                "frost_road": cls.TIER2_POETRY["frost_road"],
                "newton_first_law": cls.TIER2_SCIENCE["newton_first_law"],
            })
            return suite
        
        else:  # comprehensive
            return cls.get_tier1()
    
    @classmethod
    def get_short_attractors(cls, max_tokens: int = 30) -> Dict[str, Attractor]:
        """Get attractors with token count below threshold."""
        all_attractors = cls.get_all_attractors()
        return {
            name: attr for name, attr in all_attractors.items()
            if attr.tokens_approx <= max_tokens
        }
    
    @classmethod
    def get_long_attractors(cls, min_tokens: int = 50) -> Dict[str, Attractor]:
        """Get attractors with token count above threshold."""
        all_attractors = cls.get_all_attractors()
        return {
            name: attr for name, attr in all_attractors.items()
            if attr.tokens_approx >= min_tokens
        }


def validate_attractor_memorization(
    attractor: Attractor,
    model_response: str,
    threshold: float = 0.8
) -> tuple[float, bool]:
    """
    Validate that a model has memorized an attractor.
    
    Args:
        attractor: The canonical attractor
        model_response: Model's completion
        threshold: Minimum score to consider memorized
        
    Returns:
        (memorization_score, is_memorized)
    """
    from ..core.metrics import TextMetrics
    
    # Compute memorization score
    result = TextMetrics.memorization_score(
        model_response,
        attractor.text,
        threshold=threshold
    )
    
    score = result.value
    is_memorized = score >= threshold
    
    return score, is_memorized


if __name__ == "__main__":
    # Demo usage
    attractors = CanonicalAttractors()
    
    print("=== RECOMMENDED MINIMAL SUITE ===\n")
    minimal = attractors.get_recommended_suite("minimal")
    for name, attr in minimal.items():
        print(f"{name}:")
        print(f"  Source: {attr.source}")
        print(f"  Expected mem: {attr.expected_memorization:.2f}")
        print(f"  Text: {attr.text[:80]}...")
        print()
    
    print("\n=== STATISTICS ===")
    all_attr = attractors.get_all_attractors()
    print(f"Total attractors: {len(all_attr)}")
    print(f"Tier 1 (>97%): {len(attractors.get_tier1())}")
    print(f"English: {len(attractors.get_by_language('en'))}")
    print(f"Short (<30 tokens): {len(attractors.get_short_attractors(30))}")
    print(f"Long (>50 tokens): {len(attractors.get_long_attractors(50))}")
    
    print("\n=== BY CATEGORY ===")
    for category in ["literature", "legal", "speech", "religious", "poetry", "science"]:
        cat_attractors = attractors.get_by_category(category)
        if cat_attractors:
            print(f"{category.capitalize()}: {len(cat_attractors)}")
