import requests
import re

CLEARURLS_DATA_URLS = [
    "https://rules2.clearurls.xyz/data.minify.json",  # GitHub Pages (primary)
    "https://rules1.clearurls.xyz/data.minify.json",  # GitLab Pages (fallback)
]


def extract_clearurls_data():
    """
    Downloads ClearURLs data and extracts ONLY the parameter names.
    This is a clean-room implementation that discards all regex logic.
    """
    response = None
    last_error = None
    for url in CLEARURLS_DATA_URLS:
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = e
            continue
    if response is None:
        raise last_error
    data = response.json()

    extracted_params = set()

    for info in data.get("providers", {}).values():
        rules = info.get("rules", [])
        for rule in rules:
            clean_param = re.sub(r'[^a-zA-Z0-9_-]', '', rule)
            if clean_param and len(clean_param) > 1:
                extracted_params.add(clean_param)

    return {
        "sacred_params": sorted(extracted_params),
        "shortener_domains": [],
    }
