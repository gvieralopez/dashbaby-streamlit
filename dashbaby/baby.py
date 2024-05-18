from datetime import datetime
from pathlib import Path

import pandas as pd
from data_loader import load_data, load_descriptor, load_meds


class Variable:
    def __init__(self, name: str, units: str, dataframe: pd.DataFrame):
        self.name = name
        self.units = units
        self.history = self.clean_history_samples(dataframe)

        self.last_updated = self.history["Date"].iloc[-1]
        self.current = self.history["Value"].iloc[-1]
        self.compute_time_increments()

    def clean_history_samples(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans the dataframe from NaN values and ensure samples are sorted.
        """
        history = dataframe.dropna().copy()
        history.rename(columns={self.name: "Value"}, inplace=True)
        history.sort_values("Date", inplace=True)
        return history

    def prior_sample_with_minimum_days_difference(
        self, reference_sample: pd.Series, min_days: int
    ) -> pd.Series | None:
        """
        Finds the first sample in the history with a time difference
        of at least 'min_days' from the given reference sample.
        """
        old_sample = None
        for index, row in self.history.iloc[::-1].iterrows():
            days_difference = (reference_sample["Date"] - row["Date"]).days
            if days_difference >= min_days:
                old_sample = row
                break
        return old_sample

    def compute_time_increments(self):
        """
        Computes average daily and weekly increments.
        """
        self.daily_increment, self.weekly_increment = 0, 0

        if len(self.history) < 2:
            return

        last_entry = self.history.iloc[-1]
        week_old_sample = self.prior_sample_with_minimum_days_difference(last_entry, 7)

        if week_old_sample is None:
            return

        value_difference = last_entry["Value"] - week_old_sample["Value"]
        days_difference = (last_entry["Date"] - week_old_sample["Date"]).days
        self.daily_increment = round(value_difference / days_difference, 2)
        self.weekly_increment = round(self.daily_increment * 7, 2)


class Baby:
    def __init__(self, name: str, data: pd.DataFrame, meds: pd.DataFrame):
        self.name = name
        self.age = self.calculate_age(data)
        self.weight = Variable("Weight", "g", data[["Date", "Weight"]])
        self.length = Variable("Length", "cm", data[["Date", "Length"]])
        self.cc = Variable(
            "Cephalic Circumference", "cm", data[["Date", "Cephalic Circumference"]]
        )
        self.meds = meds
        self.data = data

    def calculate_age(self, data: pd.DataFrame) -> int:
        oldest_date = data["Date"].min().date()
        today = datetime.today().date()
        return (today - oldest_date).days

    @classmethod
    def from_descriptor(cls, descriptor_file: Path):
        conn = load_descriptor(descriptor_file)
        return cls.from_dict(conn)

    @classmethod
    def from_dict(cls, descriptor: dict):
        data_ss, meds_ss = (
            descriptor["data_spreadsheet"],
            descriptor["meds_spreadsheet"],
        )
        data_df = load_data(data_ss["url"], data_ss["sheet"], data_ss["fields"])
        meds_df = load_meds(meds_ss["url"], meds_ss["sheet"], meds_ss["fields"])
        return cls(name=descriptor["name"], data=data_df, meds=meds_df)
