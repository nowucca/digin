import asyncio
import csv
import io
import json as json_module
import sys

import click

from digin import __version__
from digin.config import Config, load_config
from digin.storage import PostStorage


@click.group()
@click.option("--config", "-c", "config_path", default=None, help="Path to config file")
@click.option("--verbose", "-v", is_flag=True, help="Increase output verbosity")
@click.option("--quiet", "-q", is_flag=True, help="Suppress non-error output")
@click.version_option(__version__)
@click.pass_context
def cli(ctx, config_path, verbose, quiet):
    """DigIn — LinkedIn Post Research & Clustering Tool"""
    ctx.ensure_object(dict)
    if "config" not in ctx.obj:
        ctx.obj["config"] = load_config(config_path)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@cli.command()
@click.option("--num", "-n", type=int, default=None, help="Number of posts to fetch")
@click.option("--headless", is_flag=True, default=None, help="Run browser without visible window")
@click.pass_context
def sync(ctx, num, headless):
    """Fetch your latest saved posts from LinkedIn.

    Examples:
      digin sync                    Sync all saved posts
      digin sync --num 50           Sync only 50 most recent
      digin sync --headless         Run browser in background
    """
    config: Config = ctx.obj["config"]
    if headless is not None:
        config.headless = headless

    # Load existing post IDs so we can skip them during scraping
    storage = PostStorage(config.db_path)
    existing_posts = storage.load_posts()
    known_ids = {p.id for p in existing_posts}
    existing_count = len(known_ids)
    if existing_count:
        click.echo(f"Found {existing_count} existing posts in DB, will skip duplicates.")

    from digin.scraper import scrape_saved_posts

    try:
        posts = asyncio.run(scrape_saved_posts(config, max_posts=num, known_ids=known_ids))
    except Exception as e:
        click.echo(f"Error during scraping: {e}", err=True)
        click.echo("Make sure Playwright is installed: uv run playwright install chromium", err=True)
        storage.close()
        sys.exit(1)

    if not posts:
        click.echo("No new posts found.")
        storage.close()
        return

    new_count, updated_count = storage.save_posts(posts)
    storage.close()

    click.echo(f"Synced {len(posts)} posts ({new_count} new, {updated_count} updated)")


@cli.command()
@click.option("--method", type=click.Choice(["kmeans"]), default=None, help="Clustering algorithm")
@click.option("--num-clusters", "-k", type=int, default=None, help="Number of clusters (auto if omitted)")
@click.option("--min-size", type=int, default=None, help="Minimum cluster size")
@click.pass_context
def cluster(ctx, method, num_clusters, min_size):
    """Group saved posts into topic clusters.

    Examples:
      digin cluster                     Auto-detect cluster count
      digin cluster -k 5                Force 5 clusters
      digin cluster --min-size 5        Minimum 5 posts per cluster
    """
    config: Config = ctx.obj["config"]
    storage = PostStorage(config.db_path)
    posts = storage.load_posts()

    if len(posts) < 6:
        click.echo(f"Need at least 6 posts to cluster (have {len(posts)}). Run 'digin sync' first.")
        storage.close()
        return

    from digin.clustering import cluster_posts

    click.echo(f"Clustering {len(posts)} posts...")
    labels, clusters = cluster_posts(posts, num_clusters=num_clusters, model_name=config.embedding_model)

    if labels is None or clusters is None:
        click.echo("Clustering failed — not enough data.")
        storage.close()
        return

    storage.clear_clusters()
    post_cluster_map = {posts[i].id: labels[i] for i in range(len(posts))}
    storage.update_post_clusters(post_cluster_map)
    storage.save_clusters(clusters)
    storage.close()

    click.echo(f"\nFound {len(clusters)} clusters:\n")
    click.echo(f"  {'#':>3}  {'Cluster':<20}  {'Posts':>5}  Keywords")
    click.echo(f"  {'---':>3}  {'--------------------':<20}  {'-----':>5}  --------")
    for c in clusters:
        kw = ", ".join(c.keywords[:3])
        click.echo(f"  {c.id:>3}  {c.summary:<20}  {c.post_count:>5}  {kw}")


@cli.command()
@click.option("--cluster", "-c", "cluster_id", type=int, default=None, help="Show specific cluster")
@click.option("--format", "-f", "fmt", type=click.Choice(["table", "json"]), default=None, help="Output format")
@click.pass_context
def show(ctx, cluster_id, fmt):
    """Display saved posts or clustering results.

    Examples:
      digin show                    Show cluster summary table
      digin show --cluster 1        Show posts in cluster 1
      digin show --format json      Output as JSON
    """
    config: Config = ctx.obj["config"]
    fmt = fmt or config.default_format
    storage = PostStorage(config.db_path)

    if cluster_id is not None:
        _show_cluster_detail(storage, cluster_id, fmt)
    else:
        _show_cluster_summary(storage, fmt)

    storage.close()


