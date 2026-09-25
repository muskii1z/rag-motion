"""Step 7 demo: what an embedding looks like, and how similarity ranks text.

Run from the project folder:
    uv run python scripts/embedding_demo.py
    uv run python scripts/embedding_demo.py "your own question"
"""

import sys

from ragmotion.embeddings import cosine_similarity, embed_documents, embed_query

# Short stand-ins for exercise descriptions (embedded as "documents").
DOCUMENTS = {
    "romanian deadlift": "Dumbbell Romanian deadlift: push the hips back and lower the weights along the legs to train hamstrings and glutes.",
    "kettlebell swing": "Kettlebell swing: an explosive hip hinge that drives the bell to chest height with a powerful hip snap.",
    "goblet squat": "Goblet squat: squat holding one dumbbell at the chest to build leg strength and squat technique.",
    "overhead press": "Dumbbell overhead press: press the weights from the shoulders to overhead to build shoulder strength.",
    "band pull-apart": "Band pull-apart: stretch a resistance band across the chest to train the rear shoulders and upper back.",
}

DEFAULT_QUESTIONS = [
    "hip hinge exercise with dumbbells",  # plain words, no exact name
    "beginner RDL",                       # coach jargon: RDL = Romanian deadlift
]


def main() -> None:
    questions = sys.argv[1:] or DEFAULT_QUESTIONS

    names = list(DOCUMENTS)
    doc_vectors = embed_documents(list(DOCUMENTS.values()))

    v = doc_vectors[0]
    print(f"One embedding ('{names[0]}'): {len(v)} numbers")
    print(f"  first 8: {[round(x, 4) for x in v[:8]]}")
    print(f"  last 3:  {[round(x, 4) for x in v[-3:]]}\n")

    for question in questions:
        q = embed_query(question)
        ranked = sorted(
            ((cosine_similarity(q, d), name) for name, d in zip(names, doc_vectors)),
            reverse=True,
        )
        print(f'QUESTION: "{question}"')
        for score, name in ranked:
            bar = "#" * round(score * 40)
            print(f"  {score:.3f}  {name:<18} {bar}")
        print()


if __name__ == "__main__":
    main()
