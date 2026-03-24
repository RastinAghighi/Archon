"""Renders Markdown content into a professional PDF using WeasyPrint and Jinja2."""

import os
import re
import json
from datetime import datetime

import jinja2

from src.utils.markdown_converter import convert_markdown_to_html
from src.utils.diagram_generator import generate_diagram, diagram_to_base64


def sanitize_filename(name):
    """Remove special characters and spaces, returning a clean filename fragment."""
    name = name.lower().replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    return name[:40]


def render_pdf(markdown_content, episode_num, topic_name, phase, category, output_dir="output/pdfs"):
    """Convert markdown content to a styled PDF.

    Returns the path to the generated PDF file.
    """
    # ── Extract and process DIAGRAM lines before markdown conversion ──
    diagram_map = {}  # placeholder text -> base64 img tag
    diagram_pattern = re.compile(r"(DIAGRAM:\s*(\{.*?\}))", re.DOTALL)

    for idx, match in enumerate(diagram_pattern.finditer(markdown_content)):
        full_match = match.group(1)
        json_str = match.group(2)
        try:
            diagram_json = json.loads(json_str)
        except json.JSONDecodeError:
            continue

        diagram_dir = os.path.join(output_dir, "diagrams")
        img_path = generate_diagram(diagram_json, diagram_dir, episode_num, idx)
        b64 = diagram_to_base64(img_path)
        img_tag = (
            f'<div class="diagram">'
            f'<img src="data:image/png;base64,{b64}" '
            f'style="max-width:100%;height:auto;" '
            f'alt="{diagram_json.get("description", "Diagram")}">'
            f'</div>'
        )
        diagram_map[full_match] = img_tag

    # Remove DIAGRAM lines from markdown and insert unique placeholders
    processed_md = markdown_content
    for idx, placeholder in enumerate(diagram_map):
        slot = f'<div id="diagram-slot-{idx}"></div>'
        processed_md = processed_md.replace(placeholder, slot)

    # ── Convert markdown to HTML ──
    content_html = convert_markdown_to_html(processed_md)

    # Replace diagram slot divs with actual embedded images
    for idx, (_placeholder, img_tag) in enumerate(diagram_map.items()):
        slot_tag = f'<div id="diagram-slot-{idx}"></div>'
        content_html = content_html.replace(slot_tag, img_tag)

    # ── Load Jinja2 template ──
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(project_root, "templates")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=False,
    )
    template = env.get_template("episode_template.html")

    rendered_html = template.render(
        episode_num=episode_num,
        topic_name=topic_name,
        date=datetime.now().strftime("%B %d, %Y"),
        content_html=content_html,
        phase=phase,
        category=category,
    )

    # ── Generate PDF with WeasyPrint ──
    os.makedirs(output_dir, exist_ok=True)
    safe_topic = sanitize_filename(topic_name)
    filename = f"episode_{episode_num:03d}_{safe_topic}.pdf"
    filepath = os.path.join(output_dir, filename)

    css_path = os.path.join(template_dir, "episode_style.css")

    try:
        from weasyprint import HTML, CSS

        html_doc = HTML(string=rendered_html, base_url=template_dir)
        stylesheets = [CSS(filename=css_path)] if os.path.exists(css_path) else []
        doc = html_doc.render(stylesheets=stylesheets)
        doc.write_pdf(filepath)

        pages = len(doc.pages)
        print(f"PDF generated: {filepath} ({pages} pages)")
    except OSError as e:
        if "cannot load library" in str(e).lower() or "gobject" in str(e).lower():
            print(
                "WeasyPrint requires GTK. Install it from: "
                "https://github.com/nicothin/weasyprint-on-windows"
            )
        raise

    return filepath


if __name__ == "__main__":
    # Try to find an existing episode markdown
    md_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "output", "markdown",
    )

    md_content = None
    if os.path.isdir(md_dir):
        md_files = [f for f in os.listdir(md_dir) if f.endswith(".md")]
        if md_files:
            with open(os.path.join(md_dir, md_files[0]), "r", encoding="utf-8") as f:
                md_content = f.read()

    if not md_content:
        md_content = """\
# Scalars, Vectors, and Vector Spaces

## Introduction

A **scalar** is simply a single number, in contrast to a **vector** which is an ordered list of numbers.

## Key Concepts

Vectors live in **vector spaces**, which obey specific axioms like closure under addition.

```python
import numpy as np

v = np.array([1, 2, 3])
w = np.array([4, 5, 6])
print("Sum:", v + w)
```

The dot product of two vectors is defined as:

$$
\\mathbf{v} \\cdot \\mathbf{w} = \\sum_{i=1}^{n} v_i w_i
$$

| Operation      | Symbol              | Result   |
|----------------|---------------------|----------|
| Addition       | $\\mathbf{v} + \\mathbf{w}$ | Vector   |
| Scalar Product | $c \\cdot \\mathbf{v}$       | Vector   |
| Dot Product    | $\\mathbf{v} \\cdot \\mathbf{w}$ | Scalar   |

DIAGRAM: {"type": "flowchart", "description": "Vector Space Axioms", "components": {"nodes": ["Closure", "Associativity", "Commutativity", "Identity", "Inverse"]}}
"""

    path = render_pdf(
        md_content,
        episode_num=1,
        topic_name="Scalars Vectors and Vector Spaces",
        phase=1,
        category="linear_algebra",
    )
    print(f"Output: {path}")
