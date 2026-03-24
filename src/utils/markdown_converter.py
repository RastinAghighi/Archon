"""Converts Markdown output from the document writer into HTML suitable for PDF rendering."""

import re
import base64
import io
import markdown

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _simplify_bmatrix(latex_expr):
    """Convert \\begin{bmatrix}...\\end{bmatrix} to matplotlib-compatible notation."""
    expr = latex_expr
    # Replace bmatrix environments with bracket notation
    def _bmatrix_to_brackets(m):
        inner = m.group(1).strip()
        # Split rows by \\ and cells by &
        rows = [r.strip() for r in re.split(r'\\\\', inner) if r.strip()]
        if len(rows) == 1:
            # Single row — render as [a, b, c]
            cells = [c.strip() for c in rows[0].split('&')]
            return r'\left[' + r',\;'.join(cells) + r'\right]'
        else:
            # Multi-row — render as column vector [a; b; c]
            formatted = []
            for row in rows:
                cells = [c.strip() for c in row.split('&')]
                formatted.append(r',\;'.join(cells))
            return r'\left[' + r';\;'.join(formatted) + r'\right]'

    for env in ('bmatrix', 'pmatrix', 'vmatrix', 'matrix'):
        expr = re.sub(
            r'\\begin\{' + env + r'\}(.*?)\\end\{' + env + r'\}',
            _bmatrix_to_brackets, expr, flags=re.DOTALL
        )

    # Replace other unsupported environments with plain text
    expr = re.sub(r'\\begin\{(\w+)\}', '', expr)
    expr = re.sub(r'\\end\{(\w+)\}', '', expr)
    # Replace \text{...} with mathrm
    expr = re.sub(r'\\text\{([^}]*)\}', r'\\mathrm{\1}', expr)

    return expr


def render_latex_to_base64(latex_expr, fontsize=14, display=False):
    """Render a LaTeX expression to a base64-encoded PNG using matplotlib mathtext."""
    def _try_render(expr):
        fig = plt.figure(figsize=(0.01, 0.01))
        fig.patch.set_alpha(0.0)
        wrapped = f"${expr}$"
        fig.text(0, 0, wrapped, fontsize=fontsize,
                 ha="left", va="baseline",
                 color="black", usetex=False)
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, transparent=True,
                    bbox_inches="tight", pad_inches=0.05)
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    try:
        return _try_render(latex_expr)
    except Exception:
        plt.close("all")

    # Retry with simplified expression (convert bmatrix etc.)
    try:
        simplified = _simplify_bmatrix(latex_expr)
        if simplified != latex_expr:
            return _try_render(simplified)
    except Exception:
        plt.close("all")

    return None


def replace_display_math(html):
    """Find $$...$$ blocks and replace with rendered PNG images (centered)."""
    def _replace(match):
        latex = match.group(1).strip()
        b64 = render_latex_to_base64(latex, fontsize=16, display=True)
        if b64:
            return (
                f'<div style="text-align:center;margin:12px 0;">'
                f'<img src="data:image/png;base64,{b64}" '
                f'alt="{latex[:80]}" style="max-width:90%;height:auto;">'
                f'</div>'
            )
        return match.group(0)

    return re.sub(r'\$\$(.+?)\$\$', _replace, html, flags=re.DOTALL)


def replace_inline_math(html):
    """Find $...$ (not $$) and replace with rendered PNG images (inline)."""
    def _replace(match):
        latex = match.group(1).strip()
        if not latex:
            return match.group(0)
        b64 = render_latex_to_base64(latex, fontsize=13, display=False)
        if b64:
            return (
                f'<img src="data:image/png;base64,{b64}" '
                f'alt="{latex[:80]}" '
                f'style="vertical-align:middle;height:1.3em;">'
            )
        return match.group(0)

    return re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)', _replace, html)


def convert_markdown_to_html(markdown_text: str) -> str:
    """Convert raw Markdown text to HTML with code highlighting, tables, TOC, and math/diagram post-processing."""

    extensions = [
        "fenced_code",
        "tables",
        "codehilite",
        "toc",
        "md_in_html",
    ]

    extension_configs = {
        "codehilite": {
            "css_class": "highlight",
            "guess_lang": False,
        },
    }

    html = markdown.markdown(
        markdown_text,
        extensions=extensions,
        extension_configs=extension_configs,
    )

    # Render display math $$...$$ as PNG images (must be done before inline math)
    html = replace_display_math(html)

    # Render inline math $...$ as PNG images
    html = replace_inline_math(html)

    return html


if __name__ == "__main__":
    import os

    test_md = """\
# Test Document

This is a paragraph demonstrating the markdown converter.

```python
def hello(name):
    return f"Hello, {name}!"
```

The quadratic formula uses $x^2$ and other terms.

$$
E = mc^2
$$

| Column A | Column B |
|----------|----------|
| 1        | Alpha    |
| 2        | Beta     |

DIAGRAM: {"type": "flowchart", "description": "Simple test diagram"}
"""

    html = convert_markdown_to_html(test_md)

    os.makedirs("output", exist_ok=True)
    with open("output/test_conversion.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Conversion complete — check output/test_conversion.html")
