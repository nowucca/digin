# How to Write Agentic Tools

Lessons from building DigIn — a CLI tool designed for both humans and AI agents.

Most CLI tools are built for humans. But AI coding agents are now the fastest-growing consumer of CLI tools. An agent-friendly tool isn't a different tool — it's a well-structured tool with a few deliberate choices that make it equally useful to both audiences.

This document explains the patterns DigIn uses and why.

## 1. Structured Output with `--json`

The single most important thing you can do for agents: give every command a machine-readable output mode.

```bash
# Human output
$ digin status
Config:    /home/user/.config/digin/config.yaml
Database:  /home/user/.local/share/digin/digin.db
Posts:     50
Clusters:  5

# Agent output
$ digin --json status
{
  "config_path": "/home/user/.config/digin/config.yaml",
  "db_path": "/home/user/.local/share/digin/digin.db",
  "post_count": 50,
  "cluster_count": 5,
  "clusters": [...]
}
```

**Implementation pattern:** Add `--json` as a global flag on the Click group. Each command checks it and branches between human-friendly and structured output.

```python
@click.group()
@click.option("--json", "json_output", is_flag=True, help="Output JSON.")
@click.pass_context
def cli(ctx, json_output):
    ctx.obj["json"] = json_output

@cli.command()
@click.pass_context
def status(ctx):
    use_json = ctx.obj.get("json", False)
    # ... gather data ...
    if use_json:
        click.echo(json.dumps(data, indent=2))
    else:
        click.echo(f"Posts: {data['post_count']}")
```

**Key decisions:**

- **Global flag, not per-command.** Agents set it once; humans never see it. Don't make agents learn which commands support JSON and which don't.
- **Errors are JSON too.** When `--json` is set and something fails, output `{"error": "...", "hint": "..."}` instead of plain text to stderr. The agent needs to parse the failure, not just detect a non-zero exit code.
- **Don't mix formats.** If `--json` is on, *everything* goes through JSON — no progress messages, no "Clustering 50 posts..." interleaved with the result. Use `--quiet` internally when JSON mode is active.

## 2. Schema Command for Tool Discovery

Agents need to know what your tool can do before they use it. A `schema` command outputs a machine-readable description of every command, option, type, and default.

```bash
$ digin schema
{
  "tool": "digin",
  "version": "0.1.0",
  "description": "LinkedIn saved posts research and clustering tool",
  "global_options": [
    {"name": "--json", "type": "flag", "description": "Output JSON (agent-friendly)"},
    ...
  ],
  "commands": [
    {
      "name": "cluster",
      "description": "Group saved posts into topic clusters.",
      "options": [
        {"name": "--num-clusters", "short": "-k", "type": "integer", "description": "Number of clusters"}
      ]
    },
    ...
  ],
  "workflow": [
    "digin sync --headless",
    "digin cluster",
    "digin --json show",
    "digin export -f json"
  ]
}
```

**Why not just use `--help`?** Help text is for humans — it has formatting, examples, descriptions that are great to read but painful to parse. Schema is for machines — structured data an agent can reason over.

**The `workflow` field** is the most valuable part for agents. It tells them the intended sequence of commands. An agent seeing `digin` for the first time can read the schema and immediately know: sync first, then cluster, then show/export.

**Implementation:** Walk Click's command tree and extract option metadata programmatically. Don't maintain the schema by hand — it drifts.

```python
@cli.command()
def schema():
    commands_schema = []
    for name, cmd in sorted(cli.commands.items()):
        if name == "schema":
            continue
        cmd_info = {
            "name": name,
            "description": cmd.help.split("\n")[0],
            "options": _extract_options(cmd),
        }
        commands_schema.append(cmd_info)
    click.echo(json.dumps({"tool": "digin", "commands": commands_schema}, indent=2))
```

## 3. Publishing as a Claude Code Plugin

If your tool has a CLI, you can also ship it as a Claude Code plugin. This means anyone cloning your repo gets an AI skill that knows how to use your tool.

**Plugin structure:**

```
your-repo/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── skills/
│   └── your-workflow/
│       └── SKILL.md         # Skill that guides agents through your tool
├── src/your_tool/
│   └── ...                  # Your actual tool
```

**plugin.json** — minimal manifest:

