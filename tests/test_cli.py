from click.testing import CliRunner
from datetime import datetime, timezone

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
    assert "--method" in result.output


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
