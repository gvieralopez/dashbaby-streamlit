import os

import requests


def check_url(url: str | None) -> bool:
    # Make an HTTP request to the decrypted URL
    if url is None:
        return False
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True
        else:
            return False
    except requests.RequestException:
        return False


def reveal_urls(descriptor: dict) -> dict:
    for spreadsheet_type in ["data_spreadsheet", "meds_spreadsheet"]:
        spreadsheet = descriptor.get(spreadsheet_type, {})
        if spreadsheet.get("is_hidden", False):
            hidden_url = spreadsheet.get("url")
            revealed_url = os.environ.get(hidden_url)
            if check_url(revealed_url):
                spreadsheet["url"] = revealed_url
                spreadsheet["is_hidden"] = False
    return descriptor


def are_hidden_urls(babies_descriptors: list[dict]) -> bool:
    for descriptor in babies_descriptors:
        for spreadsheet_type in ["data_spreadsheet", "meds_spreadsheet"]:
            if descriptor.get(spreadsheet_type, {}).get("is_hidden", False):
                return True
    return False
