from datetime import datetime, timezone
from digin.clustering import cluster_posts, extract_keywords
from digin.models import Post

def _make_posts(topics: list[tuple[str, int]]) -> list[Post]:
    posts = []
    idx = 0
    for content_base, count in topics:
        for i in range(count):
            idx += 1
            posts.append(Post(
                id=f"urn:li:activity:{idx}",
                url=f"https://linkedin.com/feed/update/urn:li:activity:{idx}",
                author=f"Author {idx}",
                author_profile=f"https://linkedin.com/in/author{idx}",
                content=f"{content_base} post number {i}",
                post_type="text",
                saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                engagement={"likes": 10, "comments": 1},
                links=[],
                cluster_id=None,
            ))
    return posts

def test_cluster_posts_returns_labels():
    posts = _make_posts([
        ("artificial intelligence machine learning deep neural networks", 5),
        ("leadership management team culture hiring", 5),
    ])
    labels, clusters = cluster_posts(posts, num_clusters=2)
    assert len(labels) == 10
    assert len(clusters) == 2
    assert all(isinstance(label, int) for label in labels)

def test_cluster_posts_auto_k():
    posts = _make_posts([
        ("artificial intelligence machine learning neural networks transformers", 5),
        ("leadership management team hiring culture organization", 5),
        ("devtools developer experience cli tooling automation", 5),
    ])
    labels, clusters = cluster_posts(posts, num_clusters=None)
    assert len(labels) == 15
    assert len(clusters) >= 2

def test_extract_keywords():
    docs = [
        "artificial intelligence machine learning deep learning neural networks",
        "leadership management team culture hiring organizational",
    ]
    keywords = extract_keywords(docs, top_n=3)
    assert len(keywords) == 2
    assert len(keywords[0]) == 3
    assert all(isinstance(kw, str) for kw in keywords[0])

def test_cluster_posts_too_few():
    posts = _make_posts([("only a few posts", 3)])
    labels, clusters = cluster_posts(posts, num_clusters=2)
    assert labels is None
    assert clusters is None


def test_auto_select_k_with_single_cluster_trial(monkeypatch):
    """Test _auto_select_k skips k values where KMeans collapses to a single cluster,
    and exercises the False branch of 'if score > best_score' when a later k scores lower.

    We use 25 embeddings so sqrt(25)=5 → max_k=5, range(2,6) → 4 k values tried.
    Call 1 (k=2): all-same labels → continue (line 75)
    Call 2 (k=3): 2 distinct labels → high score sets best_k=3
    Call 3 (k=4): 2 distinct labels but silhouette_score will be lower → 77->71 False branch
    Call 4 (k=5): 2 distinct labels → similar
    """
    import numpy as np
    import digin.clustering as clustering_module

    call_count = [0]

    class FakeKMeans:
        def __init__(self, n_clusters, random_state, n_init):
            self.n_clusters = n_clusters

        def fit_predict(self, embeddings):
            call_count[0] += 1
            if call_count[0] == 1:
                # First call: all labels same → triggers continue (line 75)
                return np.zeros(len(embeddings), dtype=int)
            else:
                # Subsequent calls: alternate between two clusters
                labels = np.zeros(len(embeddings), dtype=int)
                labels[len(embeddings) // 2:] = 1
                return labels

    monkeypatch.setattr(clustering_module, "KMeans", FakeKMeans)

    # Use 25 embeddings with clear two-cluster structure so silhouette_score is stable
    # but the False branch on 'if score > best_score' gets hit on repeated same-score calls
    embeddings = np.vstack([
        np.ones((12, 8), dtype=np.float32),
        np.zeros((13, 8), dtype=np.float32),
    ])
    result = clustering_module._auto_select_k(embeddings)
    assert result >= 2
