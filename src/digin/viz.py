"""Visualization module — generates interactive HTML with treemap, scatter, and network views."""

import json
import tempfile
import webbrowser
from pathlib import Path

from digin.models import Cluster, Post


def generate_viz(
    clusters: list[Cluster],
    posts_by_cluster: dict[int, list[Post]],
    output_path: str | None = None,
    open_browser: bool = True,
) -> str:
    """Generate an interactive HTML visualization of clusters and posts."""
    treemap_data = _build_treemap_data(clusters, posts_by_cluster)
    scatter_data = _build_scatter_data(clusters, posts_by_cluster)
    network_data = _build_network_data(clusters, posts_by_cluster)

    html = _render_html(treemap_data, scatter_data, network_data)

    if output_path is None:
        output_path = str(Path(tempfile.mkdtemp()) / "digin_viz.html")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    if open_browser:
        webbrowser.open(f"file://{Path(output_path).resolve()}")

    return output_path


def _build_treemap_data(
    clusters: list[Cluster], posts_by_cluster: dict[int, list[Post]]
) -> dict:
    labels = ["All Posts"]
    parents = [""]
    values = [0]
    text = [""]
    cluster_ids = [0]

    for cluster in clusters:
        cluster_label = f"{cluster.summary} ({cluster.post_count})"
        labels.append(cluster_label)
        parents.append("All Posts")
        values.append(0)
        text.append(", ".join(cluster.keywords[:4]))
        cluster_ids.append(cluster.id)

        for post in posts_by_cluster.get(cluster.id, []):
            preview = post.content[:80].replace("\n", " ").strip()
            post_label = f"{post.author}: {preview}..."
            labels.append(post_label)
            parents.append(cluster_label)
            values.append(1)
            link_info = f"<br>Links: {', '.join(post.links[:2])}" if post.links else ""
            text.append(f"{post.url}{link_info}")
            cluster_ids.append(cluster.id)

    return {
        "labels": labels,
        "parents": parents,
        "values": values,
        "text": text,
        "cluster_ids": cluster_ids,
    }


def _build_scatter_data(
    clusters: list[Cluster], posts_by_cluster: dict[int, list[Post]]
) -> dict:
    all_posts = []
    all_cluster_ids = []
    all_cluster_names = []

    for cluster in clusters:
        for post in posts_by_cluster.get(cluster.id, []):
            all_posts.append(post)
            all_cluster_ids.append(cluster.id)
            all_cluster_names.append(cluster.summary)

    if len(all_posts) < 4:
        return {"x": [], "y": [], "text": [], "cluster_ids": [], "cluster_names": []}

    # Compute 2D projection using UMAP
    import os
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    from sentence_transformers import SentenceTransformer
    import umap

    model = SentenceTransformer("all-MiniLM-L6-v2")
    contents = [p.content for p in all_posts]
    embeddings = model.encode(contents, show_progress_bar=False)

    n_neighbors = min(15, len(all_posts) - 1)
    reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=n_neighbors)
    coords = reducer.fit_transform(embeddings)

    hover_text = []
    for post in all_posts:
        preview = post.content[:120].replace("\n", " ").strip()
        hover_text.append(f"<b>{post.author}</b><br>{preview}...")

    return {
        "x": coords[:, 0].tolist(),
        "y": coords[:, 1].tolist(),
        "text": hover_text,
        "cluster_ids": all_cluster_ids,
        "cluster_names": all_cluster_names,
    }


def _build_network_data(
    clusters: list[Cluster], posts_by_cluster: dict[int, list[Post]]
) -> dict:
    nodes = []
    edges = []

    # Central node
    nodes.append({
        "id": "root",
        "label": "Saved Posts",
        "size": 30,
        "type": "root",
    })

    for cluster in clusters:
        cluster_node_id = f"cluster_{cluster.id}"
        nodes.append({
            "id": cluster_node_id,
            "label": cluster.summary,
            "size": 20 + cluster.post_count,
            "type": "cluster",
            "keywords": cluster.keywords[:4],
        })
        edges.append({"from": "root", "to": cluster_node_id})

        for post in posts_by_cluster.get(cluster.id, []):
            post_node_id = f"post_{post.id}"
            preview = post.content[:60].replace("\n", " ").strip()
            nodes.append({
                "id": post_node_id,
                "label": post.author,
                "size": 8,
                "type": "post",
                "preview": preview,
                "url": post.url,
            })
            edges.append({"from": cluster_node_id, "to": post_node_id})

    return {"nodes": nodes, "edges": edges}


