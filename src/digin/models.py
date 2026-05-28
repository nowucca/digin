import json
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class Post:
    id: str
    url: str
    author: str
    author_profile: str
    content: str
    post_type: str
    saved_at: datetime
    engagement: dict
    links: list[str]
    cluster_id: int | None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "url": self.url,
            "author": self.author,
            "author_profile": self.author_profile,
            "content": self.content,
            "post_type": self.post_type,
            "saved_at": self.saved_at.isoformat(),
            "engagement": json.dumps(self.engagement),
            "links": json.dumps(self.links),
            "cluster_id": self.cluster_id,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Post":
        engagement = d["engagement"]
        if isinstance(engagement, str):
            engagement = json.loads(engagement)
        links = d["links"]
        if isinstance(links, str):
            links = json.loads(links)
        saved_at = d["saved_at"]
        if isinstance(saved_at, str):
            saved_at = datetime.fromisoformat(saved_at)
        cluster_id = d.get("cluster_id")
        if cluster_id is not None:
            cluster_id = int(cluster_id)
        return cls(
            id=d["id"],
            url=d["url"],
            author=d["author"],
            author_profile=d.get("author_profile", ""),
            content=d["content"],
            post_type=d.get("post_type", "text"),
            saved_at=saved_at,
            engagement=engagement,
            links=links,
            cluster_id=cluster_id,
        )


@dataclass
class Cluster:
    id: int
    keywords: list[str]
    summary: str
    post_count: int
    created_at: datetime

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "keywords": json.dumps(self.keywords),
            "summary": self.summary,
            "post_count": self.post_count,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Cluster":
        keywords = d["keywords"]
        if isinstance(keywords, str):
            keywords = json.loads(keywords)
        created_at = d["created_at"]
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        return cls(
            id=d["id"],
            keywords=keywords,
            summary=d["summary"],
            post_count=d["post_count"],
            created_at=created_at,
        )
