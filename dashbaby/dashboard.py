from pathlib import Path

import streamlit as st
from baby import Baby
from data_loader import get_encrypted_urls, load_descriptor
from login import check_url, decrypt_urls
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


# Function to display the login page
def display_login(encrypted_urls: set[str]):
    col1, sep12, col2, sep23, col3 = st.columns([1, 0.1, 1, 0.1, 1])
    with col2:
        st.title("Welcome back.")
        password = st.text_input("Enter your secret pin code:", type="password")

        if st.button("Go"):
            if password:
                try:
                    key = int(password)  # Use the password as an integer key
                    if all(
                        check_url(encrypted_url, key)
                        for encrypted_url in encrypted_urls
                    ):
                        st.success("Login successful!")
                        st.session_state.logged_in = True
                        st.session_state.key = key
                        st.rerun()  # Rerun to display the dashboard
                    else:
                        st.error(AUTH_ERROR_MSG)
                except ValueError:
                    st.error(AUTH_ERROR_MSG)
                except OverflowError:
                    st.error(AUTH_ERROR_MSG)
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
babies_descriptors = [
    load_descriptor(file) for file in CONNECTORS_FOLDER.glob("*.json")
]
encrypted_urls = get_encrypted_urls(babies_descriptors)

st.set_page_config(layout="wide")

if "logged_in" not in st.session_state.keys():
    st.session_state.logged_in = False

if not any(encrypted_urls):
    st.session_state.logged_in = True

if st.session_state.logged_in:
    if any(encrypted_urls):
        babies_descriptors = [
            decrypt_urls(descriptor, st.session_state.key)
            for descriptor in babies_descriptors
        ]
    babies = [Baby.from_dict(descriptor) for descriptor in babies_descriptors]
    display_dashboard(babies)
else:
    display_login(encrypted_urls)
