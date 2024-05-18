import json
from pathlib import Path

import pandas as pd

DATA_COLUMNS = ["Date", "Weight", "Length", "Cephalic Circumference", "Event"]
MEDS_COLUMNS = ["Med", "Concentration", "Unit"]


def dataframe_has_all_columns(dataframe: pd.DataFrame, elements: list[str]) -> bool:
    """
    Ensure that all elements of a list are present as columns in a DataFrame.
    """
    return all(element in dataframe.columns for element in elements)


def load_descriptor(descriptor_file: Path) -> dict:
    with Path.open(descriptor_file, "r") as file:
        return json.load(file)


def load_spreadsheet(
    url: str, sheet_name: str, field_aliases: dict[str, str]
) -> pd.DataFrame:
    df = pd.read_excel(url, sheet_name)
    df.rename(
        columns={v: k for k, v in field_aliases.items()},
        inplace=True,
    )
    return df


def load_data(url: str, sheet_name: str, field_aliases: dict[str, str]) -> pd.DataFrame:
    df = load_spreadsheet(url, sheet_name, field_aliases)
    if dataframe_has_all_columns(df, DATA_COLUMNS):
        return df
    raise ValueError(f"Invalid dataframe columns {df.columns}, expected {DATA_COLUMNS}")


def load_meds(url: str, sheet_name: str, field_aliases: dict[str, str]) -> pd.DataFrame:
    df = load_spreadsheet(url, sheet_name, field_aliases)
    if dataframe_has_all_columns(df, MEDS_COLUMNS):
        return df
    raise ValueError(f"Invalid dataframe columns {df.columns}, expected {MEDS_COLUMNS}")


def get_encrypted_urls(babies_descriptors: list[dict]):
    encrypted_urls = set()
    for descriptor in babies_descriptors:
        for spreadsheet_type in ["data_spreadsheet", "meds_spreadsheet"]:
            if descriptor.get(spreadsheet_type, {}).get("is_encrypted", False):
                encrypted_urls.add(descriptor[spreadsheet_type]["url"])
    return encrypted_urls
