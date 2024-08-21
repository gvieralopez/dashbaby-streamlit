from typing import Callable

import altair as alt
import pandas as pd
import streamlit as st
from baby import Baby, Variable
from meds import get_baby_intake_df
from data_loader import (
    load_weight_percentils,
    load_length_percentils,
    load_cc_percentils,
)


weight_percentils = load_weight_percentils()
length_percentils = load_length_percentils()
cc_percentils = load_cc_percentils()

def plot_metrics(baby: Baby):
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Age", f"{baby.age} days")
    m2.metric(
        "Weight",
        f"{int(baby.weight.current)} {baby.weight.units}",
        f"{int(baby.weight.daily_increment)} {baby.weight.units} per day",
    )
    m3.metric(
        "Length",
        f"{baby.length.current} {baby.length.units}",
        f"{baby.length.weekly_increment} {baby.length.units} per week",
    )
    m4.metric(
        "Cephalic Circumference",
        f"{baby.cc.current} {baby.cc.units}",
    )
    st.write("")


def plot_intake_report(baby: Baby):
    st.table(get_baby_intake_df(baby))


def plot_summary(baby: Baby):
    st.subheader(f"{baby.name}'s summary")
    plot_metrics(baby)
    st.write("\nMilk and Medicine Intake")
    plot_intake_report(baby)


def plot_trend(
    babies: list,  # Assuming babies is a list of Baby objects or similar
    variable_selector: Callable[
        [Baby], Variable
    ],  # Adjust to select the correct variable
    colors: list[str],
    percentils: pd.DataFrame | None = None,
    corrected: bool = False,
):
    if not babies:
        return

    # Initialize empty dataframe for merging
    merged_df = pd.DataFrame()

    # Process each baby's data
    for baby in babies:
        variable = variable_selector(baby)
        df = variable.history.rename(columns={"Value": baby.name})

        # Convert 'Date' to elapsed days
        df["Date"] = (df["Date"] - df["Date"].min()).dt.days

        # Adjust for prematurity if corrected is True
        if corrected:
            df["Date"] = df["Date"] - baby.prematurity_days
            # Filter out rows where Date is less than or equal to 0
            df = df[df["Date"] > 0]

        # Merge dataframes
        merged_df = (
            pd.merge(merged_df, df, on="Date", how="outer")
            if not merged_df.empty
            else df
        )

    # Fill missing values
    merged_df = merged_df.ffill().bfill()

    # Prepare the data in a long format for Altair
    merged_df = merged_df.melt(
        id_vars=["Date"], var_name="Baby", value_name=variable.name
    )

    # Determine the maximum number of days from the babies' data
    max_days = merged_df["Date"].max()
    min_days = merged_df["Date"].min()

    # Create the baby's data line chart
    baby_chart = (
        alt.Chart(merged_df)
        .mark_line()
        .encode(
            x=alt.X(
                "Date",
                title=f"{'Corrected ' if corrected else ''}Living time [Days]",
            ),
            y=alt.Y(variable.name, title=f"{variable.name} [{variable.units}]"),
            color=alt.Color(
                "Baby:N", scale=alt.Scale(range=colors) if colors else alt.Undefined
            ),
        )
    )

    # Plot percentiles data with shaded regions
    if percentils is not None:
        # Filter percentiles data to include only rows up to the maximum number of days
        filtered_percentils = percentils[percentils["Days"] <= max_days + 16]
        filtered_percentils = filtered_percentils[
            filtered_percentils["Days"] >= min_days - 16
        ]

        # Define percentile ranges for shaded regions
        percentile_ranges = [
            ("P3", "P97"),
            ("P5", "P95"),
            ("P10", "P90"),
            ("P25", "P75"),
            ("P50", "P50"),
        ]

        # Create shaded areas and lines for percentile ranges
        percentile_areas = []
        percentile_lines = []
        for lower, upper in percentile_ranges:
            if lower != upper:
                percentile_area = (
                    alt.Chart(filtered_percentils)
                    .mark_area(opacity=0.2)  # Semi-transparent regions for percentiles
                    .encode(
                        x=alt.X(
                            "Days",
                            title=f"{'Corrected ' if corrected else ''}Living time [Days]",
                        ),
                        y=alt.Y(
                            f"{lower}", title=f"{variable.name} [{variable.units}]"
                        ),
                        y2=alt.Y2(f"{upper}"),
                        color=alt.value(
                            "gray"
                        ),  # Uniform color for all percentile areas
                    )
                )
                percentile_areas.append(percentile_area)
            else:
                percentile_line = (
                    alt.Chart(filtered_percentils)
                    .mark_line(color="gray")  # Gray line for P50
                    .encode(
                        x=alt.X(
                            "Days",
                            title=f"{'Corrected ' if corrected else ''}Living time [Days]",
                        ),
                        y=alt.Y(
                            f"{lower}", title=f"{variable.name} [{variable.units}]"
                        ),
                    )
                )
                percentile_lines.append(percentile_line)

        # Combine baby, shaded area, and line charts, ensuring baby's data is on top
        combined_chart = alt.layer(
            *percentile_areas, *percentile_lines, baby_chart
        ).properties(width=700, height=400)
    else:
        # If no percentiles are provided, only plot baby's data
        combined_chart = baby_chart

    st.altair_chart(combined_chart, use_container_width=True)


