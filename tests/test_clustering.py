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
