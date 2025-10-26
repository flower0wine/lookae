from dataclasses import dataclass
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
from slugify import slugify
from markdownify import markdownify


@dataclass
class Item:
    title: str
    url: str
    thumb: Optional[str] = None
    summary: Optional[str] = None
    slug: Optional[str] = None


def parse_listing(html: str) -> List[Item]:
    soup = BeautifulSoup(html, "html.parser")
    items: List[Item] = []
    for art in soup.select("article, div.post, li.post"):
        a = art.select_one("a")
        title_el = art.select_one("h2, h3, .entry-title, .post-title")
        img = art.select_one("img")
        if a and a.get("href"):
            url = a["href"]
            title = (title_el.get_text(strip=True) if title_el else a.get_text(strip=True)) or url
            thumb = img["src"] if img and img.get("src") else None
            summary_el = art.select_one(".entry-summary, .excerpt, p")
            summary = summary_el.get_text(" ", strip=True) if summary_el else None
            items.append(Item(title=title, url=url, thumb=thumb, summary=summary, slug=slugify(title)))
    if not items:
        for a in soup.select(".entry-title a, h2 a, h3 a, a[rel='bookmark']"):
            url = a.get("href")
            if not url:
                continue
            title = a.get_text(strip=True) or url
            items.append(Item(title=title, url=url, slug=slugify(title)))
    return items


def extract_article_md_and_tags(html: str) -> Tuple[str, List[str]]:
    if not html:
        return "", []
    soup = BeautifulSoup(html, "html.parser")

    header = soup.select_one("header.article-header")
    tags_div = soup.select_one("div.article-tags")
    article = soup.select_one("article.article-content, .article-content") or soup

    tags: List[str] = []
    if tags_div:
        for a in tags_div.select("a"):
            txt = a.get_text(strip=True)
            if txt:
                tags.append(txt)

    container_html_parts: List[str] = []
    for node in (header, tags_div, article):
        if node:
            for sel in ["script", "style", ".ads", ".ad", "noscript"]:
                for t in node.select(sel):
                    t.decompose()
            container_html_parts.append(str(node))

    merged_html = "\n".join(container_html_parts) if container_html_parts else str(article)

    try:
        md = markdownify(merged_html, heading_style="ATX")
    except Exception:
        md = BeautifulSoup(merged_html, "html.parser").get_text("\n", strip=True)
    return md.strip(), tags
