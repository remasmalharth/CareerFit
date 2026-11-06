
from functools import lru_cache
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer(MODEL_NAME)


def match_evidence(resume_sentences, job_requirements):
    model = get_model()

    resume_embeddings = model.encode(
        resume_sentences,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    job_embeddings = model.encode(
        job_requirements,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        job_embeddings,
        resume_embeddings
    )

    results = []

    for i, requirement in enumerate(job_requirements):
        best_index = similarities[i].argmax().item()
        best_score = similarities[i][best_index].item()

        if best_score >= 0.60:
            status = "Matched"
        elif best_score >= 0.40:
            status = "Uncertain"
        else:
            status = "Missing Evidence"

        results.append({
            "requirement": requirement,
            "evidence": resume_sentences[best_index],
            "similarity": round(best_score, 3),
            "status": status
        })

    return results


if __name__ == "__main__":
    resume = [
        "Developed backend APIs using FastAPI.",
        "Built machine learning models with Python.",
        "Worked with SQL databases."
    ]

    job = [
        "Experience developing REST APIs.",
        "Knowledge of machine learning.",
        "Experience with cloud infrastructure."
    ]

    for result in match_evidence(resume, job):
        print(result)
