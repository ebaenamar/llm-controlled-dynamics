# Atractores Canónicos Garantizadamente Memorizados

## Criterios de Selección

Un atractor canónico debe cumplir:

1. **Universalidad**: Presente en todos los corpus de entrenamiento
2. **Invariancia**: Texto idéntico en todas las fuentes
3. **Alta frecuencia**: Repetido miles de veces en internet
4. **Verificabilidad**: Fácil de medir desviación exacta
5. **Longitud adecuada**: 20-100 tokens para medir trayectorias

## 🌟 Tier 1: Máxima Garantía (>99.9% memorización esperada)

### 1. Declaraciones Legales y Constitucionales

```python
ATTRACTORS_LEGAL = {
    "us_constitution_preamble": {
        "text": "We the People of the United States, in Order to form a more perfect Union, establish Justice, insure domestic Tranquility, provide for the common defence, promote the general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, do ordain and establish this Constitution for the United States of America.",
        "language": "en",
        "source": "US Constitution (1787)",
        "expected_memorization": 0.99,
        "tokens_approx": 60
    },
    
    "declaration_independence": {
        "text": "We hold these truths to be self-evident, that all men are created equal, that they are endowed by their Creator with certain unalienable Rights, that among these are Life, Liberty and the pursuit of Happiness.",
        "language": "en",
        "source": "Declaration of Independence (1776)",
        "expected_memorization": 0.99,
        "tokens_approx": 45
    },
    
    "magna_carta": {
        "text": "No free man shall be seized or imprisoned, or stripped of his rights or possessions, or outlawed or exiled, or deprived of his standing in any other way, nor will we proceed with force against him, or send others to do so, except by the lawful judgement of his equals or by the law of the land.",
        "language": "en",
        "source": "Magna Carta (1215)",
        "expected_memorization": 0.85,
        "tokens_approx": 70
    }
}
```

### 2. Literatura Clásica (Dominio Público)

```python
ATTRACTORS_LITERATURE = {
    "shakespeare_hamlet": {
        "text": "To be, or not to be, that is the question: Whether 'tis nobler in the mind to suffer The slings and arrows of outrageous fortune, Or to take arms against a sea of troubles And by opposing end them.",
        "language": "en",
        "source": "Hamlet, Act III, Scene 1",
        "expected_memorization": 0.98,
        "tokens_approx": 50
    },
    
    "shakespeare_romeo": {
        "text": "But, soft! what light through yonder window breaks? It is the east, and Juliet is the sun.",
        "language": "en",
        "source": "Romeo and Juliet, Act II, Scene 2",
        "expected_memorization": 0.95,
        "tokens_approx": 25
    },
    
    "dickens_tale_two_cities": {
        "text": "It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, it was the season of Darkness.",
        "language": "en",
        "source": "A Tale of Two Cities (1859)",
        "expected_memorization": 0.97,
        "tokens_approx": 60
    },
    
    "moby_dick": {
        "text": "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world.",
        "language": "en",
        "source": "Moby-Dick (1851)",
        "expected_memorization": 0.96,
        "tokens_approx": 50
    },
    
    "pride_prejudice": {
        "text": "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife.",
        "language": "en",
        "source": "Pride and Prejudice (1813)",
        "expected_memorization": 0.97,
        "tokens_approx": 30
    },
    
    "quijote_spanish": {
        "text": "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, rocín flaco y galgo corredor.",
        "language": "es",
        "source": "Don Quijote (1605)",
        "expected_memorization": 0.90,  # Menor para modelos no-españoles
        "tokens_approx": 40
    },
    
    "dante_inferno": {
        "text": "Nel mezzo del cammin di nostra vita mi ritrovai per una selva oscura, ché la diritta via era smarrita.",
        "language": "it",
        "source": "Divina Commedia - Inferno (1320)",
        "expected_memorization": 0.85,
        "tokens_approx": 25
    }
}
```

### 3. Textos Religiosos

