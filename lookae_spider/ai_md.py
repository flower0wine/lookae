import os
from typing import Dict, Any
from textwrap import dedent
from slugify import slugify
from openai import OpenAI


def to_front_matter(meta: Dict[str, Any]) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, (list, tuple)):
            lines.append(f"{k}: [{', '.join(map(str, v))}]")
        else:
            v_str = str(v).replace('\n', ' ')
            lines.append(f"{k}: {v_str}")
    lines.append("---\n")
    return "\n".join(lines)


class AIParser:
    """Optional AI-backed Markdown formatter.

    If OPENAI_API_KEY is available, uses GPT to normalize item content into
    a consistent Markdown template. Otherwise falls back to a deterministic
    template.
    """

    def __init__(self, model: str | None = None):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.client = None
        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception:
                self.client = None

    def to_markdown(self, item: Dict[str, Any]) -> str:
        """Given a scraped item {title, url, markdown, html, ...},
        return a Markdown document with YAML front-matter.
        """
        slug = slugify(item.get("title") or item.get("url", "item"))
        meta = {
            "title": item.get("title") or slug,
            "slug": slug,
            "source_url": item.get("url"),
            "category": item.get("category", "aescripts"),
        }
        if item.get("tags"):
            meta["tags"] = item.get("tags")
        body = item.get("markdown") or ""

        if self.client:
            prompt = dedent(
                f"""
                You are a documentation editor for a resource/download site (LookAE-style).
                The goal is to produce a concise, well-structured Markdown page summarizing
                the resource (plugin/script/preset/tutorial). The input has already been
                trimmed to the main article section and converted to Markdown to reduce tokens.

                Requirements:
                - Do NOT hallucinate or invent missing info. Use only what's present.
                - Keep it short and useful; remove marketing fluff and boilerplate.
                - Preserve code blocks, commands, version numbers, and filenames accurately.
                - Keep markdown clean and standard; no HTML.

                Title: {meta['title']}
                Source URL: {meta['source_url']}

                Content (already in Markdown):
                ---
                {body}
                ---
                """
            ).strip()
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    temperature=0.2,
                    messages=[
                        {"role": "system", "content": "Return clean Markdown only, no YAML, no extra commentary."},
                        {"role": "user", "content": prompt},
                    ],
                )
                body = resp.choices[0].message.content or body
            except Exception:
                # Fallback to deterministic
                pass

        fm = to_front_matter(meta)
        return f"{fm}{body.strip()}\n"
