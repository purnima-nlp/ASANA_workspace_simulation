import requests

FALLBACK_COMPANY_NAMES = [
    "CloudNova",
    "DataFlux",
    "ScaleOps",
    "InfraStack",
    "Productify",
    "Launchpad Systems",
    "MetricHive",
    "SignalWorks",
    "Vertex Labs"
]

RAW_CSV_URL = (
    "https://raw.githubusercontent.com/connor11528/tech-companies-and-startups/master/companies.csv"
)


def get_company_names(limit: int = 100):
    """
    Try to scrape company names from a public GitHub repo.
    If network fails or parsing fails, return fallback names.
    """
    try:
        resp = requests.get(RAW_CSV_URL, timeout=5)
        resp.raise_for_status()

        lines = resp.text.splitlines()
        # Skip header if present
        if lines and "," in lines[0]:
            lines = lines[1:]

        names = []
        for line in lines:
            parts = line.strip().split(",")
            if parts:
                # First column is typically company name
                name = parts[0].strip()
                if name and name not in names:
                    names.append(name)

            if len(names) >= limit:
                break

        if len(names) < 5:
            raise ValueError("Too few names scraped")

        return names

    except Exception:
        # Network errors, parsing errors, or too few names
        return FALLBACK_COMPANY_NAMES
