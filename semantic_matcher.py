"""Semantic skill matching with multilingual sentence embeddings.

Idea: cut the text into short phrases (1 to 3 words), turn every phrase and
every skill alias into a vector, and call a skill "found" when a phrase is
close in meaning to one of its aliases. This is how "تعلم الآلة" can match
"Machine Learning" even though no word is the same.
"""
import json
import re
from functools import lru_cache

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# How close in meaning a phrase must be (0 to 1). Higher = stricter.
# Tune it with evaluate.py: try 0.65, 0.70, 0.75, 0.80 and keep the best F1.
THRESHOLD = 0.75

# Only skills that are CONCEPTS use the semantic layer. Names of tools and
# languages (Java, Vue, Azure, Kotlin...) are not words, so embeddings match
# them to random text. Keyword matching already finds those perfectly.
SEMANTIC_SKILLS = {
    "Machine Learning",
    "Deep Learning",
    "NLP",
    "Computer Vision",
    "Data Analysis",
    "Data Visualization",
    "Statistics",
    "Databases",
    "APIs",
    "Cybersecurity",
    "Networking",
    "Software Testing",
    "Object-Oriented Programming",
    "Data Structures",
    "Algorithms",
    "Agile",
    "Debugging",
    "Communication",
    "Teamwork",
    "Problem Solving",
    "Project Management",
}


def _load_skill_aliases():
    """Get {skill: [aliases]} from matcher.py, or from skills.json."""
    try:
        from matcher import SKILL_ALIASES

        return SKILL_ALIASES
    except ImportError:
        pass

    with open("skills.json", encoding="utf-8") as f:
        raw = json.load(f)

    return {
        name: (value["aliases"] if isinstance(value, dict) else value)
        for name, value in raw.items()
    }


@lru_cache(maxsize=1)
def get_model():
    # Imported here so the app still starts if the package is not installed.
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def _alias_data():
    """Embed every skill name and alias once, then reuse."""
    texts, owners = [], []

    for skill, aliases in _load_skill_aliases().items():
        if skill not in SEMANTIC_SKILLS:
            continue
        for alias in [skill] + list(aliases):
            if alias.startswith("re:"):  # regex aliases cannot be embedded
                continue
            texts.append(alias)
            owners.append(skill)

    if not texts:
        return [], [], None

    embeddings = get_model().encode(
        texts, convert_to_tensor=True, normalize_embeddings=True
    )
    return texts, owners, embeddings


def candidate_phrases(text, max_words=3):
    """All 1 to 3 word phrases in the text."""
    words = [w.strip(".-/") for w in re.findall(r"[\w+#./\-]+", text)]
    words = [w for w in words if w]

    phrases = set()
    for n in range(1, max_words + 1):
        for i in range(len(words) - n + 1):
            phrase = " ".join(words[i : i + n])
            if len(phrase) >= 4 and not phrase.isdigit():
                phrases.add(phrase)

    return sorted(phrases)


def find_semantic_skills(text, threshold=None, with_scores=False):
    """Skills whose meaning appears in the text (even with different words)."""
    from sentence_transformers import util

    threshold = THRESHOLD if threshold is None else threshold

    phrases = candidate_phrases(text)
    if not phrases:
        return {} if with_scores else []

    _, owners, alias_embeddings = _alias_data()
    if not owners:
        return {} if with_scores else []

    phrase_embeddings = get_model().encode(
        phrases,
        convert_to_tensor=True,
        normalize_embeddings=True,
        batch_size=64,
    )

    similarity = util.cos_sim(phrase_embeddings, alias_embeddings)
    best_per_alias = similarity.max(dim=0).values.tolist()

    found = {}
    for index, score in enumerate(best_per_alias):
        if score >= threshold:
            skill = owners[index]
            found[skill] = max(found.get(skill, 0.0), round(score, 3))

    if with_scores:
        return dict(sorted(found.items(), key=lambda kv: -kv[1]))
    return sorted(found, key=found.get, reverse=True)


def find_skills_hybrid(text, threshold=None):
    """Keyword matches (precise) plus semantic matches (flexible)."""
    from matcher import find_skills

    combined = list(find_skills(text))
    for skill in find_semantic_skills(text, threshold):
        if skill not in combined:
            combined.append(skill)
    return combined


if __name__ == "__main__":
    # None of these phrases are written in the aliases on purpose.
    sample = "نبحث عن خبرة في بناء نماذج الذكاء الاصطناعي وتحليل المعلومات"
    print(find_semantic_skills(sample, threshold=0.6, with_scores=True))
