"""
Rule Compiler — merges extracted tracking parameters into ShareGuard RuleSet JSON.

Clean-room implementation: only factual parameter names are included.
No regex, no blocking syntax, no proprietary logic from upstream sources.
"""

import datetime
import json
import os
from pathlib import Path
import sys

from extractors.clearurls_extractor import extract_clearurls_data
from extractors.adguard_extractor import extract_adguard_data

IGNORE_LIST_PATH = Path(__file__).parent / "ignore_list.txt"
SHORTENERS_PATH = Path(__file__).parent / "shorteners.json"
OUTPUT_FILENAME = "latest.json"


def load_shorteners(path: Path = SHORTENERS_PATH) -> dict:
    """Load shortener domains and exclusions.

    Raises FileNotFoundError when the configuration file is missing; a
    configuration file that exists may still carry empty lists.
    """
    if not path.exists():
        raise FileNotFoundError(f"Shortener configuration not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_ignore_list(path: Path = IGNORE_LIST_PATH) -> set[str]:
    """Load functional parameters that must never be stripped."""
    if not path.exists():
        return set()
    with open(path, "r", encoding="utf-8") as f:
        return {
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        }


def compile_rules(output_path: str | None = None) -> dict:
    """
    Extract, merge, deduplicate, filter, and output ShareGuard RuleSet JSON.

    Returns the compiled rule set dictionary.
    """
    print("Extracting ClearURLs data...")
    clearurls_data = extract_clearurls_data()
    print(f"  → {len(clearurls_data['sacred_params'])} params from ClearURLs")

    print("Extracting AdGuard data...")
    adguard_data = extract_adguard_data()
    print(f"  → {len(adguard_data['sacred_params'])} params from AdGuard")

    # Merge and deduplicate
    all_params = set(clearurls_data["sacred_params"]) | set(adguard_data["sacred_params"])

    # Load and apply ignore list
    ignore_list = load_ignore_list()
    filtered_params = all_params - ignore_list
    ignored_count = len(all_params) - len(filtered_params)
    if ignored_count > 0:
        print(f"  → Filtered out {ignored_count} functional params from ignore list")

    # Load shortener domains
    shorteners = load_shorteners()
    print(f"  → {len(shorteners['shortener_domains'])} shortener domains loaded")

    # Sort for deterministic output
    sorted_params = sorted(filtered_params)

    # Build version and expiry: workflow-provided VERSION wins, UTC date is the fallback
    now = datetime.datetime.now(datetime.timezone.utc)
    version = os.environ.get("VERSION") or now.strftime("%Y.%m.%d")
    expires_at = (now + datetime.timedelta(days=90)).strftime("%Y-%m-%d")

    # Construct ShareGuard RuleSet
    rule_set = {
        "version": version,
        "schema_version": 1,
        "expires_at": expires_at,
        "global": {
            "analytics_strip": sorted_params,
            "analytics_prefix": [],
        },
        "domains": {},
        "redirect_chains": {},
        "sacred_params": sorted(ignore_list),
        "shortener_domains": shorteners["shortener_domains"],
        "shortener_excluded": shorteners["shortener_excluded"],
    }

    # Write output
    if output_path is None:
        output_path = OUTPUT_FILENAME

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(rule_set, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"\nCompiled {len(sorted_params)} parameters → {output_path}")
    print(f"  Version: {version}")
    print(f"  Expires: {expires_at}")

    return rule_set


if __name__ == "__main__":
    output_arg = sys.argv[1] if len(sys.argv) > 1 else None
    compile_rules(output_arg)