def _render_html(treemap_data: dict, scatter_data: dict, network_data: dict) -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>DigIn — Cluster Visualization</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f0f0f; color: #e0e0e0; }}
  .tabs {{ display: flex; gap: 0; border-bottom: 2px solid #333; padding: 0 20px; background: #1a1a1a; }}
  .tab {{ padding: 14px 28px; cursor: pointer; border: none; background: none; color: #888; font-size: 15px; font-weight: 500;
          border-bottom: 3px solid transparent; transition: all 0.2s; }}
  .tab:hover {{ color: #ccc; }}
  .tab.active {{ color: #fff; border-bottom-color: #4a9eff; }}
  .panel {{ display: none; height: calc(100vh - 52px); }}
  .panel.active {{ display: block; }}
  #network-panel {{ padding: 20px; overflow: auto; }}
  .network-container {{ display: flex; flex-wrap: wrap; gap: 24px; justify-content: center; padding: 20px; }}
  .cluster-group {{ background: #1e1e1e; border-radius: 12px; padding: 20px; min-width: 300px; max-width: 420px; flex: 1; }}
  .cluster-title {{ font-size: 18px; font-weight: 600; color: #4a9eff; margin-bottom: 4px; }}
  .cluster-keywords {{ font-size: 12px; color: #666; margin-bottom: 16px; }}
  .post-card {{ background: #262626; border-radius: 8px; padding: 12px; margin-bottom: 8px; transition: background 0.15s; cursor: pointer; }}
  .post-card:hover {{ background: #333; }}
  .post-author {{ font-weight: 600; font-size: 13px; color: #ccc; margin-bottom: 4px; }}
  .post-preview {{ font-size: 12px; color: #999; line-height: 1.4; }}
  .post-links {{ font-size: 11px; color: #4a9eff; margin-top: 6px; }}
  .post-links a {{ color: #4a9eff; text-decoration: none; }}
  .post-links a:hover {{ text-decoration: underline; }}
  h2 {{ text-align: center; margin: 20px 0 10px; color: #ccc; font-weight: 400; font-size: 14px; }}
</style>
</head>
<body>

<div class="tabs">
  <div class="tab active" onclick="showTab('treemap')">Treemap</div>
  <div class="tab" onclick="showTab('scatter')">Scatter</div>
  <div class="tab" onclick="showTab('network')">Network</div>
</div>

<div id="treemap-panel" class="panel active">
  <div id="treemap" style="width:100%;height:100%"></div>
</div>

<div id="scatter-panel" class="panel">
  <div id="scatter" style="width:100%;height:100%"></div>
</div>

<div id="network-panel" class="panel">
  <h2>Cluster Network</h2>
  <div class="network-container" id="network"></div>
</div>

<script>
function showTab(name) {{
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(name + '-panel').classList.add('active');
  if (name === 'treemap') Plotly.Plots.resize('treemap');
  if (name === 'scatter') Plotly.Plots.resize('scatter');
}}

// --- Treemap ---
const treemapData = {json.dumps(treemap_data)};
Plotly.newPlot('treemap', [{{
  type: 'treemap',
  labels: treemapData.labels,
  parents: treemapData.parents,
  values: treemapData.values,
  text: treemapData.text,
  hovertemplate: '<b>%{{label}}</b><br>%{{text}}<extra></extra>',
  textinfo: 'label',
  marker: {{ colorscale: 'Viridis', colors: treemapData.cluster_ids }},
  pathbar: {{ visible: true }},
  branchvalues: 'total',
}}], {{
  margin: {{ t: 10, l: 10, r: 10, b: 10 }},
  paper_bgcolor: '#0f0f0f',
  font: {{ color: '#e0e0e0' }},
}}, {{ responsive: true }});

// --- Scatter ---
const scatterData = {json.dumps(scatter_data)};
if (scatterData.x.length > 0) {{
  const clusterNames = [...new Set(scatterData.cluster_names)];
  const traces = clusterNames.map(name => {{
    const indices = scatterData.cluster_names.map((n, i) => n === name ? i : -1).filter(i => i >= 0);
    return {{
      x: indices.map(i => scatterData.x[i]),
      y: indices.map(i => scatterData.y[i]),
      text: indices.map(i => scatterData.text[i]),
      mode: 'markers',
      type: 'scatter',
      name: name,
      marker: {{ size: 10, opacity: 0.8 }},
      hovertemplate: '%{{text}}<extra>' + name + '</extra>',
    }};
  }});
  Plotly.newPlot('scatter', traces, {{
    margin: {{ t: 30, l: 40, r: 20, b: 40 }},
    paper_bgcolor: '#0f0f0f',
    plot_bgcolor: '#1a1a1a',
    font: {{ color: '#e0e0e0' }},
    xaxis: {{ showgrid: false, zeroline: false, showticklabels: false }},
    yaxis: {{ showgrid: false, zeroline: false, showticklabels: false }},
    legend: {{ bgcolor: 'rgba(0,0,0,0.5)', font: {{ size: 12 }} }},
  }}, {{ responsive: true }});
}}

// --- Network ---
const networkData = {json.dumps(network_data)};
const container = document.getElementById('network');
const clusterNodes = networkData.nodes.filter(n => n.type === 'cluster');
clusterNodes.forEach(cluster => {{
  const group = document.createElement('div');
  group.className = 'cluster-group';
  const kw = cluster.keywords ? cluster.keywords.join(', ') : '';
  group.innerHTML = '<div class="cluster-title">' + cluster.label + '</div>' +
    '<div class="cluster-keywords">' + kw + '</div>';
  const postEdges = networkData.edges.filter(e => e.from === cluster.id);
  const postNodes = postEdges.map(e => networkData.nodes.find(n => n.id === e.to)).filter(Boolean);
  postNodes.forEach(post => {{
    const card = document.createElement('div');
    card.className = 'post-card';
    if (post.url) card.onclick = () => window.open(post.url, '_blank');
    let linksHtml = '';
    card.innerHTML = '<div class="post-author">' + post.label + '</div>' +
      '<div class="post-preview">' + (post.preview || '') + '...</div>' + linksHtml;
    group.appendChild(card);
  }});
  container.appendChild(group);
}});
</script>
</body>
</html>"""
