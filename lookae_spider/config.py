from pathlib import Path
from typing import Dict

# Category path segments on LookAE (After Effects section)
CATEGORY_PATHS: Dict[str, str] = {
    # plugins/scripts
    "aescripts": "after-effects/aescripts",
    # categories requested by user
    "aechajian": "after-effects/aechajian",
    "aejiaocheng": "after-effects/aejiaocheng",
    "other-after-effects": "after-effects/other-after-effects",
}

# Defaults
DEFAULT_CATEGORY = "aescripts"
DEFAULT_OUTPUT_ROOT = Path("data/lookae")
DEFAULT_CONCURRENCY = 3  # polite by default
DEFAULT_DELAY_SECONDS = 0.5  # base delay between requests


def build_listing_url(category: str, page: int) -> str:
    seg = CATEGORY_PATHS.get(category, CATEGORY_PATHS[DEFAULT_CATEGORY])
    return f"https://www.lookae.com/{seg}/page/{page}/"


def output_dir_for(category: str) -> Path:
    seg = category if category in CATEGORY_PATHS else DEFAULT_CATEGORY
    out = DEFAULT_OUTPUT_ROOT / seg
    out.mkdir(parents=True, exist_ok=True)
    return out
