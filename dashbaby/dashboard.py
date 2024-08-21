import os
from pathlib import Path

import streamlit as st
from baby import Baby
from data_loader import load_descriptor
from login import are_hidden_urls, reveal_urls
from plots import (
    plot_average_daily_increment,
    plot_cc,
    plot_lengths,
    plot_summary,
    plot_weights,
)

AUTH_ERROR_MSG = "Invalid password! Please enter the correct pin code."
COLOR_PALETTE = [
    "#e377c2",  # raspberry yogurt pink
    "#9467bd",  # muted purple
    "#d62728",  # brick red
]

CONNECTORS_FOLDER = Path("data_loaders")
BANNER_IMAGE = ".streamlit/banner.png"
SECRET_PIN = os.environ.get("SECRET_PIN")


def display_data_error() -> None:
    st.error("Data Error: Hidden URLs remain in the descriptors.")
    st.info("Maybe someone forgot to set env vars?")
    st.stop()  # This will stop the execution and display only the error screen.


# Function to display the login page
def display_login() -> None:
    col1, sep12, col2, sep23, col3 = st.columns([1, 0.1, 1, 0.1, 1])
    with col2:
        st.title("Welcome back.")
        password = st.text_input("Enter your secret pin code:", type="password")

        if st.button("Go"):
            if password and password == SECRET_PIN:
                st.success("Login successful!")
                st.session_state.logged_in = True
                st.rerun()  # Rerun to display the dashboard
            else:
                st.error(AUTH_ERROR_MSG)


# Function to display the main dashboard
def display_dashboard(babies: list[Baby]):
    tab1, tab2, tab3 = st.tabs(["Today", "History", "Monthly Report"])

    with tab1:
        st.image(BANNER_IMAGE, use_column_width=True)
        st.write("")
        st.header("Today")

        # Create three columns with padding
        col1, sep12, col2 = st.columns([1, 0.1, 1])
        with col1:
            for i, baby in enumerate(babies):
                if i % 2 == 0:  # Even index
                    plot_summary(baby)

        with col2:
            for i, baby in enumerate(babies):
                if i % 2 != 0:  # Odd index
                    plot_summary(baby)

    with tab2:
        st.image(BANNER_IMAGE, use_column_width=True)
        st.write("")
        st.header("History")

        # Create three columns with padding
        col1, sep12, col2, sep23, col3 = st.columns([1, 0.1, 1, 0.1, 1])

        with col1:
            # Plot weights for selected baby
            st.subheader("Weight")
            plot_weights(babies, COLOR_PALETTE)

        with sep12:
            st.write("")

        with col2:
            # Plot weights for selected baby
            st.subheader("Length")
            plot_lengths(babies, COLOR_PALETTE)

        with sep23:
            st.write("")

        with col3:
            # Plot weights for selected baby
            st.subheader("Cephalic Circumference")
            plot_cc(babies, COLOR_PALETTE)

    with tab3:
        st.image(BANNER_IMAGE, use_column_width=True)
        st.write("")
        st.header("Monthly Report")

        # Create three columns with padding
        col1, sep12, col2 = st.columns([1, 0.1, 1])
        with col1:
            for i, baby in enumerate(babies):
                if i % 2 == 0:  # Even index
                    color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
                    plot_average_daily_increment(
                        baby, lambda baby: baby.weight, bar_color=color
                    )
                    plot_average_daily_increment(
                        baby, lambda baby: baby.length, bar_color=color
                    )

        with col2:
            for i, baby in enumerate(babies):
                if i % 2 != 0:  # Odd index
                    color = COLOR_PALETTE[i % len(COLOR_PALETTE)]
                    plot_average_daily_increment(
                        baby, lambda baby: baby.weight, bar_color=color
                    )
                    plot_average_daily_increment(
                        baby, lambda baby: baby.length, bar_color=color
                    )


# Main logic
babies_descriptors = []
for file in CONNECTORS_FOLDER.glob("*.json"):
    descriptor = load_descriptor(file)
    descriptor = reveal_urls(descriptor)
    babies_descriptors.append(descriptor)

st.set_page_config(layout="wide")

if are_hidden_urls(babies_descriptors):
    display_data_error()

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if st.session_state.logged_in:
    babies = [Baby.from_dict(descriptor) for descriptor in babies_descriptors]
    display_dashboard(babies)
else:
    display_login()
