import requests

# Fallback list (always available)
FALLBACK_COMPANY_NAMES = [
    "CloudNova",
    "DataFlux",
    "ScaleOps",
    "InfraStack",
    "Productify",
    "Launchpad Systems",
    "MetricHive",
    "SignalWorks",
    "Vertex Labs",
]

DATASET_URL = (
    "https://raw.githubusercontent.com/datasets/companies/master/data/companies.csv"
)


def get_company_names(limit: int = 50):
    """
    Fetch company names from a public dataset.
    Falls back to a static list if network is unavailable.

    This simulates sampling from YC / Crunchbase–like corpora
    without violating ToS or requiring auth.
    """
    try:
        resp = requests.get(DATASET_URL, timeout=5)
        resp.raise_for_status()

        lines = resp.text.splitlines()[1 : limit + 1]
        names = []

        for line in lines:
            name = line.split(",")[0].strip()
            if name:
                names.append(name)

        # Safety check
        if len(names) < 5:
            raise ValueError("Too few names scraped")

        return names

    except Exception:
        return FALLBACK_COMPANY_NAMES

