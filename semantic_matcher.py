import json
import re
from functools import lru_cache
 
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
 
# How close in meaning a phrase must be (0 to 1). Higher = stricter.
# Tune it with evaluate.py: try 0.65, 0.70, 0.75, 0.80 and keep the best F1.
THRESHOLD = 0.75
 
 
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
        for alias in [skill] + list(aliases):
            if alias.startswith("re:"):  # regex aliases cannot be embedded
                continue
            texts.append(alias)
            owners.append(skill)
 
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
            if len(phrase) >= 2 and not phrase.isdigit():
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
    sample = "نبحث عن خبرة في تعلم الآلة و تحليل البيانات مع Python"
    print(find_semantic_skills(sample, with_scores=True))