def _show_cluster_summary(storage: PostStorage, fmt: str):
    clusters = storage.load_clusters()
    if not clusters:
        click.echo("No clusters found. Run 'digin cluster' first.")
        return

    if fmt == "json":
        data = [{"id": c.id, "summary": c.summary, "post_count": c.post_count,
                 "keywords": c.keywords} for c in clusters]
        click.echo(json_module.dumps(data, indent=2))
        return

    click.echo(f"\n  {'#':>3}  {'Cluster':<20}  {'Posts':>5}  Keywords")
    click.echo(f"  {'---':>3}  {'--------------------':<20}  {'-----':>5}  --------")
    for c in clusters:
        kw = ", ".join(c.keywords[:3])
        click.echo(f"  {c.id:>3}  {c.summary:<20}  {c.post_count:>5}  {kw}")
    click.echo()


def _show_cluster_detail(storage: PostStorage, cluster_id: int, fmt: str):
    clusters = storage.load_clusters()
    cluster = next((c for c in clusters if c.id == cluster_id), None)
    if cluster is None:
        click.echo(f"Cluster {cluster_id} not found.")
        return

    posts = storage.load_posts(cluster_id=cluster_id)

    if fmt == "json":
        data = {
            "cluster": {"id": cluster.id, "summary": cluster.summary, "keywords": cluster.keywords},
            "posts": [{"author": p.author, "content": p.content[:200], "url": p.url,
                       "engagement": p.engagement} for p in posts],
        }
        click.echo(json_module.dumps(data, indent=2))
        return

    kw = ", ".join(cluster.keywords)
    click.echo(f"\n  Cluster: {cluster.summary} ({cluster.post_count} posts)")
    click.echo(f"  Keywords: {kw}\n")

    for i, post in enumerate(posts, 1):
        preview = post.content[:80].replace("\n", " ")
        click.echo(f'  {i}. {post.author} — "{preview}..."')
        click.echo(f"     {post.url}")
        likes = post.engagement.get("likes", 0)
        comments = post.engagement.get("comments", 0)
        click.echo(f"     Likes: {likes:,}  Comments: {comments:,}")
        click.echo()


@cli.command()
@click.option("--format", "-f", "fmt", type=click.Choice(["csv", "json", "md"]), required=True, help="Export format")
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file (default: stdout)")
@click.option("--cluster", "-c", "cluster_id", type=int, default=None, help="Export specific cluster only")
@click.pass_context
def export(ctx, fmt, output, cluster_id):
    """Export posts and clusters to file.

    Examples:
      digin export -f csv -o posts.csv      Export all to CSV
      digin export -f json                   Export all as JSON to stdout
      digin export -f md -c 1               Export cluster 1 as Markdown
    """
    config: Config = ctx.obj["config"]
    storage = PostStorage(config.db_path)
    clusters = storage.load_clusters()

    if not clusters:
        click.echo("No clusters found. Run 'digin cluster' first.")
        storage.close()
        return

    if cluster_id is not None:
        clusters = [c for c in clusters if c.id == cluster_id]
        if not clusters:
            click.echo(f"Cluster {cluster_id} not found.")
            storage.close()
            return

    if fmt == "csv":
        content = _export_csv(storage, clusters)
    elif fmt == "json":
        content = _export_json(storage, clusters)
    elif fmt == "md":
        content = _export_markdown(storage, clusters)

    storage.close()

    if output:
        with open(output, "w") as f:
            f.write(content)
        click.echo(f"Exported to {output}")
    else:
        click.echo(content)


def _export_csv(storage: PostStorage, clusters: list) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["cluster_id", "cluster_keywords", "post_id", "author",
                     "content", "post_type", "engagement_likes",
                     "engagement_comments", "url"])
    for cluster in clusters:
        posts = storage.load_posts(cluster_id=cluster.id)
        kw = ", ".join(cluster.keywords)
        for post in posts:
            writer.writerow([
                cluster.id, kw, post.id, post.author,
                post.content, post.post_type,
                post.engagement.get("likes", 0),
                post.engagement.get("comments", 0),
                post.url,
            ])
    return buf.getvalue()


def _export_json(storage: PostStorage, clusters: list) -> str:
    data = []
    for cluster in clusters:
        posts = storage.load_posts(cluster_id=cluster.id)
        data.append({
            "id": cluster.id,
            "summary": cluster.summary,
            "keywords": cluster.keywords,
            "post_count": cluster.post_count,
            "posts": [{
                "id": p.id, "author": p.author, "content": p.content,
                "url": p.url, "post_type": p.post_type,
                "engagement": p.engagement, "links": p.links,
            } for p in posts],
        })
    return json_module.dumps(data, indent=2)


def _export_markdown(storage: PostStorage, clusters: list) -> str:
    lines = ["# DigIn Export\n"]
    for cluster in clusters:
        posts = storage.load_posts(cluster_id=cluster.id)
        kw = ", ".join(cluster.keywords)
        lines.append(f"## {cluster.summary} ({cluster.post_count} posts)")
        lines.append(f"**Keywords:** {kw}\n")
        for post in posts:
            preview = post.content[:150].replace("\n", " ")
            likes = post.engagement.get("likes", 0)
            comments = post.engagement.get("comments", 0)
            lines.append(f"- **{post.author}**: {preview}")
            lines.append(f"  - {post.url}")
            lines.append(f"  - Likes: {likes:,} | Comments: {comments:,}")
        lines.append("")
    return "\n".join(lines)
