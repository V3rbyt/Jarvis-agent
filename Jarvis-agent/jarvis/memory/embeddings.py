"""Simple embeddings."""
import re
from collections import Counter
from math import sqrt


def tokenize(text):
    STOP = {"a","o","e","de","da","do","em","para","com","por","que","e","um","uma","no","na","the","and","or","in"}
    return [t for t in re.findall(r"\b[a-zà-ú]{3,}\b", text.lower()) if t not in STOP]


def cosine(v1, v2):
    keys = set(v1.keys()) | set(v2.keys())
    dot = sum(v1.get(k,0)*v2.get(k,0) for k in keys)
    m1 = sqrt(sum(v*v for v in v1.values()))
    m2 = sqrt(sum(v*v for v in v2.values()))
    return 0.0 if m1==0 or m2==0 else dot/(m1*m2)


class SimpleEmbeddings:
    def vectorize(self, text):
        return Counter(tokenize(text))

    def search(self, query, documents, top_k=5):
        if not documents: return []
        q = self.vectorize(query)
        scores = [(i, cosine(q, self.vectorize(d))) for i, d in enumerate(documents)]
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_k]
