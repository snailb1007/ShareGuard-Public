"""Clean-room ClearURLs extractor: downloads data and keeps literal parameter names only."""

import requests
import re

CLEARURLS_DATA_URLS = [
    "https://rules2.clearurls.xyz/data.minify.json",  # GitHub Pages (primary)
    "https://rules1.clearurls.xyz/data.minify.json",  # GitLab Pages (fallback)
]

# Literal parameter names only: alphanumeric/underscore/hyphen, plain or
# wrapped in parentheses. Everything else is regex-shaped and rejected.
_LITERAL_RULE_PATTERN = re.compile(r"([a-zA-Z0-9_-]+)|\(([a-zA-Z0-9_-]+)\)")


def extract_clearurls_data():
    """
    Downloads ClearURLs data and extracts ONLY the parameter names.
    This is a clean-room implementation that discards all regex logic.
    """
    data: dict | None = None
    last_error = None
    for url in CLEARURLS_DATA_URLS:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            break
        except (requests.RequestException, ValueError) as e:
            # Network errors and JSON decoding failures are both retryable
            # against the next URL; only fail once every URL has been tried.
            last_error = e
            continue
    if not isinstance(data, dict):
        if last_error is not None:
            raise last_error
        raise RuntimeError("No ClearURLs data URLs configured")

    extracted_params = set()

    for info in data.get("providers", {}).values():
        rules = info.get("rules", [])
        for rule in rules:
            match = _LITERAL_RULE_PATTERN.fullmatch(rule)
            if not match:
                # Regex-shaped rule: not a literal parameter name, so skip it
                # rather than sanitizing it into a different parameter.
                continue
            clean_param = match.group(1) or match.group(2)
            if clean_param and len(clean_param) > 1:
                extracted_params.add(clean_param)

    return {
        "sacred_params": sorted(extracted_params),
        "shortener_domains": [],
    }
