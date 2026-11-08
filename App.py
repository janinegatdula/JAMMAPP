
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================
# 1. PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Star Explorer",
    page_icon="🌌",
    layout="wide"
)

st.title("🌌 Star Explorer")
st.caption("Stellar Data Analysis and Evolution Exploration")

# =====================================
# 2. DATASET UPLOADS
# =====================================

st.sidebar.header("Dataset Management")

gaia_file = st.sidebar.file_uploader(
    "Upload Gaia DR3 Dataset",
    type=["csv"]
)

planet_file = st.sidebar.file_uploader(
    "Upload NASA Exoplanet Dataset",
    type=["csv"]
)

snr_file = st.sidebar.file_uploader(
    "Upload MOST-SNRcat Dataset",
    type=["csv"]
)

starsds = pd.read_csv(gaia_file) if gaia_file else None
exoplanetds = pd.read_csv(planet_file) if planet_file else None
snrds = pd.read_csv(snr_file) if snr_file else None

# =====================================
# 3. NAVIGATION
# =====================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Home",
        "Gaia Star Explorer",
        "Exoplanet Analysis",
        "Supernova Remnants",
        "Stellar Evolution Simulator"
    ]
)

# =====================================
# 4. HOME DASHBOARD
# =====================================

if page == "Home":

    st.header("Astronomical Research Dashboard")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Gaia Stars",
        len(starsds) if starsds is not None else "Not loaded"
    )

    col2.metric(
        "Exoplanet Records",
        len(exoplanetds) if exoplanetds is not None else "Not loaded"
    )

    col3.metric(
        "Supernova Remnants",
        len(snrds) if snrds is not None else "Not loaded"
    )

    st.subheader("Research Objective")

    st.write("""
    Investigate relationships between stellar properties,
    exoplanet characteristics, and supernova remnants.

    Explore possible stellar evolutionary outcomes using
    stellar evolution models.
    """)

# =====================================
# 5. GAIA STAR EXPLORER
# =====================================

elif page == "Gaia Star Explorer":

    st.header("Gaia Stellar Properties")

    if starsds is not None:

        st.dataframe(starsds, use_container_width=True)

        st.subheader("Hertzsprung-Russell Diagram")

        required = ["teff_gspphot", "abs_g_mag"]

        if all(c in starsds.columns for c in required):

            plot_data = starsds.dropna(subset=required)

            fig = px.scatter(
                plot_data,
                x="teff_gspphot",
                y="abs_g_mag",
                color="mh_gspphot"
                if "mh_gspphot" in plot_data.columns
                else None,
                hover_data=["source_id"]
                if "source_id" in plot_data.columns
                else None,
                labels={
                    "teff_gspphot": "Temperature (K)",
                    "abs_g_mag": "Absolute G Magnitude",
                    "mh_gspphot": "Metallicity"
                },
                title="Stellar Distribution"
            )

            fig.update_xaxes(autorange="reversed")
            fig.update_yaxes(autorange="reversed")

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload your Gaia dataset to begin.")

# =====================================
# 6. EXOPLANET ANALYSIS
# =====================================

elif page == "Exoplanet Analysis":

    st.header("Exoplanet Correlations")

    if exoplanetds is not None:

        st.dataframe(exoplanetds, use_container_width=True)

        st.subheader("Planet Radius vs Orbital Period")

        if all(c in exoplanetds.columns
               for c in ["pl_rade", "pl_orbper"]):

            fig = px.scatter(
                exoplanetds.dropna(
                    subset=["pl_rade", "pl_orbper"]
                ),
                x="pl_orbper",
                y="pl_rade",
                hover_name="pl_name"
                if "pl_name" in exoplanetds.columns
                else None,
                labels={
                    "pl_orbper": "Orbital Period (days)",
                    "pl_rade": "Planet Radius (Earth radii)"
                }
            )

            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Host Star Properties")

        if all(c in exoplanetds.columns
               for c in ["st_mass", "st_age"]):

            fig = px.scatter(
                exoplanetds.dropna(
                    subset=["st_mass", "st_age"]
                ),
                x="st_mass",
                y="st_age",
                labels={
                    "st_mass": "Stellar Mass (Solar Masses)",
                    "st_age": "Stellar Age"
                }
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload your NASA Exoplanet dataset.")

# =====================================
# 7. SUPERNOVA REMNANTS
# =====================================

elif page == "Supernova Remnants":

    st.header("Supernova Remnant Explorer")

    if snrds is not None:

        st.dataframe(snrds, use_container_width=True)

        if all(c in snrds.columns for c in ["Lii", "bii"]):

            fig = px.scatter(
                snrds.dropna(subset=["Lii", "bii"]),
                x="Lii",
                y="bii",
                hover_name="Name" if "Name" in snrds.columns else None,
                title="Galactic Distribution of Supernova Remnants",
                labels={
                    "Lii": "Galactic Longitude",
                    "bii": "Galactic Latitude"
                }
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.info("Upload your MOST-SNRcat dataset.")

# =====================================
# 8. STELLAR EVOLUTION SIMULATOR
# =====================================

elif page == "Stellar Evolution Simulator":

    st.header("Stellar Evolution Simulator")

    st.write(
        "Explore possible stellar evolutionary outcomes "
        "based on initial stellar properties."
    )

    mass = st.slider(
        "Initial Stellar Mass (Solar Masses)",
        0.1, 50.0, 1.0, 0.1
    )

    metallicity = st.slider(
        "Metallicity [Fe/H]",
        -2.5, 0.5, 0.0, 0.1
    )

    age = st.number_input(
        "Current Stellar Age (Gyr)",
        min_value=0.0,
        max_value=13.8,
        value=1.0
    )

    # Simplified main-sequence approximation
    lifetime = 10 * (mass ** -2.5)

    st.subheader("Estimated Results")

    col1, col2 = st.columns(2)

    col1.metric(
        "Approx. Main-Sequence Lifetime",
        f"{lifetime:.3f} Gyr"
    )

    remaining = max(0, lifetime - age)

    col2.metric(
        "Approx. Main-Sequence Time Remaining",
        f"{remaining:.3f} Gyr"
    )

    if age < lifetime:
        stage = "Approximately Main Sequence"
    else:
        stage = "Possibly Post-Main-Sequence"

    if mass < 8:
        outcome = "Likely White Dwarf"
    elif mass < 25:
        outcome = "Core-Collapse Candidate"
    else:
        outcome = "Black Hole Formation Possible"

    st.divider()

    st.write("**Estimated Evolutionary Stage:**", stage)

    st.write("**Possible Final Outcome:**", outcome)

    st.warning(
        "This is a simplified educational estimate, "
        "not a calibrated stellar evolution model. "
        "Metallicity is not yet incorporated into the "
        "lifetime calculation. MIST/PARSEC tracks are "
        "needed for more reliable evolutionary estimates."
    )