def plot_average_daily_increment(
    baby: Baby,
    variable_selector: Callable[[Baby], Variable],
    bar_color: str = "steelblue",
):
    variable = variable_selector(baby)
    if variable is None or not hasattr(variable, "history"):
        st.write("No valid variable data available.")
        return

    var_name, units = variable.name, variable.units
    df = variable.history.copy()

    if "Date" not in df.columns or "Value" not in df.columns:
        st.write("Missing required data columns.")
        return

    # Ensure 'Date' column is datetime type
    df["Date"] = pd.to_datetime(df["Date"])

    # Resample data to daily frequency and interpolate missing values
    df.set_index("Date", inplace=True)
    df_daily = df.resample(
        "D"
    ).first()  # Use 'first' to avoid introducing NaNs where not necessary
    df_daily["Value"] = df_daily[
        "Value"
    ].interpolate()  # Interpolate to fill missing values

    # Calculate daily increments
    df_daily["Daily Increment"] = df_daily["Value"].diff()

    # Reset index to remove 'Date' as the index if necessary for further processing
    df_daily.reset_index(inplace=True)

    # Calculate weekly averages
    weekly_df = df_daily.resample("W", on="Date").mean().reset_index()
    weekly_df.rename(
        columns={"Daily Increment": "Average Daily Increment"}, inplace=True
    )

    # Add a column for adjusted week number
    base_week = weekly_df["Date"].iloc[0].isocalendar().week
    weekly_df["Week Number"] = weekly_df["Date"].dt.isocalendar().week - base_week + 1

    # Create the bar chart using Altair
    chart = (
        alt.Chart(weekly_df)
        .mark_bar(color=bar_color)
        .encode(
            x=alt.X(
                "Week Number:O", title="Week", axis=alt.Axis(labelAngle=0)
            ),  # Set label angle to 0
            y=alt.Y(
                "Average Daily Increment:Q", title=f"Average Daily Increment [{units}]"
            ),
            tooltip=["Week Number:O", "Average Daily Increment:Q"],
        )
        .properties(
            width=700,
            height=400,
            title=f"{baby.name}'s Average Daily Increment of {var_name} [{units}]",
        )
    )

    st.altair_chart(chart, use_container_width=True)


def plot_weights(babies: list[Baby], colors: list[str], corrected: bool = False):
    plot_trend(babies, lambda baby: baby.weight, colors, weight_percentils, corrected)


def plot_lengths(babies: list[Baby], colors: list[str], corrected: bool = False):
    plot_trend(babies, lambda baby: baby.length, colors, length_percentils, corrected)


def plot_cc(babies: list[Baby], colors: list[str], corrected: bool = False):
    plot_trend(babies, lambda baby: baby.cc, colors, cc_percentils, corrected)
