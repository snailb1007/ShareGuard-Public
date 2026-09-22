import requests
import re

ADGUARD_TRACKING_URL = "https://raw.githubusercontent.com/AdguardTeam/FiltersRegistry/master/filters/filter_3_Spyware/filter.txt"


def extract_adguard_data():
    """
    Downloads AdGuard Tracking filter and extracts tracking parameters.
    Discards all blocking rules and regex.
    """
    response = requests.get(ADGUARD_TRACKING_URL, timeout=30)
    response.raise_for_status()
    lines = response.text.splitlines()

    extracted_params = set()

    for line in lines:
        if "$removeparam=" in line and not line.startswith("!"):
            match = re.search(r'\$removeparam=([a-zA-Z0-9_-]+)', line)
            if match:
                extracted_params.add(match.group(1))

    return {
        "sacred_params": sorted(extracted_params),
        "shortener_domains": [],
    }
