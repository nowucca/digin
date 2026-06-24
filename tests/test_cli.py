from click.testing import CliRunner
from datetime import datetime, timezone
from pathlib import Path

from digin.cli import cli
from digin.config import Config
from digin.models import Post
from digin.storage import PostStorage


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "LinkedIn Post Research" in result.output


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_sync_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--help"])
    assert result.exit_code == 0
    assert "--num" in result.output
    assert "--headless" in result.output


def test_cluster_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["cluster", "--help"])
    assert result.exit_code == 0
    assert "--num-clusters" in result.output
    assert "--local" in result.output


def test_cluster_no_posts(tmp_path):
    runner = CliRunner()
    db_path = str(tmp_path / "test.db")
    result = runner.invoke(cli, ["cluster"], obj={
        "config": Config(db_path=db_path),
        "verbose": False,
        "quiet": False,
    })
    assert result.exit_code != 0
    assert "Need at least" in result.output or "No posts" in result.output


def test_show_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["show", "--help"])
    assert result.exit_code == 0
    assert "--cluster" in result.output
    assert "--format" in result.output


def test_export_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["export", "--help"])
    assert result.exit_code == 0
    assert "--format" in result.output
    assert "--output" in result.output


def test_status_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["status", "--help"])
    assert result.exit_code == 0


def test_status_empty(tmp_path):
    runner = CliRunner()
    db_path = str(tmp_path / "test.db")
    result = runner.invoke(cli, ["status"], obj={
        "config": Config(db_path=db_path),
        "verbose": False,
        "quiet": False,
    })
    assert result.exit_code == 0
    assert "Posts:     0" in result.output


