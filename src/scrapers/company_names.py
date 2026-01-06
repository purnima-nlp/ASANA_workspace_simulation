import requests
import csv
import io

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
    Fetch company names from a public tech-company CSV.
    Falls back to static names if network or parsing fails.
    """
    try:
        resp = requests.get(RAW_CSV_URL, timeout=5)
        resp.raise_for_status()

        csv_file = io.StringIO(resp.text)
        reader = csv.DictReader(csv_file)

        names = []
        for row in reader:
            name = row.get("Company Name")
            if name:
                name = name.strip()
                if name and name not in names:
                    names.append(name)

            if len(names) >= limit:
                break

        if len(names) < 5:
            raise ValueError("Too few company names parsed")

        return names

    except Exception:
        return FALLBACK_COMPANY_NAMES

