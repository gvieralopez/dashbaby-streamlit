import pandas as pd
from baby import Baby

MIN_DAILY_MILK_INTAKE_UNDER_3_MONTHS = 140  # ml / kg / day
MAX_DAILY_MILK_INTAKE_UNDER_3_MONTHS = 200  # ml / kg / day
DAILY_VITAMIN_D_TARGET_UNDER_1_YEAR = 500  # ui / day
MIN_IRON_INTAKE_UNDER_6_MONTHS = 4  # mg / kg / day
MAX_IRON_INTAKE_UNDER_6_MONTHS = 10  # mg / kg / day


def compute_milk_intake_3h_ml(age: int, weight: float, daily_dose: float) -> str:
    weight_kg = weight / 1000
    if age < 90:
        return str(int(daily_dose * weight_kg / 8))
    return "?"


def compute_range_milk_intake_3h_ml(age: int, weight: float) -> str:
    max_dose = compute_milk_intake_3h_ml(
        age, weight, MAX_DAILY_MILK_INTAKE_UNDER_3_MONTHS
    )
    min_dose = compute_milk_intake_3h_ml(
        age, weight, MIN_DAILY_MILK_INTAKE_UNDER_3_MONTHS
    )
    return f"{min_dose} - {max_dose}"


def compute_vitamin_d_intake_24h_drops(age: int, concentration: float) -> str:
    if age < 365:
        return str(int(DAILY_VITAMIN_D_TARGET_UNDER_1_YEAR / concentration))
    return "?"


def compute_iron_intake_12h_drops(
    age: int, weight: float, concentration: float, daily_dose: float
) -> str:
    weight_kg = weight / 1000
    if age < 183:
        return str(int(0.5 * (daily_dose * weight_kg) / concentration))
    return "?"


def compute_range_iron_intake_12h_drops(
    age: int, weight: float, concentration: float
) -> str:
    max_dose = compute_iron_intake_12h_drops(
        age, weight, concentration, MAX_IRON_INTAKE_UNDER_6_MONTHS
    )
    min_dose = compute_iron_intake_12h_drops(
        age, weight, concentration, MIN_IRON_INTAKE_UNDER_6_MONTHS
    )
    return f"{min_dose} - {max_dose}"


def get_med_concentration(meds_df: pd.DataFrame, med_name: str) -> float:
    return meds_df.loc[meds_df["Med"] == med_name, "Concentration"].values[0]


def compute_all_doses_for_baby(baby: Baby) -> dict[str, dict[str, str]]:
    weight = baby.weight.current
    age = baby.age
    vit_d_concentration = get_med_concentration(baby.meds, "Vitamina D")
    fe_concentration = get_med_concentration(baby.meds, "Hierro")

    return {
        "Milk": {
            "Value": compute_range_milk_intake_3h_ml(age, weight),
            "Unit": "ml",
            "Interval": "3h",
        },
        "Vitamin D": {
            "Value": compute_vitamin_d_intake_24h_drops(age, vit_d_concentration),
            "Unit": "drops",
            "Interval": "24h",
        },
        "Iron": {
            "Value": compute_range_iron_intake_12h_drops(age, weight, fe_concentration),
            "Unit": "drops",
            "Interval": "12h",
        },
    }


def get_baby_intake_df(baby: Baby) -> pd.DataFrame:
    baby_intake = compute_all_doses_for_baby(baby)
    df_data: dict[str, list[str]] = {
        "Substance": [],
        "Value": [],
        "Unit": [],
        "Interval": [],
    }

    for substance, details in baby_intake.items():
        df_data["Substance"].append(substance)
        df_data["Value"].append(details["Value"])
        df_data["Unit"].append(details["Unit"])
        df_data["Interval"].append(details["Interval"])

    return pd.DataFrame(df_data)