```python
ATTRACTORS_RELIGIOUS = {
    "bible_genesis": {
        "text": "In the beginning God created the heaven and the earth. And the earth was without form, and void; and darkness was upon the face of the deep. And the Spirit of God moved upon the face of the waters.",
        "language": "en",
        "source": "Genesis 1:1-2 (KJV)",
        "expected_memorization": 0.98,
        "tokens_approx": 50
    },
    
    "bible_john": {
        "text": "In the beginning was the Word, and the Word was with God, and the Word was God.",
        "language": "en",
        "source": "John 1:1 (KJV)",
        "expected_memorization": 0.97,
        "tokens_approx": 20
    },
    
    "lords_prayer": {
        "text": "Our Father which art in heaven, Hallowed be thy name. Thy kingdom come, Thy will be done in earth, as it is in heaven. Give us this day our daily bread. And forgive us our debts, as we forgive our debtors.",
        "language": "en",
        "source": "Matthew 6:9-12 (KJV)",
        "expected_memorization": 0.96,
        "tokens_approx": 55
    },
    
    "psalm_23": {
        "text": "The Lord is my shepherd; I shall not want. He maketh me to lie down in green pastures: he leadeth me beside the still waters.",
        "language": "en",
        "source": "Psalm 23:1-2 (KJV)",
        "expected_memorization": 0.95,
        "tokens_approx": 30
    }
}
```

### 4. Discursos Históricos

```python
ATTRACTORS_SPEECHES = {
    "gettysburg_address": {
        "text": "Four score and seven years ago our fathers brought forth on this continent, a new nation, conceived in Liberty, and dedicated to the proposition that all men are created equal.",
        "language": "en",
        "source": "Gettysburg Address (1863)",
        "expected_memorization": 0.98,
        "tokens_approx": 40
    },
    
    "i_have_a_dream": {
        "text": "I have a dream that one day this nation will rise up and live out the true meaning of its creed: We hold these truths to be self-evident, that all men are created equal.",
        "language": "en",
        "source": "MLK Jr. Speech (1963)",
        "expected_memorization": 0.97,
        "tokens_approx": 40
    },
    
    "jfk_inaugural": {
        "text": "And so, my fellow Americans: ask not what your country can do for you—ask what you can do for your country.",
        "language": "en",
        "source": "JFK Inaugural Address (1961)",
        "expected_memorization": 0.96,
        "tokens_approx": 25
    },
    
    "churchill_finest_hour": {
        "text": "Let us therefore brace ourselves to our duties, and so bear ourselves, that if the British Empire and its Commonwealth last for a thousand years, men will still say, This was their finest hour.",
        "language": "en",
        "source": "Churchill Speech (1940)",
        "expected_memorization": 0.94,
        "tokens_approx": 45
    }
}
```

## 🥈 Tier 2: Alta Garantía (>95% memorización esperada)

### 5. Poesía Clásica

```python
ATTRACTORS_POETRY = {
    "frost_road_not_taken": {
        "text": "Two roads diverged in a yellow wood, And sorry I could not travel both And be one traveler, long I stood And looked down one as far as I could To where it bent in the undergrowth;",
        "language": "en",
        "source": "The Road Not Taken - Robert Frost (1916)",
        "expected_memorization": 0.95,
        "tokens_approx": 50
    },
    
    "poe_raven": {
        "text": "Once upon a midnight dreary, while I pondered, weak and weary, Over many a quaint and curious volume of forgotten lore—",
        "language": "en",
        "source": "The Raven - Edgar Allan Poe (1845)",
        "expected_memorization": 0.94,
        "tokens_approx": 30
    },
    
    "wordsworth_daffodils": {
        "text": "I wandered lonely as a cloud That floats on high o'er vales and hills, When all at once I saw a crowd, A host, of golden daffodils;",
        "language": "en",
        "source": "I Wandered Lonely as a Cloud (1807)",
        "expected_memorization": 0.92,
        "tokens_approx": 35
    }
}
```

### 6. Fórmulas y Textos Científicos

