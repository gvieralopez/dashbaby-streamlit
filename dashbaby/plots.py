from typing import Callable

import altair as alt
import pandas as pd
import streamlit as st
from baby import Baby, Variable
from meds import get_baby_intake_df


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
    babies: list[Baby],
    variable_selector: Callable[[Baby], Variable],
    colors: list[str],
):
    if not len(babies):
        return

    # Merge the dataframes of the selected variable
    var_name, units = "", ""
    merged_df = pd.DataFrame()
    for baby in babies:
        variable = variable_selector(baby)
        if not var_name:
            var_name, units = variable.name, variable.units
        df = variable.history.rename(columns={"Value": baby.name})
        merged_df = (
            pd.merge(merged_df, df, on="Date", how="outer")
            if not merged_df.empty
            else df
        )
    merged_df = merged_df.ffill().bfill()

    # Convert dates to elapsed days
    merged_df["Date"] = (merged_df["Date"] - merged_df["Date"].min()).dt.days

    # Prepare the data in a long format for Altair
    merged_df = merged_df.melt(id_vars=["Date"], var_name="Baby", value_name=var_name)

    # Create the line chart using Altair
    chart = (
        alt.Chart(merged_df)
        .mark_line()
        .encode(
            x=alt.X("Date", title="Living time [Days]"),
            y=alt.Y(var_name, title=f"{var_name} [{units}]"),
            color=alt.Color(
                "Baby:N", scale=alt.Scale(range=colors) if colors else alt.Undefined
            ),
        )
        .properties(width=700, height=400)
    )

    st.altair_chart(chart, use_container_width=True)


def plot_average_daily_increment(
    baby: Baby,
    variable_selector: Callable[[Baby], Variable],
    bar_color: str = "steelblue",
):
    if baby is None:
        st.write("No baby data available.")
        return

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


def plot_weights(babies: list[Baby], colors: list[str]):
    plot_trend(babies, lambda baby: baby.weight, colors)


def plot_lengths(babies: list[Baby], colors: list[str]):
    plot_trend(babies, lambda baby: baby.length, colors)


def plot_cc(babies: list[Baby], colors: list[str]):
    plot_trend(babies, lambda baby: baby.cc, colors)
