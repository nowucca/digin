import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from digin.models import Cluster, Post
from digin.paths import db_path as default_db_path


class PostStorage:
    def __init__(self, db_path: str | None = None):
        if db_path is None:
            db_path = str(default_db_path())
        if db_path == ":memory:":
            self.db_path = db_path
        else:
            self.db_path = str(Path(db_path).expanduser())
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS posts (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                author TEXT NOT NULL,
                author_profile TEXT DEFAULT '',
                content TEXT NOT NULL,
                post_type TEXT DEFAULT 'text',
                saved_at TEXT NOT NULL,
                engagement TEXT DEFAULT '{}',
                links TEXT DEFAULT '[]',
                cluster_id INTEGER,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS clusters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keywords TEXT NOT NULL,
                summary TEXT NOT NULL,
                post_count INTEGER NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            );
        """)

    def save_posts(self, posts: list[Post]) -> tuple[int, int]:
        new_count = 0
        updated_count = 0
        for post in posts:
            d = post.to_dict()
            existing = self.conn.execute("SELECT id FROM posts WHERE id = ?", (d["id"],)).fetchone()
            if existing:
                self.conn.execute(
                    "UPDATE posts SET content=?, engagement=?, links=?, updated_at=datetime('now') WHERE id=?",
                    (d["content"], d["engagement"], d["links"], d["id"]))
                updated_count += 1
            else:
                self.conn.execute(
                    "INSERT INTO posts (id, url, author, author_profile, content, post_type, saved_at, engagement, links, cluster_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (d["id"], d["url"], d["author"], d["author_profile"], d["content"], d["post_type"], d["saved_at"], d["engagement"], d["links"], d["cluster_id"]))
                new_count += 1
        self.conn.commit()
        return new_count, updated_count

    def load_posts(self, cluster_id: int | None = None) -> list[Post]:
        if cluster_id is not None:
            rows = self.conn.execute("SELECT * FROM posts WHERE cluster_id = ? ORDER BY saved_at DESC", (cluster_id,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM posts ORDER BY saved_at DESC").fetchall()
        return [Post.from_dict(dict(row)) for row in rows]

    def post_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) as cnt FROM posts").fetchone()
        return row["cnt"]

    def save_clusters(self, clusters: list[Cluster]):
        for cluster in clusters:
            d = cluster.to_dict()
            self.conn.execute("INSERT OR REPLACE INTO clusters (id, keywords, summary, post_count, created_at) VALUES (?, ?, ?, ?, ?)",
                (d["id"], d["keywords"], d["summary"], d["post_count"], d["created_at"]))
        self.conn.commit()

    def load_clusters(self) -> list[Cluster]:
        rows = self.conn.execute("SELECT * FROM clusters ORDER BY id").fetchall()
        return [Cluster.from_dict(dict(row)) for row in rows]

    def update_post_clusters(self, post_cluster_map: dict[str, int]):
        for post_id, cluster_id in post_cluster_map.items():
            self.conn.execute("UPDATE posts SET cluster_id = ? WHERE id = ?", (cluster_id, post_id))
        self.conn.commit()

    def clear_clusters(self):
        self.conn.execute("DELETE FROM clusters")
        self.conn.execute("UPDATE posts SET cluster_id = NULL")
        self.conn.commit()

    def close(self):
        self.conn.close()
