
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


# =====================================
# COSMIC VISUAL THEME
# =====================================

st.markdown("""
<style>

.stApp {
    background:
        radial-gradient(ellipse at 15% 15%, rgba(89, 45, 160, 0.25), transparent 40%),
        radial-gradient(ellipse at 85% 75%, rgba(25, 91, 180, 0.20), transparent 40%),
        linear-gradient(135deg, #070817, #11102B 55%, #080B1C);
    color: #F4F0FF;
}

.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #F4F0FF !important;
    font-weight: 700 !important;
}

[data-testid="stSidebar"] {
    background: #0B0A20;
    border-right: 1px solid rgba(153, 115, 255, 0.2);
}

[data-testid="stMetric"] {
    background: linear-gradient(
        145deg,
        rgba(49, 37, 91, 0.75),
        rgba(20, 29, 65, 0.75)
    );
    border: 1px solid rgba(153, 115, 255, 0.3);
    border-radius: 16px;
    padding: 20px;
}

[data-testid="stMetricValue"] {
    color: #AFA0FF;
}

.stButton > button {
    background: linear-gradient(90deg, #7046D8, #357BEA);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 0.5rem 1rem;
    transition: 0.3s ease;
}

.stButton > button:hover {
    box-shadow: 0 0 18px rgba(133, 92, 255, 0.55);
    border: none;
    transform: translateY(-2px);
}

hr {
    border-color: rgba(153, 115, 255, 0.2);
}

</style>
""", unsafe_allow_html=True)

# =====================================
# LOAD RESEARCH DATASETS
# =====================================

starsds = pd.read_csv("data/gaia_dr3_stars_within_500_light_years.csv", dtype={"source_id": str}) 
exoplanetds = pd.read_csv("data/nasa_exoplanet_archive_confirmed_planets.csv", dtype={"gaia_dr3_id": str}) 
snrds = pd.read_csv("data/SUPERNOVA_REMNANTS.csv", skiprows=1) 

# =====================================
# MATCH GAIA AND EXOPLANET DATA
# =====================================

# Clean Gaia source IDs
starsds["source_id"] = starsds["source_id"].str.strip()

# Remove the "Gaia DR3 " prefix from NASA Gaia IDs
exoplanetds["gaia_dr3_id"] = (
    exoplanetds["gaia_dr3_id"]
    .str.replace("Gaia DR3 ", "", regex=False)
    .str.strip()
)

# Match exoplanet records to their Gaia host stars
combined_data = exoplanetds.merge(
    starsds,
    left_on="gaia_dr3_id",
    right_on="source_id",
    how="inner",
    suffixes=("_planet", "_gaia")
)

# =====================================
# CREATE UNIQUE STELLAR DATASET
# =====================================

stellar_columns = [
    "st_mass",
    "st_age",
    "st_teff",
    "st_rad",
    "st_lum",
    "teff_gspphot",
    "logg_gspphot",
    "mh_gspphot",
    "abs_g_mag",
    "bp_rp",
    "distance_pc"
]

# One row per unique host star
stellar_data = (
    combined_data
    .groupby("source_id")[stellar_columns]
    .median()
    .reset_index()
)

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

    st.markdown("""
    <style>
    .hero {
        background: linear-gradient(120deg, #402477, #172D65);
        padding: 45px;
        border-radius: 20px;
        text-align: center;
        border: 1px solid rgba(170, 140, 255, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        '<div class="hero"><h1 style="color:white;">'
        'POSSIBLE FUTURE<br>EVOLUTION OF STARS'
        '</h1><p style="color:white;">'
        'Explore stellar properties and the mysteries of the cosmos.'
        '</p></div>',
        unsafe_allow_html=True
    )

    st.subheader("✦ Research Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "🌟 Gaia Stars",
        f"{len(starsds):,}" if starsds is not None else "Not loaded"
    )

    col2.metric(
        "🪐 Exoplanet Records",
        f"{len(exoplanetds):,}" if exoplanetds is not None else "Not loaded"
    )

    col3.metric(
        "💥 Supernova Remnants",
        f"{len(snrds):,}" if snrds is not None else "Not loaded"
    )

# =====================================
# 5. GAIA STAR EXPLORER
# =====================================

elif page == "Gaia Star Explorer":

    st.header("Gaia Stellar Properties")

    if starsds is not None:

        # =====================================
        # HERTZSPRUNG-RUSSELL DIAGRAM
        # =====================================

        st.subheader("✦ Hertzsprung–Russell Diagram")

        st.write(
            "Explore the relationship between stellar temperature "
            "and absolute magnitude, with metallicity represented by color."
        )

        # Keep only records with the required values
        hr_data = stellar_data.dropna(
            subset=["teff_gspphot", "abs_g_mag"]
        ).copy()

        fig_hr = px.scatter(
            hr_data,
            x="teff_gspphot",
            y="abs_g_mag",
            color="mh_gspphot",
            hover_data=[
                "source_id",
                "st_mass",
                "st_age"
            ],
            color_continuous_scale="Plasma",
            labels={
                "teff_gspphot": "Effective Temperature (K)",
                "abs_g_mag": "Absolute G Magnitude",
                "mh_gspphot": "Metallicity (dex)",
                "source_id": "Gaia Source ID",
                "st_mass": "Stellar Mass (Solar Masses)",
                "st_age": "Stellar Age (Gyr)"
            },
            title="Stellar Temperature vs Absolute Magnitude"
        )

        # Traditional astronomical HR diagram orientation
        fig_hr.update_xaxes(autorange="reversed")
        fig_hr.update_yaxes(autorange="reversed")

        fig_hr.update_layout(
            template="plotly_dark",
            height=650,
            coloraxis_colorbar=dict(
                title="Metallicity (dex)"
            ),
            margin=dict(l=40, r=40, t=70, b=40)
        )

        st.plotly_chart(
            fig_hr,
            use_container_width=True
        )

        st.caption(
            f"Showing {len(hr_data):,} matched host stars with "
            "available temperature and absolute magnitude measurements."
        )

# =====================================
# 6. EXOPLANET ANALYSIS
# =====================================

elif page == "Exoplanet Analysis":

    st.header("Exoplanet Correlations")

    if exoplanetds is not None:

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
