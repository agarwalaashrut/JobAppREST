"""
api_client.py
This module contains helper functions to interact with an external job listing
service via a REST API.  In the context of this project the REST API
is assumed to expose a ``/jobs`` endpoint that accepts a search query via a
``search`` query parameter.  Adjust ``BASE_URL`` and the logic in
``get_jobs`` to match the real API you intend to consume.

Using a dedicated module for API calls keeps the Flask application code
clean and makes it easy to swap out the implementation if you change
services or add authentication later on.
"""

from typing import List, Dict

import requests

# Base URL of the third‑party job listings API.  Replace this with the
# actual service you plan to call.  The default provided here is a
# placeholder and will not return real results without modification.
BASE_URL = "https://jobs-api.example.com"


def get_jobs(job_title: str) -> List[Dict[str, str]]:
    """Fetch job listings matching ``job_title`` from an external REST API.

    Args:
        job_title: The job title or keywords entered by the user.

    Returns:
        A list of dictionaries, each representing a job posting.  Each
        dictionary should contain at least ``title``, ``company``,
        ``location`` and ``link`` keys.  If the API call fails or returns
        unexpected data an empty list is returned.
    """
    # Compose the request URL.  Here we assume the API exposes a
    # ``/jobs`` endpoint that accepts search queries via a ``search``
    # query parameter.  Adjust the endpoint or parameters to match your
    # actual API.
    url = f"{BASE_URL}/jobs"
    params = {"search": job_title}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
    except Exception as exc:
        # Log the error and return no results.  In a real application
        # consider logging to a file or monitoring system instead of
        # printing to stdout.
        print(f"Error fetching jobs: {exc}")
        return []

    try:
        data = response.json()
    except ValueError:
        print("Received non‑JSON response from job API")
        return []

    # The expected structure of ``data`` depends on the API you call.  Here
    # we assume it returns a top‑level object with a ``jobs`` list, where
    # each entry is a dict containing relevant fields.  If your API
    # returns data in a different shape adjust the extraction accordingly.
    jobs = data.get("jobs")
    if not isinstance(jobs, list):
        return []
    # Filter each job to contain only the keys we care about and provide
    # sensible default values to avoid ``KeyError`` if a key is missing.
    normalized: List[Dict[str, str]] = []
    for job in jobs:
        normalized.append(
            {
                "title": str(job.get("title", "N/A")),
                "company": str(job.get("company", "")),
                "location": str(job.get("location", "")),
                "link": str(job.get("link", "")),
            }
        )
    return normalized
