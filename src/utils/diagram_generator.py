"""Generates visual diagrams from structured descriptions for PDF episodes."""

import os
import json
import base64
import io

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import seaborn as sns
import numpy as np


def generate_diagram(diagram_json, output_dir, episode_num, diagram_index):
    """Route to the appropriate generator based on diagram type and save as PNG."""
    os.makedirs(output_dir, exist_ok=True)
    save_path = os.path.join(output_dir, f"diagram_{episode_num}_{diagram_index}.png")

    diagram_type = diagram_json.get("type", "placeholder")
    description = diagram_json.get("description", "Diagram")
    components = diagram_json.get("components", None)

    if diagram_type in ("plot", "line_plot"):
        generate_line_plot(description, components, save_path)
    elif diagram_type == "bar_chart":
        generate_bar_chart(description, components, save_path)
    elif diagram_type == "matrix":
        generate_matrix_visualization(description, components, save_path)
    elif diagram_type in ("architecture", "flowchart"):
        generate_flowchart(description, components, save_path)
    else:
        generate_placeholder(description, save_path)

    return save_path


def generate_line_plot(description, components, save_path):
    """Create a line plot from components data or sample data."""
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))

    if components and "data" in components:
        for series in components["data"]:
            ax.plot(series.get("x", range(len(series["y"]))), series["y"],
                    label=series.get("label", ""), marker="o", linewidth=2)
    else:
        x = np.linspace(0, 10, 50)
        ax.plot(x, np.sin(x), label="Sample", marker="", linewidth=2)

    ax.set_title(description, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(components.get("xlabel", "X") if components else "X")
    ax.set_ylabel(components.get("ylabel", "Y") if components else "Y")
    if ax.get_legend_handles_labels()[1]:
        ax.legend()
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_bar_chart(description, components, save_path):
    """Create a bar chart from components data or sample data."""
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(8, 5))

    if components and "labels" in components and "values" in components:
        labels = components["labels"]
        values = components["values"]
    else:
        labels = ["A", "B", "C", "D", "E"]
        values = [23, 45, 12, 67, 34]

    colors = sns.color_palette("muted", len(labels))
    bars = ax.bar(labels, values, color=colors, edgecolor="white", linewidth=1.2)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(values) * 0.02,
                str(val), ha="center", va="bottom", fontsize=10, fontweight="bold")

    ax.set_title(description, fontsize=13, fontweight="bold", pad=12)
    ax.set_xlabel(components.get("xlabel", "") if components else "")
    ax.set_ylabel(components.get("ylabel", "Value") if components else "Value")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_matrix_visualization(description, components, save_path):
    """Visualize a matrix as an annotated heatmap."""
    fig, ax = plt.subplots(figsize=(7, 6))

    if components and "matrix" in components:
        data = np.array(components["matrix"])
    else:
        data = np.random.rand(4, 4).round(2)

    row_labels = components.get("row_labels") if components else None
    col_labels = components.get("col_labels") if components else None

    sns.heatmap(data, annot=True, fmt=".2f", cmap="YlOrRd", linewidths=0.5,
                ax=ax, xticklabels=col_labels or "auto", yticklabels=row_labels or "auto",
                cbar_kws={"shrink": 0.8})

    ax.set_title(description, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_flowchart(description, components, save_path):
    """Create a flowchart / architecture diagram with boxes and arrows."""
    if components and "nodes" in components:
        nodes = components["nodes"]
    else:
        nodes = ["Input", "Process", "Output"]

    n = len(nodes)
    vertical = n > 4
    fig_w = 6 if vertical else max(3 * n, 8)
    fig_h = max(2.5 * n, 6) if vertical else 5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    box_color = "#1e3a5f"
    fill_color = "white"
    box_w, box_h = 3.0, 1.0

    positions = []
    for i in range(n):
        if vertical:
            cx = 5.0
            cy = 9.0 - i * (8.0 / max(n - 1, 1))
        else:
            cx = 1.5 + i * (7.0 / max(n - 1, 1))
            cy = 5.0
        positions.append((cx, cy))

    for i, (cx, cy) in enumerate(positions):
        box = FancyBboxPatch(
            (cx - box_w / 2, cy - box_h / 2), box_w, box_h,
            boxstyle="round,pad=0.15",
            facecolor=fill_color, edgecolor=box_color, linewidth=2,
        )
        ax.add_patch(box)
        ax.text(cx, cy, nodes[i], ha="center", va="center",
                fontsize=11, fontweight="bold", color=box_color)

    for i in range(n - 1):
        x1, y1 = positions[i]
        x2, y2 = positions[i + 1]
        if vertical:
            start = (x1, y1 - box_h / 2)
            end = (x2, y2 + box_h / 2)
        else:
            start = (x1 + box_w / 2, y1)
            end = (x2 - box_w / 2, y2)
        ax.annotate("", xy=end, xytext=start,
                     arrowprops=dict(arrowstyle="-|>", color=box_color, lw=2))

    ax.set_title(description, fontsize=13, fontweight="bold", pad=12)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def generate_placeholder(description, save_path):
    """Create a placeholder image with the description text centered."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.set_facecolor("#f0f0f0")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")

    rect = mpatches.FancyBboxPatch(
        (0.3, 0.3), 9.4, 5.4,
        boxstyle="round,pad=0.1",
        facecolor="#f0f0f0", edgecolor="#999999", linewidth=2,
    )
    ax.add_patch(rect)
    ax.text(5, 3, description, ha="center", va="center",
            fontsize=12, color="#555555", wrap=True,
            fontweight="bold")

    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)


def diagram_to_base64(image_path):
    """Read a PNG file and return its base64-encoded string."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


if __name__ == "__main__":
    test_dir = "output/test_diagrams"

    diagrams = [
        {
            "type": "line_plot",
            "description": "Training Loss Over Epochs",
            "components": {
                "xlabel": "Epoch",
                "ylabel": "Loss",
                "data": [
                    {"y": [2.5, 1.8, 1.2, 0.8, 0.5, 0.35, 0.25], "label": "Train"},
                    {"y": [2.7, 2.0, 1.5, 1.1, 0.9, 0.7, 0.6], "label": "Validation"},
                ],
            },
        },
        {
            "type": "bar_chart",
            "description": "Model Performance Comparison",
            "components": {
                "labels": ["GPT-2", "BERT", "T5", "LLaMA", "Claude"],
                "values": [78, 82, 85, 89, 93],
                "ylabel": "Accuracy (%)",
            },
        },
        {
            "type": "matrix",
            "description": "Attention Weight Matrix",
            "components": {
                "matrix": [[0.9, 0.05, 0.03, 0.02],
                           [0.1, 0.7, 0.15, 0.05],
                           [0.05, 0.1, 0.8, 0.05],
                           [0.02, 0.08, 0.1, 0.8]],
                "row_labels": ["The", "cat", "sat", "down"],
                "col_labels": ["The", "cat", "sat", "down"],
            },
        },
        {
            "type": "flowchart",
            "description": "Transformer Architecture",
            "components": {
                "nodes": ["Input Embedding", "Multi-Head Attention", "Feed Forward", "Layer Norm", "Output"],
            },
        },
    ]

    paths = []
    for i, d in enumerate(diagrams):
        path = generate_diagram(d, test_dir, "test", i)
        paths.append(path)
        print(f"Generated: {path}")

    print(f"\nAll {len(paths)} diagrams saved to {test_dir}/")
