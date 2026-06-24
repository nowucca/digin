"""Claude-powered clustering via Anthropic SDK."""

import json
import os
from datetime import datetime, timezone

import anthropic

from digin.models import Cluster, Post


def cluster_posts_with_llm(posts: list[Post]) -> tuple[list[int], list[Cluster]]:
    """Send posts to Claude and get back natural topic clusters.

    Returns (labels, clusters) where labels[i] is the 1-indexed cluster ID
    for posts[i], same interface as the local clustering function.
    """
    client = anthropic.Anthropic()

    # Build compact post list — id + author + preview
    post_lines = []
    for p in posts:
        preview = p.content[:150].replace("\n", " ").strip()
        post_lines.append(f"[{p.id}] {p.author}: {preview}")

    post_text = "\n".join(post_lines)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": f"""Analyze these {len(posts)} LinkedIn saved posts and group them into 8-15 natural topic clusters.

Here are the posts (format: [id] author: content preview):

{post_text}

For each cluster, provide:
1. A concise descriptive name (2-4 words, title case)
2. A one-sentence description
3. The list of post IDs belonging to it
4. 3-5 representative keywords

Output ONLY valid JSON — no markdown, no explanation:
[
  {{"name": "...", "description": "...", "keywords": ["..."], "post_ids": ["id1", "id2"]}}
]

Rules:
- Every post must be assigned to exactly one cluster
- Name clusters by TOPIC, not surface features
- Ignore URL fragments (https, lnkd.in) in content
- Group by meaning and intent, not keywords"""
        }],
    )

    # Extract JSON from response (may have thinking blocks)
    result_text = ""
    for block in response.content:
        if block.type == "text":
            result_text = block.text
            break

    # Parse the JSON
    # Handle potential markdown wrapping
    if "```" in result_text:
        start = result_text.find("[")
        end = result_text.rfind("]") + 1
        result_text = result_text[start:end]

    claude_clusters = json.loads(result_text)

    # Build post_id -> cluster_id mapping
    post_id_to_cluster = {}
    clusters = []
    now = datetime.now(timezone.utc)

    for i, cc in enumerate(claude_clusters):
        cluster_id = i + 1
        for pid in cc["post_ids"]:
            post_id_to_cluster[pid] = cluster_id

        clusters.append(Cluster(
            id=cluster_id,
            keywords=cc.get("keywords", []),
            summary=cc["name"],
            post_count=len(cc["post_ids"]),
            created_at=now,
        ))

    # Build labels array matching posts order
    labels = []
    # Track unassigned posts
    default_cluster = len(clusters) + 1
    unassigned = []
    for p in posts:
        if p.id in post_id_to_cluster:
            labels.append(post_id_to_cluster[p.id])
        else:
            labels.append(default_cluster)
            unassigned.append(p.id)

    # If any posts weren't assigned, add a catch-all cluster
    if unassigned:
        clusters.append(Cluster(
            id=default_cluster,
            keywords=["unassigned"],
            summary="Other",
            post_count=len(unassigned),
            created_at=now,
        ))

    return labels, clusters


def has_api_key() -> bool:
    """Check if ANTHROPIC_API_KEY is available."""
    return bool(os.environ.get("ANTHROPIC_API_KEY"))
