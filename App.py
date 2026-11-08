
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import pearsonr, spearmanr


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
        # STELLAR MASS DISTRIBUTION
        # =====================================

        st.divider()

        st.subheader("✦ Stellar Mass Distribution")

        st.write(
            "Examine the distribution of estimated stellar masses "
            "among the matched exoplanet-host stars."
        )

        # Remove records without stellar mass estimates
        mass_data = stellar_data.dropna(subset=["st_mass"]).copy()

        fig_mass = px.histogram(
            mass_data,
            x="st_mass",
            nbins=30,
            labels={
                "st_mass": "Stellar Mass (Solar Masses)",
                "count": "Number of Stars"
            },
            title="Distribution of Stellar Masses",
            color_discrete_sequence=["#9B72CF"]
        )

        # Approximate core-collapse threshold
        fig_mass.add_vline(
            x=8,
            line_dash="dash",
            line_color="#FF6B6B",
            line_width=2,
            annotation_text="Approx. 8 Solar Masses",
            annotation_position="top right"
        )

        fig_mass.update_layout(
            template="plotly_dark",
            height=500,
            xaxis_title="Stellar Mass (Solar Masses)",
            yaxis_title="Number of Stars",
            margin=dict(l=40, r=40, t=70, b=40)
        )

        st.plotly_chart(
            fig_mass,
            use_container_width=True
        )

        # Summary statistics
        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Stars with Mass Estimates",
            f"{len(mass_data):,}"
        )

        col2.metric(
            "Average Stellar Mass",
            f"{mass_data['st_mass'].mean():.2f} M☉"
        )

        col3.metric(
            "Maximum Recorded Mass",
            f"{mass_data['st_mass'].max():.2f} M☉"
        )

        st.caption(
            "The dashed line represents the approximate 8-solar-mass "
            "initial-mass threshold commonly associated with core-collapse "
            "supernovae. The available values are host-star mass estimates, "
            "not necessarily their initial masses."
        )

        # =====================================
        # STELLAR MASS VS STELLAR AGE
        # =====================================

        st.divider()

        st.subheader("✦ Stellar Mass vs. Stellar Age")

        st.write(
            "Explore how stellar mass relates to the estimated age "
            "of exoplanet-host stars."
        )

        # Keep only stars with both mass and age measurements
        mass_age_data = stellar_data.dropna(
            subset=["st_mass", "st_age"]
        ).copy()

        fig_mass_age = px.scatter(
            mass_age_data,
            x="st_mass",
            y="st_age",
            color="mh_gspphot",
            hover_data=[
                "source_id",
                "st_teff",
                "st_rad"
            ],
            color_continuous_scale="Plasma",
            labels={
                "st_mass": "Stellar Mass (Solar Masses)",
                "st_age": "Stellar Age (Gyr)",
                "mh_gspphot": "Metallicity (dex)",
                "source_id": "Gaia Source ID",
                "st_teff": "Effective Temperature (K)",
                "st_rad": "Stellar Radius (Solar Radii)"
            },
            title="Stellar Mass vs. Stellar Age"
        )

        fig_mass_age.update_layout(
            template="plotly_dark",
            height=550,
            margin=dict(l=40, r=40, t=70, b=40)
        )

        st.plotly_chart(
            fig_mass_age,
            use_container_width=True
        )

        st.caption(
            f"Showing {len(mass_age_data):,} host stars with "
            "available mass and age measurements. "
            "Age estimates are unavailable for some stars."
        )

        # =====================================
        # STELLAR METALLICITY VS STELLAR MASS
        # =====================================

        st.divider()

        st.subheader("✦ Stellar Metallicity vs. Stellar Mass")

        st.write(
            "Investigate the relationship between stellar metallicity "
            "and estimated stellar mass."
        )

        # Keep records with both measurements
        metallicity_data = stellar_data.dropna(
            subset=["mh_gspphot", "st_mass"]
        ).copy()

        fig_metallicity = px.scatter(
            metallicity_data,
            x="mh_gspphot",
            y="st_mass",
            color="st_age",
            hover_data=[
                "source_id",
                "st_teff"
            ],
            trendline="ols",
            color_continuous_scale="Plasma",
            labels={
                "mh_gspphot": "Metallicity (dex)",
                "st_mass": "Stellar Mass (Solar Masses)",
                "st_age": "Stellar Age (Gyr)",
                "source_id": "Gaia Source ID",
                "st_teff": "Effective Temperature (K)"
            },
            title="Stellar Metallicity vs. Stellar Mass"
        )

        fig_metallicity.update_layout(
            template="plotly_dark",
            height=550,
            margin=dict(l=40, r=40, t=70, b=40)
        )

        st.plotly_chart(
            fig_metallicity,
            use_container_width=True
        )

        st.caption(
            f"Showing {len(metallicity_data):,} host stars with "
            "available metallicity and mass measurements. "
            "The dashed trendline represents an ordinary least-squares "
            "linear regression."
        )

