from datetime import datetime, timezone
from digin.models import Post, Cluster
from digin.storage import PostStorage

def _make_post(id: str = "urn:li:activity:123", **kwargs) -> Post:
    defaults = {
        "id": id,
        "url": f"https://linkedin.com/feed/update/{id}",
        "author": "Test Author",
        "author_profile": "https://linkedin.com/in/test",
        "content": "Test post content about AI.",
        "post_type": "text",
        "saved_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "engagement": {"likes": 100, "comments": 10},
        "links": [],
        "cluster_id": None,
    }
    defaults.update(kwargs)
    return Post(**defaults)

def test_save_and_load_posts():
    storage = PostStorage(":memory:")
    posts = [_make_post("urn:li:activity:1"), _make_post("urn:li:activity:2")]
    storage.save_posts(posts)
    loaded = storage.load_posts()
    assert len(loaded) == 2
    assert loaded[0].id == "urn:li:activity:1"

def test_upsert_updates_existing():
    storage = PostStorage(":memory:")
    post = _make_post(engagement={"likes": 100, "comments": 10})
    storage.save_posts([post])
    updated = _make_post(engagement={"likes": 200, "comments": 20})
    storage.save_posts([updated])
    loaded = storage.load_posts()
    assert len(loaded) == 1
    assert loaded[0].engagement == {"likes": 200, "comments": 20}

def test_save_and_load_clusters():
    storage = PostStorage(":memory:")
    posts = [
        _make_post("urn:li:activity:1", cluster_id=1),
        _make_post("urn:li:activity:2", cluster_id=1),
        _make_post("urn:li:activity:3", cluster_id=2),
    ]
    storage.save_posts(posts)
    clusters = [
        Cluster(id=1, keywords=["ai", "ml"], summary="AI & ML", post_count=2,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
        Cluster(id=2, keywords=["devtools"], summary="DevTools", post_count=1,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    storage.save_clusters(clusters)
    loaded = storage.load_clusters()
    assert len(loaded) == 2
    assert loaded[0].keywords == ["ai", "ml"]

def test_update_post_clusters():
    storage = PostStorage(":memory:")
    posts = [_make_post("urn:li:activity:1"), _make_post("urn:li:activity:2")]
    storage.save_posts(posts)
    storage.update_post_clusters({"urn:li:activity:1": 1, "urn:li:activity:2": 2})
    loaded = storage.load_posts()
    ids_to_clusters = {p.id: p.cluster_id for p in loaded}
    assert ids_to_clusters["urn:li:activity:1"] == 1
    assert ids_to_clusters["urn:li:activity:2"] == 2

def test_clear_clusters():
    storage = PostStorage(":memory:")
    posts = [_make_post("urn:li:activity:1", cluster_id=1)]
    storage.save_posts(posts)
    clusters = [
        Cluster(id=1, keywords=["ai"], summary="AI", post_count=1,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc)),
    ]
    storage.save_clusters(clusters)
    storage.clear_clusters()
    assert len(storage.load_clusters()) == 0
    loaded_posts = storage.load_posts()
    assert loaded_posts[0].cluster_id is None

def test_load_posts_by_cluster():
    storage = PostStorage(":memory:")
    posts = [
        _make_post("urn:li:activity:1", cluster_id=1),
        _make_post("urn:li:activity:2", cluster_id=2),
        _make_post("urn:li:activity:3", cluster_id=1),
    ]
    storage.save_posts(posts)
    cluster_1_posts = storage.load_posts(cluster_id=1)
    assert len(cluster_1_posts) == 2
    assert all(p.cluster_id == 1 for p in cluster_1_posts)

def test_post_count():
    storage = PostStorage(":memory:")
    assert storage.post_count() == 0
    storage.save_posts([_make_post("urn:li:activity:1")])
    assert storage.post_count() == 1
