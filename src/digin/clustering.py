import math
import os

import numpy as np

# Use cached model offline — don't phone home to HuggingFace on every run
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
from digin.models import Cluster, Post

_model_cache: SentenceTransformer | None = None

def _get_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    global _model_cache
    if _model_cache is None:
        _model_cache = SentenceTransformer(model_name)
    return _model_cache

def cluster_posts(
    posts: list[Post],
    num_clusters: int | None = None,
    min_posts: int = 6,
    model_name: str = "all-MiniLM-L6-v2",
) -> tuple[list[int] | None, list[Cluster] | None]:
    if len(posts) < min_posts:
        return None, None

    model = _get_model(model_name)
    contents = [p.content for p in posts]
    embeddings = model.encode(contents, show_progress_bar=False)

    if num_clusters is None:
        num_clusters = _auto_select_k(embeddings)

    num_clusters = min(num_clusters, len(posts) - 1)
    num_clusters = max(num_clusters, 2)

    kmeans = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(embeddings).tolist()

    cluster_docs = _group_by_cluster(contents, labels, num_clusters)
    keywords_per_cluster = extract_keywords(cluster_docs, top_n=5)

    from datetime import datetime, timezone
    clusters = []
    for i in range(num_clusters):
        kw = keywords_per_cluster[i]
        summary = " & ".join(kw[:3]).title() if kw else f"Cluster {i + 1}"
        post_count = labels.count(i)
        clusters.append(Cluster(
            id=i + 1,
            keywords=kw,
            summary=summary,
            post_count=post_count,
            created_at=datetime.now(timezone.utc),
        ))

    labels = [label + 1 for label in labels]
    return labels, clusters

def _auto_select_k(embeddings: np.ndarray) -> int:
    max_k = min(int(math.floor(math.sqrt(len(embeddings)))), 20)
    max_k = max(max_k, 2)
    best_k = 2
    best_score = -1.0
    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        trial_labels = kmeans.fit_predict(embeddings)
        if len(set(trial_labels)) < 2:
            continue
        score = silhouette_score(embeddings, trial_labels)
        if score > best_score:
            best_score = score
            best_k = k
    return best_k

def _group_by_cluster(contents: list[str], labels: list[int], num_clusters: int) -> list[str]:
    cluster_docs = [""] * num_clusters
    for content, label in zip(contents, labels):
        cluster_docs[label] += " " + content
    return cluster_docs

def extract_keywords(docs: list[str], top_n: int = 5) -> list[list[str]]:
    vectorizer = TfidfVectorizer(max_features=1000, stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(docs)
    feature_names = vectorizer.get_feature_names_out()
    keywords = []
    for i in range(len(docs)):
        row = tfidf_matrix[i].toarray().flatten()
        top_indices = row.argsort()[-top_n:][::-1]
        top_words = [feature_names[idx] for idx in top_indices if row[idx] > 0]
        keywords.append(top_words)
    return keywords
