"""Converts Markdown output from the document writer into HTML suitable for PDF rendering."""

import re
import markdown


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

    # Post-process: wrap display math $$...$$ in <div class="math-block">
    html = re.sub(
        r'\$\$(.+?)\$\$',
        r'<div class="math-block">\1</div>',
        html,
        flags=re.DOTALL,
    )

    # Post-process: wrap inline math $...$ in <span class="math-inline">
    # Avoid matching already-processed math-block divs
    html = re.sub(
        r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',
        r'<span class="math-inline">\1</span>',
        html,
    )

    # Post-process: wrap DIAGRAM: {...} lines in <div class="diagram">
    html = re.sub(
        r'DIAGRAM:\s*(\{.*?\})',
        r'<div class="diagram">\1</div>',
        html,
        flags=re.DOTALL,
    )

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