```python
ATTRACTORS_SCIENCE = {
    "einstein_emc2": {
        "text": "E = mc²",
        "language": "universal",
        "source": "Einstein's mass-energy equivalence",
        "expected_memorization": 0.99,
        "tokens_approx": 5
    },
    
    "newton_first_law": {
        "text": "Every body perseveres in its state of rest, or of uniform motion in a right line, unless it is compelled to change that state by forces impressed thereon.",
        "language": "en",
        "source": "Principia Mathematica (1687)",
        "expected_memorization": 0.93,
        "tokens_approx": 30
    },
    
    "darwin_origin": {
        "text": "There is grandeur in this view of life, with its several powers, having been originally breathed into a few forms or into one; and that, whilst this planet has gone cycling on according to the fixed law of gravity, from so simple a beginning endless forms most beautiful and most wonderful have been, and are being, evolved.",
        "language": "en",
        "source": "On the Origin of Species (1859)",
        "expected_memorization": 0.90,
        "tokens_approx": 70
    }
}
```

## 🥉 Tier 3: Cultura Popular Moderna (>85% memorización)

### 7. Cine y Cultura Pop

```python
ATTRACTORS_POPCULTURE = {
    "star_wars_opening": {
        "text": "A long time ago in a galaxy far, far away....",
        "language": "en",
        "source": "Star Wars (1977)",
        "expected_memorization": 0.95,
        "tokens_approx": 12
    },
    
    "lotr_ring_verse": {
        "text": "One Ring to rule them all, One Ring to find them, One Ring to bring them all, and in the darkness bind them.",
        "language": "en",
        "source": "The Lord of the Rings (1954)",
        "expected_memorization": 0.93,
        "tokens_approx": 30
    },
    
    "wizard_of_oz": {
        "text": "There's no place like home.",
        "language": "en",
        "source": "The Wizard of Oz (1939)",
        "expected_memorization": 0.92,
        "tokens_approx": 7
    }
}
```

## 📊 Recomendaciones por Caso de Uso

### Para Experimentos de Robustez Máxima
**Usar**: Tier 1 - Legal/Literatura clásica
- Memorización garantizada >97%
- Texto invariante
- Fácil verificación

**Top 5**:
1. "To be, or not to be..." (Hamlet)
2. "We the People..." (US Constitution)
3. "It was the best of times..." (Dickens)
4. "Call me Ishmael" (Moby Dick)
5. "Four score and seven years ago..." (Gettysburg)

### Para Experimentos Multilingües
**Usar**: Textos en múltiples idiomas
- Don Quijote (español)
- Dante (italiano)
- Bible (múltiples traducciones)

### Para Detectar Phase Transitions
**Usar**: Textos con longitud variable
- Cortos (5-10 tokens): "E = mc²", "To be or not to be"
- Medios (30-50 tokens): Hamlet, Dickens
- Largos (60-100 tokens): Constitution, Darwin

## 🔬 Protocolo de Validación

Antes de usar un atractor, validar con:

```python
def validate_attractor(text, model, threshold=0.8):
    """
    Valida que un texto sea un atractor fuerte.
    
    Returns:
        - memorization_score: 0-1
        - is_valid: bool (score > threshold)
    """
    response = model.generate(text[:20])  # Primeras palabras
    score = compute_memorization(response, text)
    return score, score > threshold
```

## 📝 Notas de Implementación

1. **Normalización**: Ignorar puntuación/capitalización en comparaciones
2. **Tokenización**: Usar tokenizer del modelo específico
3. **Longitud**: Generar al menos 2x la longitud del atractor
4. **Temperatura**: Usar T=0.0 para máxima reproducibilidad en validación

## 🎯 Atractores Recomendados para Paper NeurIPS

**Suite Mínima (5 atractores)**:
1. Hamlet "To be or not to be" (poesía/drama)
2. Dickens "It was the best of times" (prosa narrativa)
3. US Constitution Preamble (texto legal)
4. Gettysburg Address (discurso histórico)
5. Genesis 1:1 (texto religioso)

**Suite Completa (15 atractores)**:
- Añadir: Moby Dick, Pride & Prejudice, Shakespeare Romeo, MLK Dream, Churchill, Frost, Poe, Newton, Darwin, Star Wars

Esto proporciona:
- Diversidad de géneros
- Diferentes épocas (1215-1977)
- Múltiples longitudes (7-70 tokens)
- Alta confianza de memorización (>90%)