def test_full_pipeline_cluster_show_export(tmp_path):
    """Test cluster -> show -> export with pre-loaded synthetic data."""
    db_path = str(tmp_path / "test.db")
    storage = PostStorage(db_path)

    posts = []
    for i in range(6):
        posts.append(Post(
            id=f"urn:li:activity:ai{i}",
            url=f"https://linkedin.com/feed/update/urn:li:activity:ai{i}",
            author=f"AI Author {i}",
            author_profile=f"https://linkedin.com/in/ai{i}",
            content=f"Deep learning neural networks artificial intelligence transformers large language models post {i}",
            post_type="text",
            saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            engagement={"likes": 100 + i, "comments": 10 + i},
            links=[],
            cluster_id=None,
        ))
        posts.append(Post(
            id=f"urn:li:activity:lead{i}",
            url=f"https://linkedin.com/feed/update/urn:li:activity:lead{i}",
            author=f"Leadership Author {i}",
            author_profile=f"https://linkedin.com/in/lead{i}",
            content=f"Leadership management team culture hiring organizational development growth post {i}",
            post_type="text",
            saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            engagement={"likes": 50 + i, "comments": 5 + i},
            links=[],
            cluster_id=None,
        ))

    storage.save_posts(posts)
    storage.close()

    config = Config(db_path=db_path)
    runner = CliRunner()

    # Test cluster
    result = runner.invoke(cli, ["cluster", "-k", "2"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Cluster" in result.output

    # Test show summary
    result = runner.invoke(cli, ["show"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Cluster" in result.output

    # Test show cluster detail
    result = runner.invoke(cli, ["show", "--cluster", "1"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0

    # Test export JSON
    result = runner.invoke(cli, ["export", "-f", "json"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert len(data) == 2

    # Test export CSV
    result = runner.invoke(cli, ["export", "-f", "csv"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "cluster_id" in result.output

    # Test export Markdown
    result = runner.invoke(cli, ["export", "-f", "md"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "# DigIn Export" in result.output


def _make_posts_for_db(db_path, include_links=False, include_engagement=True):
    """Helper: create storage with posts and clusters pre-populated."""
    from digin.models import Cluster
    storage = PostStorage(db_path)
    posts = []
    for i in range(2):
        posts.append(Post(
            id=f"urn:li:activity:p{i}",
            url=f"https://linkedin.com/feed/update/urn:li:activity:p{i}",
            author=f"Author {i}",
            author_profile=f"https://linkedin.com/in/author{i}",
            content=f"Content for post {i}",
            post_type="text",
            saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            engagement={"likes": 10 if include_engagement else 0, "comments": 2 if include_engagement else 0},
            links=[f"https://link{i}.com"] if include_links else [],
            cluster_id=1,
        ))
    storage.save_posts(posts)
    clusters = [Cluster(
        id=1,
        keywords=["test", "keyword", "example"],
        summary="Test Cluster",
        post_count=2,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )]
    storage.save_clusters(clusters)
    storage.update_post_clusters({p.id: 1 for p in posts})
    storage.close()
    return Config(db_path=db_path)


def test_echo_with_ctx_object(tmp_path):
    """Test _echo with a Click context object (not just bool)."""
    from digin.cli import _echo
    import click

    # Create a context with obj dict
    @click.command()
    @click.pass_context
    def dummy(ctx):
        ctx.ensure_object(dict)
        ctx.obj["quiet"] = False
        _echo(ctx, "hello from ctx")

    runner = CliRunner()
    result = runner.invoke(dummy)
    assert "hello from ctx" in result.output


def test_echo_with_ctx_quiet(tmp_path):
    """Test _echo with a Click context object in quiet mode."""
    from digin.cli import _echo
    import click

    @click.command()
    @click.pass_context
    def dummy(ctx):
        ctx.ensure_object(dict)
        ctx.obj["quiet"] = True
        _echo(ctx, "should not appear")

    runner = CliRunner()
    result = runner.invoke(dummy)
    assert "should not appear" not in result.output


def test_show_no_clusters(tmp_path):
    """Test show command when there are no clusters."""
    runner = CliRunner()
    db_path = str(tmp_path / "empty.db")
    result = runner.invoke(cli, ["show"], obj={
        "config": Config(db_path=db_path),
        "verbose": False,
        "quiet": False,
    })
    assert result.exit_code == 0
    assert "No clusters found" in result.output


def test_show_invalid_cluster_id(tmp_path):
    """Test show with a cluster ID that doesn't exist."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["show", "--cluster", "999"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "not found" in result.output


def test_show_summary_as_json(tmp_path):
    """Test show summary in JSON format."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["show", "-f", "json"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert len(data) >= 1
    assert "summary" in data[0]


def test_show_detail_as_json(tmp_path):
    """Test show detail in JSON format."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["show", "--cluster", "1", "-f", "json"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert "cluster" in data
    assert "posts" in data


def test_show_detail_with_links(tmp_path):
    """Test show detail displays links."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"), include_links=True)
    result = runner.invoke(cli, ["show", "--cluster", "1"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Links:" in result.output


def test_show_detail_with_engagement(tmp_path):
    """Test show detail displays likes/comments."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"), include_engagement=True)
    result = runner.invoke(cli, ["show", "--cluster", "1"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Likes:" in result.output


def test_export_no_clusters(tmp_path):
    """Test export when there are no clusters."""
    runner = CliRunner()
    db_path = str(tmp_path / "empty.db")
    result = runner.invoke(cli, ["export", "-f", "json"], obj={
        "config": Config(db_path=db_path),
        "verbose": False,
        "quiet": False,
    })
    assert result.exit_code != 0
    assert "No clusters found" in result.output


def test_export_invalid_cluster_id(tmp_path):
    """Test export with a cluster ID that doesn't exist."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["export", "-f", "json", "--cluster", "999"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code != 0
    assert "not found" in result.output


def test_export_to_file(tmp_path):
    """Test export --output flag writes to a file."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    output_file = str(tmp_path / "output.json")
    result = runner.invoke(cli, ["export", "-f", "json", "-o", output_file], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Exported to" in result.output
    from pathlib import Path
    assert Path(output_file).exists()
    import json
    data = json.loads(Path(output_file).read_text())
    assert len(data) >= 1


def test_export_to_file_quiet(tmp_path):
    """Test export --output in quiet mode (no 'Exported to' message)."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    output_file = str(tmp_path / "output.json")
    # Use --quiet CLI flag so ctx.obj["quiet"] is True
    result = runner.invoke(cli, ["--quiet", "export", "-f", "json", "-o", output_file], obj={
        "config": config,
    })
    assert result.exit_code == 0
    assert "Exported to" not in result.output


def test_export_markdown_with_links(tmp_path):
    """Test export markdown format with posts that have links."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"), include_links=True, include_engagement=True)
    result = runner.invoke(cli, ["export", "-f", "md"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "# DigIn Export" in result.output
    assert "External:" in result.output
    assert "Likes:" in result.output


def test_export_specific_cluster(tmp_path):
    """Test export with a specific cluster ID."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["export", "-f", "json", "--cluster", "1"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert len(data) == 1
    assert data[0]["id"] == 1


def test_status_with_clusters(tmp_path):
    """Test status command when clusters are present."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))
    result = runner.invoke(cli, ["status"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Clusters:  1" in result.output
    # The cluster table should be printed
    assert "Test Cluster" in result.output


def test_print_cluster_table_quiet():
    """Test _print_cluster_table does nothing in quiet mode."""
    from digin.cli import _print_cluster_table
    from digin.models import Cluster

    clusters = [Cluster(
        id=1, keywords=["a", "b"], summary="Test",
        post_count=5, created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )]
    # Should not raise and produce no output (we can verify by checking no exception)
    _print_cluster_table(clusters, quiet=True)


def test_cluster_quiet_flag(tmp_path):
    """Test cluster command with quiet flag suppresses output."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"))

    # Add more posts to the DB so we have enough to cluster
    from digin.models import Cluster
    storage = PostStorage(config.db_path)
    extra_posts = []
    for i in range(10, 20):
        extra_posts.append(Post(
            id=f"urn:li:activity:extra{i}",
            url=f"https://linkedin.com/feed/update/urn:li:activity:extra{i}",
            author=f"Author {i}",
            author_profile=f"https://linkedin.com/in/author{i}",
            content=f"Machine learning artificial intelligence neural networks deep learning post {i}",
            post_type="text",
            saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            engagement={"likes": i, "comments": i},
            links=[],
            cluster_id=None,
        ))
    storage.save_posts(extra_posts)
    storage.close()

    result = runner.invoke(cli, ["--quiet", "cluster", "-k", "2"], obj={
        "config": config,
    })
    assert result.exit_code == 0
    # With --quiet, no table should be printed
    assert "#" not in result.output


def test_cluster_labels_none(tmp_path, monkeypatch):
    """Test cluster command when clustering returns None (too few posts)."""
    runner = CliRunner()
    db_path = str(tmp_path / "test.db")
    storage = PostStorage(db_path)
    posts = []
    for i in range(6):
        posts.append(Post(
            id=f"urn:li:activity:p{i}",
            url=f"https://linkedin.com/feed/update/urn:li:activity:p{i}",
            author=f"Author {i}",
            author_profile=f"",
            content=f"Content {i}",
            post_type="text",
            saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            engagement={},
            links=[],
            cluster_id=None,
        ))
    storage.save_posts(posts)
    storage.close()

    # Monkeypatch cluster_posts to return None, None
    import digin.cli as cli_module
    monkeypatch.setattr(cli_module, "_print_cluster_table", lambda c, q: None)

    import digin.clustering as clustering_module
    original_cluster_posts = clustering_module.cluster_posts

    def mock_cluster_posts(*args, **kwargs):
        return None, None

    monkeypatch.setattr(clustering_module, "cluster_posts", mock_cluster_posts)

    result = runner.invoke(cli, ["cluster"], obj={
        "config": Config(db_path=db_path), "verbose": False, "quiet": False,
    })
    assert result.exit_code != 0
    assert "Clustering failed" in result.output


def test_show_detail_no_engagement(tmp_path):
    """Test show detail with posts that have 0 likes and 0 comments (branch not taken)."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"), include_engagement=False)
    result = runner.invoke(cli, ["show", "--cluster", "1"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Likes:" not in result.output


def test_export_markdown_no_links_no_engagement(tmp_path):
    """Test export markdown with posts that have no links and no engagement."""
    runner = CliRunner()
    config = _make_posts_for_db(str(tmp_path / "test.db"), include_links=False, include_engagement=False)
    result = runner.invoke(cli, ["export", "-f", "md"], obj={
        "config": config, "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "# DigIn Export" in result.output
    assert "External:" not in result.output
    assert "Likes:" not in result.output


def test_skill_install_missing_skill_src(monkeypatch, tmp_path):
    """Test skill install when the bundled SKILL.md doesn't exist."""
    from pathlib import Path as PathType
    monkeypatch.setattr(PathType, "home", lambda: tmp_path)
    # Monkeypatch Path.__truediv__ indirectly by monkeypatching the exists check
    # We'll patch the skill_src.exists to return False
    runner = CliRunner()
    # Create a non-existent directory for __file__ parent
    import digin.cli as cli_module
    original_file = cli_module.__file__
    # Temporarily change __file__ to a path where skills dir doesn't exist
    monkeypatch.setattr(cli_module, "__file__", str(tmp_path / "fake_cli.py"))
    result = runner.invoke(cli, ["skill", "install"])
    assert result.exit_code != 0
    assert "not found" in result.output


def test_sync_with_known_posts(tmp_path, monkeypatch):
    """Test sync command with known posts in DB and scraper mocked."""
    from datetime import datetime, timezone
    from digin.models import Post
    from digin.storage import PostStorage

    db_path = str(tmp_path / "test.db")
    storage = PostStorage(db_path)
    post = Post(
        id="urn:li:activity:existing1",
        url="https://linkedin.com/feed/update/urn:li:activity:existing1",
        author="Author",
        author_profile="",
        content="Existing content",
        post_type="text",
        saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        engagement={},
        links=[],
        cluster_id=None,
    )
    storage.save_posts([post])
    storage.close()

    # Mock scrape_saved_posts to return empty list (no new posts)
    async def mock_scrape(config, max_posts=None, known_ids=None):
        return []

    import digin.scraper as scraper_module
    monkeypatch.setattr(scraper_module, "scrape_saved_posts", mock_scrape)

    runner = CliRunner()
    result = runner.invoke(cli, ["sync"], obj={
        "config": Config(db_path=db_path), "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "already in DB" in result.output
    assert "No new posts found" in result.output


def test_sync_with_new_posts(tmp_path, monkeypatch):
    """Test sync command when scraper returns new posts."""
    from datetime import datetime, timezone
    from digin.storage import PostStorage

    db_path = str(tmp_path / "test.db")

    new_post = Post(
        id="urn:li:activity:new1",
        url="https://linkedin.com/feed/update/urn:li:activity:new1",
        author="New Author",
        author_profile="",
        content="New content",
        post_type="text",
        saved_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        engagement={},
        links=[],
        cluster_id=None,
    )

    async def mock_scrape(config, max_posts=None, known_ids=None):
        return [new_post]

    import digin.scraper as scraper_module
    monkeypatch.setattr(scraper_module, "scrape_saved_posts", mock_scrape)

    runner = CliRunner()
    result = runner.invoke(cli, ["sync", "--headless"], obj={
        "config": Config(db_path=db_path), "verbose": False, "quiet": False,
    })
    assert result.exit_code == 0
    assert "Synced 1 posts" in result.output


def test_sync_error(tmp_path, monkeypatch):
    """Test sync command when scraper raises an exception."""
    db_path = str(tmp_path / "test.db")

    async def mock_scrape(config, max_posts=None, known_ids=None):
        raise RuntimeError("Browser failed")

    import digin.scraper as scraper_module
    monkeypatch.setattr(scraper_module, "scrape_saved_posts", mock_scrape)

    runner = CliRunner()
    result = runner.invoke(cli, ["sync"], obj={
        "config": Config(db_path=db_path), "verbose": False, "quiet": False,
    })
    assert result.exit_code != 0
    assert "Error" in result.output


def test_skill_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["skill", "--help"])
    assert result.exit_code == 0
    assert "install" in result.output
    assert "list" in result.output


def test_skill_list_not_installed(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["skill", "list"])
    assert result.exit_code == 0
    assert "not installed" in result.output


def test_skill_install_and_list(monkeypatch, tmp_path):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    runner = CliRunner()

    result = runner.invoke(cli, ["skill", "install"])
    assert result.exit_code == 0
    assert "Installed" in result.output

    # Verify file exists
    skill_file = tmp_path / ".claude" / "skills" / "digin" / "SKILL.md"
    assert skill_file.exists()
    content = skill_file.read_text()
    assert "name: digin" in content

    # List should show installed
    result = runner.invoke(cli, ["skill", "list"])
    assert "installed" in result.output