# =====================================
# 6. EXOPLANET ANALYSIS
# =====================================

elif page == "Exoplanet Analysis":

            st.subheader("Stellar Mass vs Exoplanet Radius")

            planet_data = combined_data.dropna(
                subset=["st_mass", "pl_rade", "mh_gspphot"]
            ).copy()

            fig_planet = px.scatter(
                planet_data,
                x="st_mass",
                y="pl_rade",
                color="mh_gspphot",
                hover_data=[
                    "pl_name",
                    "st_age",
                    "pl_orbper"
                ],
                color_continuous_scale="Plasma",
                labels={
                    "st_mass": "Host Star Mass (Solar Masses)",
                    "pl_rade": "Planet Radius (Earth Radii)",
                    "mh_gspphot": "Host Star Metallicity (dex)",
                    "pl_name": "Planet Name",
                    "st_age": "Host Star Age (Gyr)",
                    "pl_orbper": "Orbital Period (Days)"
                },
                title="Host Star Mass vs. Exoplanet Radius"
            )

            fig_planet.update_layout(
                template="plotly_dark",
                height=600,
                margin=dict(l=40, r=40, t=70, b=40)
            )

            st.plotly_chart(fig_planet, use_container_width=True)

            st.caption(
                f"Showing {len(planet_data):,} planets with available "
                "host star mass, planet radius, and metallicity measurements. "
                "Each point represents one confirmed exoplanet."
            )

            st.divider()

            st.subheader("Exoplanet and Host Star Properties")

            # Prepare data for the additional notebook analyses
            analysis_data = combined_data.dropna(
                subset=["mh_gspphot", "pl_rade"]
            ).copy()

            st.write(
                f"Records available for analysis: "
                f"{len(analysis_data):,}"
            )

            st.subheader("Host Star Metallicity Distribution")

            fig_metallicity = px.histogram(
                analysis_data,
                x="mh_gspphot",
                nbins=30,
                labels={
                    "mh_gspphot": "Stellar Metallicity (dex)",
                    "count": "Number of Exoplanets"
                },
                title="Distribution of Host Star Metallicity"
            )

            fig_metallicity.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                fig_metallicity,
                use_container_width=True
            )

            st.subheader("Exoplanet Radius Distribution")

            fig_radius = px.histogram(
                analysis_data,
                x="pl_rade",
                nbins=30,
                labels={
                    "pl_rade": "Planet Radius (Earth Radii)",
                    "count": "Number of Exoplanets"
                },
                title="Distribution of Confirmed Exoplanet Radii"
            )

            fig_radius.update_layout(
                template="plotly_dark",
                height=500
            )

            st.plotly_chart(
                fig_radius,
                use_container_width=True
            )

            st.subheader("Stellar Metallicity vs. Exoplanet Radius")

            fig_correlation = px.scatter(
                analysis_data,
                x="mh_gspphot",
                y="pl_rade",
                trendline="ols",
                hover_data=[
                    "pl_name",
                    "st_mass",
                    "st_age"
                ],
                labels={
                    "mh_gspphot": "Host Star Metallicity (dex)",
                    "pl_rade": "Exoplanet Radius (Earth Radii)",
                    "pl_name": "Planet Name",
                    "st_mass": "Host Star Mass (Solar Masses)",
                    "st_age": "Host Star Age (Gyr)"
                },
                title="Host Star Metallicity vs. Exoplanet Radius"
            )

            fig_correlation.update_layout(
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(
                fig_correlation,
                use_container_width=True
            )

            st.divider()

            st.subheader("Correlation Analysis")

            # Calculate correlation coefficients
            pearson_corr, pearson_p = pearsonr(
                analysis_data["mh_gspphot"],
                analysis_data["pl_rade"]
            )

            spearman_corr, spearman_p = spearmanr(
                analysis_data["mh_gspphot"],
                analysis_data["pl_rade"]
            )

            # Display correlation results
            col1, col2 = st.columns(2)

            with col1:
                st.metric(
                    "Pearson Correlation",
                    f"{pearson_corr:.4f}"
                )

                st.caption(
                    f"P-value: {pearson_p:.6f}"
                )

            with col2:
                st.metric(
                    "Spearman Correlation",
                    f"{spearman_corr:.4f}"
                )

                st.caption(
                    f"P-value: {spearman_p:.8f}"
                )

# =====================================
# 7. SUPERNOVA REMNANTS
# =====================================

elif page == "Supernova Remnants":

    st.header("Supernova Remnant Explorer")

    if snrds is not None:

        # Prepare Gaia star coordinates
        gaia_coordinates = starsds.dropna(
            subset=["l", "b"]
        ).copy()

        # Prepare Supernova Remnant coordinates
        snr_coordinates = snrds.dropna(
            subset=["lii", "bii"]
        ).copy()

        # Plot both datasets
        fig = px.scatter(
            gaia_coordinates,
            x="l",
            y="b",
            hover_name="source_id",
            labels={
                "l": "Galactic Longitude",
                "b": "Galactic Latitude"
            },
            title="Galactic Distribution of Gaia Stars and Supernova Remnants"
        )

        # Add Supernova Remnants
        fig.add_scatter(
            x=snr_coordinates["lii"],
            y=snr_coordinates["bii"],
            mode="markers",
            name="Supernova Remnants",
            marker=dict(
                symbol="x",
                size=9
            ),
            text=snr_coordinates["Name"]
            if "Name" in snr_coordinates.columns
            else None,
            hovertemplate=(
                "Supernova Remnant: %{text}<br>"
                "Longitude: %{x}<br>"
                "Latitude: %{y}"
                "<extra></extra>"
            )
        )

        fig.update_layout(
            template="plotly_dark",
            height=600,
            xaxis_title="Galactic Longitude (degrees)",
            yaxis_title="Galactic Latitude (degrees)",
            legend_title="Dataset"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Gaia stars are shown as circles, while known supernova "
            "remnants are shown as crosses. Overlapping sky positions "
            "do not necessarily indicate a physical association."
        )

        st.divider()

        st.subheader("Potential Supernova Candidates")

        # Filter potential high-mass supernova progenitors
        supernova_candidates = stellar_data[
            stellar_data["st_mass"] >= 8
        ].dropna(
            subset=["st_mass", "st_age", "teff_gspphot"]
        )

        if not supernova_candidates.empty:

            fig_candidates = px.scatter(
                supernova_candidates,
                x="st_mass",
                y="st_age",
                color="teff_gspphot",
                hover_data=[
                    "source_id",
                    "logg_gspphot",
                    "mh_gspphot"
                ],
                title="Potential High-Mass Supernova Progenitors",
                labels={
                    "st_mass": "Stellar Mass (Solar Masses)",
                    "st_age": "Stellar Age (Gyr)",
                    "teff_gspphot": "Stellar Temperature (K)"
                }
            )

            fig_candidates.update_layout(
                template="plotly_dark",
                height=600
            )

            st.plotly_chart(
                fig_candidates,
                use_container_width=True
            )

        else:

            st.info(
                "No potential supernova candidates were identified "
                "using the current stellar mass threshold of 8 solar masses."
            )

            st.caption(
                "The available Gaia host-star sample contains no "
                "stars meeting this selection criterion."
            )

    else:
        st.info("MOST-SNRcat dataset is unavailable.")

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