```json
{
  "name": "your-tool",
  "description": "What the tool does",
  "version": "0.1.0",
  "author": {"name": "Your Name"},
  "homepage": "https://github.com/you/your-tool",
  "license": "MIT"
}
```

**SKILL.md** — the skill teaches agents how to use your tool. This isn't a man page — it's a workflow guide with prerequisites, steps, troubleshooting, and iterative refinement patterns.

The SKILL.md frontmatter follows the [agentskills.io spec](https://agentskills.io/specification):

```markdown
---
name: your-workflow
description: Use when the user wants to [do the thing your tool does].
---

# Your Tool Workflow

## Prerequisites Check
[How to verify the tool is installed]

## Workflow Steps
[Step-by-step guide with example commands]

## Troubleshooting
[Common problems and solutions]
```

**The key insight:** a plugin skill is not documentation. It's instructions for an agent that has never seen your tool before. Write it the way you'd brief a smart colleague who just sat down at your desk.

You can also bundle a skill inside the Python package itself and provide an install command:

```bash
your-tool skill install    # Copy SKILL.md to ~/.claude/skills/
```

This way users who install your tool via pip (not git clone) still get the agent integration.

## 4. XDG Compliance

Agents run in automated environments. Hardcoded paths like `~/.myapp/` break in containers, CI, and multi-user setups. XDG Base Directory Specification solves this.

```python
import os
from pathlib import Path

def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
    return Path(base) / "your-tool"

def data_dir() -> Path:
    base = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(base) / "your-tool"

def cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    return Path(base) / "your-tool"
```

**Three directories, three purposes:**

| Type | XDG Variable | Default | What goes here |
|------|-------------|---------|----------------|
| Config | `$XDG_CONFIG_HOME` | `~/.config/` | Settings the user edits |
| Data | `$XDG_DATA_HOME` | `~/.local/share/` | Databases, state, things the tool creates |
| Cache | `$XDG_CACHE_HOME` | `~/.cache/` | Regenerable data, browser sessions, model cache |

**Why agents care:**

- An agent can set `XDG_DATA_HOME=/tmp/test-run` to isolate a test without touching the user's real data
- Container environments set XDG vars to writable locations
- `digin --json status` reports the resolved paths so agents know exactly where data lives
- Cleanup is trivial: `rm -rf $XDG_CACHE_HOME/your-tool`

## 5. Idempotent and Resumable Operations

Agents retry. Networks fail. Processes get interrupted. Your tool should handle re-runs gracefully.

```bash
# First run: syncs 50 posts
$ digin sync --headless
Synced 50 posts (50 new, 0 updated). Total: 50.

# Second run: skips what's already there
$ digin sync --headless
50 posts already in DB.
No new posts found.
```

**Implementation:** Pass known IDs to the scraper so it can skip them. Report new vs. updated counts so the agent knows what changed.

```python
storage = PostStorage(config.db_path)
known_ids = {p.id for p in storage.load_posts()}
posts = scrape(known_ids=known_ids)
new_count, updated_count = storage.save_posts(posts)
```

**With `--json`**, the agent gets structured counts:

```json
{"synced": 10, "new": 8, "updated": 2, "total": 58}
```

This lets the agent make decisions: "No new posts, skip re-clustering."

## 6. Exit Codes

Agents don't read your error messages — they check exit codes first, then parse output.

| Exit Code | Meaning | When |
|-----------|---------|------|
| 0 | Success | Normal completion |
| 1 | Error | Missing data, failed operation, bad input |

With `--json`, errors still exit 1 but the output is parseable:

```json
{"error": "not_enough_posts", "post_count": 3, "minimum": 6}
```

The agent can read `error` to decide what to do next (run `sync`, tell the user, retry later).

## Putting It Together

An agent encountering your tool for the first time should be able to:

1. **Discover:** `your-tool schema` → learn all commands and options
2. **Check state:** `your-tool --json status` → understand current data
3. **Execute:** `your-tool --json sync` → structured result
4. **Verify:** Check exit code + parse JSON output
5. **Iterate:** Re-run commands knowing they're idempotent

If your tool supports all five, it's agent-ready. The human experience doesn't suffer — `--json` and `schema` are invisible unless requested, and XDG paths just work.

The best part: these patterns make your tool better for humans too. Structured output enables piping to `jq`. Idempotent commands prevent accidents. XDG compliance means clean home directories. Agent-friendly and human-friendly aren't in tension — they're the same thing done well.
