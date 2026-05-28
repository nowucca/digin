import json
from datetime import datetime, timezone

from digin.models import Cluster, Post


def test_post_creation():
    post = Post(
        id="urn:li:activity:123",
        url="https://linkedin.com/feed/update/urn:li:activity:123",
        author="Test Author",
        author_profile="https://linkedin.com/in/testauthor",
        content="This is a test post about AI and machine learning.",
        post_type="text",
        saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        engagement={"likes": 100, "comments": 10},
        links=["https://example.com"],
        cluster_id=None,
    )
    assert post.id == "urn:li:activity:123"
    assert post.author == "Test Author"
    assert post.cluster_id is None


def test_post_to_dict():
    post = Post(
        id="urn:li:activity:123",
        url="https://linkedin.com/feed/update/urn:li:activity:123",
        author="Test Author",
        author_profile="https://linkedin.com/in/testauthor",
        content="Test content",
        post_type="text",
        saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        engagement={"likes": 50, "comments": 5},
        links=[],
        cluster_id=None,
    )
    d = post.to_dict()
    assert d["id"] == "urn:li:activity:123"
    assert d["engagement"] == '{"likes": 50, "comments": 5}'
    assert d["links"] == "[]"
    assert d["saved_at"] == "2026-01-01T00:00:00+00:00"


def test_post_from_dict():
    d = {
        "id": "urn:li:activity:456",
        "url": "https://linkedin.com/feed/update/urn:li:activity:456",
        "author": "Another Author",
        "author_profile": "https://linkedin.com/in/another",
        "content": "Another post",
        "post_type": "article",
        "saved_at": "2026-01-01T00:00:00+00:00",
        "engagement": '{"likes": 200, "comments": 20}',
        "links": '["https://example.com"]',
        "cluster_id": 3,
    }
    post = Post.from_dict(d)
    assert post.id == "urn:li:activity:456"
    assert post.engagement == {"likes": 200, "comments": 20}
    assert post.links == ["https://example.com"]
    assert post.cluster_id == 3


def test_cluster_creation():
    cluster = Cluster(
        id=1,
        keywords=["ai", "ml", "agents"],
        summary="AI & ML",
        post_count=12,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert cluster.id == 1
    assert cluster.summary == "AI & ML"
    assert cluster.post_count == 12


def test_cluster_to_dict():
    cluster = Cluster(
        id=1,
        keywords=["ai", "ml"],
        summary="AI & ML",
        post_count=5,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    d = cluster.to_dict()
    assert d["keywords"] == '["ai", "ml"]'
    assert d["summary"] == "AI & ML"
