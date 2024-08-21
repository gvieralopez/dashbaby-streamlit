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
    try:
        df = pd.read_excel(url, sheet_name)
    except Exception as e:
        print(url)
        print(e)
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


def load_weight_percentils(
    url: str = "dashbaby/data/wtageinf.csv", gender: int = 2
) -> pd.DataFrame:
    percentiles_df = pd.read_csv(url)

    # Filter the DataFrame by gender
    percentiles_df = percentiles_df[percentiles_df["Sex"] == gender]

    # Convert 'Agemos' (months) to 'Days'
    percentiles_df["Days"] = percentiles_df["Agemos"] * 30.4375

    # Convert weights from kg to g by multiplying relevant columns by 1000
    weight_columns = ["P3", "P5", "P10", "P25", "P50", "P75", "P90", "P95", "P97"]
    percentiles_df[weight_columns] = percentiles_df[weight_columns] * 1000

    return percentiles_df


def load_length_percentils(
    url: str = "dashbaby/data/lenageinf.csv", gender: int = 2
) -> pd.DataFrame:
    percentiles_df = pd.read_csv(url)

    # Filter the DataFrame by gender
    percentiles_df = percentiles_df[percentiles_df["Sex"] == gender]

    # Convert 'Agemos' (months) to 'Days'
    percentiles_df["Days"] = percentiles_df["Agemos"] * 30.4375

    return percentiles_df

def load_cc_percentils(
    url: str = "dashbaby/data/hcageinf.csv", gender: int = 2
) -> pd.DataFrame:
    percentiles_df = pd.read_csv(url)

    # Filter the DataFrame by gender
    percentiles_df = percentiles_df[percentiles_df["Sex"] == gender]

    # Convert 'Agemos' (months) to 'Days'
    percentiles_df["Days"] = percentiles_df["Agemos"] * 30.4375

    return percentiles_df
