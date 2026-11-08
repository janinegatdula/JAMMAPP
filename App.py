
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy.stats import pearsonr, spearmanr
import textwrap
import streamlit.components.v1 as components

def evaluate_supernova_candidate(
    initial_mass=None,
    mass_uncertainty=None
):
    threshold = 8.0

    if initial_mass is None:
        return {
            "result": "Insufficient Information",
            "reason": "Initial stellar mass is unavailable."
        }

    if mass_uncertainty is not None:

        lower_mass = initial_mass - mass_uncertainty
        upper_mass = initial_mass + mass_uncertainty

        if lower_mass >= threshold:
            return {
                "result": "Potential Candidate",
                "reason": (
                    "The estimated initial mass, including "
                    "uncertainty, meets the threshold."
                )
            }

        elif upper_mass < threshold:
            return {
                "result": "Mass Criterion Not Met",
                "reason": (
                    "The estimated initial mass, including "
                    "uncertainty, is below the threshold."
                )
            }

        else:
            return {
                "result": "Uncertain",
                "reason": (
                    "The measurement uncertainty overlaps "
                    "the 8 solar mass threshold."
                )
            }

    if initial_mass >= threshold:
        return {
            "result": "Potential Candidate",
            "reason": (
                "The initial stellar mass meets the "
                "approximate 8 solar mass threshold."
            )
        }

    return {
        "result": "Mass Criterion Not Met",
        "reason": (
            "The initial stellar mass is below "
            "the approximate threshold."
        )
    }

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

# =====================================
# SPACE-THEMED SIDEBAR NAVIGATION
# =====================================

# Store the currently selected page
if "selected_page" not in st.session_state:
    st.session_state.selected_page = "Home"

# Sidebar styling
st.sidebar.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background: linear-gradient(
            180deg,
            #080d20 0%,
            #111a35 100%
        );
    }

    [data-testid="stSidebar"] h1 {
        color: #dceaff;
    }

    </style>
""", unsafe_allow_html=True)

st.sidebar.title("🌌 STAR EXPLORER")
st.sidebar.caption("YOUR JOURNEY THROUGH THE COSMOS")

st.sidebar.divider()

# Navigation buttons
if st.sidebar.button(
    "🌍  Home",
    use_container_width=True,
    type="primary" if st.session_state.selected_page == "Home" else "secondary"
):
    st.session_state.selected_page = "Home"

if st.sidebar.button(
    "🔭  Gaia Star Explorer",
    use_container_width=True,
    type="primary" if st.session_state.selected_page == "Gaia Star Explorer" else "secondary"
):
    st.session_state.selected_page = "Gaia Star Explorer"

if st.sidebar.button(
    "🪐  Exoplanet Analysis",
    use_container_width=True,
    type="primary" if st.session_state.selected_page == "Exoplanet Analysis" else "secondary"
):
    st.session_state.selected_page = "Exoplanet Analysis"

if st.sidebar.button(
    "💥  Supernova Remnants",
    use_container_width=True,
    type="primary" if st.session_state.selected_page == "Supernova Remnants" else "secondary"
):
    st.session_state.selected_page = "Supernova Remnants"

if st.sidebar.button(
    "✨  Stellar Evolution Simulator",
    use_container_width=True,
    type="primary" if st.session_state.selected_page == "Stellar Evolution Simulator" else "secondary"
):
    st.session_state.selected_page = "Stellar Evolution Simulator"

# Current page used by the existing app
page = st.session_state.selected_page



# =====================================
# SELECTED PAGE ANIMATION
# =====================================

if page == "Home":

    components.html(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    margin: 0;
                    background: transparent;
                    overflow: hidden;
                }

                .space-scene {
                    position: relative;
                    height: 155px;
                    width: 100%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                }

                .planet {
                    position: absolute;
                    width: 75px;
                    height: 75px;
                    border-radius: 50%;
                    background: radial-gradient(
                        circle at 30% 30%,
                        #b8e7ff,
                        #5689dc 45%,
                        #242b75 85%
                    );
                    box-shadow: 0 0 25px #659dff;
                    animation: glow 3s ease-in-out infinite alternate;
                }

                .orbit {
                    position: absolute;
                    width: 125px;
                    height: 125px;
                    border: 1px solid rgba(150, 190, 255, 0.5);
                    border-radius: 50%;
                }

                .moon-orbit {
                    position: absolute;
                    width: 125px;
                    height: 125px;
                    animation: rotate 5s linear infinite;
                }

                .moon {
                    position: absolute;
                    top: -5px;
                    left: 50%;
                    width: 15px;
                    height: 15px;
                    border-radius: 50%;
                    background: #e5eaff;
                    box-shadow: 0 0 12px #a8caff;
                }

                .star {
                    position: absolute;
                    color: white;
                    animation: twinkle 2s ease-in-out infinite alternate;
                }

                .star1 {
                    top: 20px;
                    left: 15%;
                }

                .star2 {
                    bottom: 20px;
                    right: 15%;
                    animation-delay: 1s;
                }

                .star3 {
                    top: 35px;
                    right: 20%;
                    animation-delay: 0.5s;
                }

                @keyframes rotate {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }

                @keyframes glow {
                    from { box-shadow: 0 0 15px #659dff; }
                    to { box-shadow: 0 0 35px #659dff, 0 0 50px #4266c5; }
                }

                @keyframes twinkle {
                    from { opacity: 0.3; }
                    to { opacity: 1; }
                }
            </style>
        </head>

        <body>
            <div class="space-scene">
                <span class="star star1">✦</span>
                <span class="star star2">✧</span>
                <span class="star star3">✦</span>

                <div class="orbit"></div>
                <div class="planet"></div>

                <div class="moon-orbit">
                    <div class="moon"></div>
                </div>
            </div>
        </body>
        </html>
        """,
        height=160,
        scrolling=False
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

    # Get the actual dataset counts
    gaia_count = len(starsds) if starsds is not None else -1
    exoplanet_count = len(exoplanetds) if exoplanetds is not None else -1
    snr_count = len(snrds) if snrds is not None else -1

    # Animated statistics cards
    counter_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {
                margin: 0;
                background: transparent;
                font-family: Arial, sans-serif;
            }

            .stats-container {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 14px;
                padding: 5px;
            }

            .stat-card {
                background: linear-gradient(145deg, #17264b, #10172f);
                border: 1px solid rgba(115, 160, 255, 0.35);
                border-radius: 14px;
                padding: 22px 10px;
                text-align: center;
                box-shadow: 0 0 15px rgba(65, 105, 225, 0.12);
            }

            .stat-title {
                color: #b9d5ff;
                font-size: 13px;
                font-weight: bold;
                margin-bottom: 15px;
            }

            .stat-number {
                color: #78bdff;
                font-size: 30px;
                font-weight: bold;
                text-shadow: 0 0 12px rgba(80, 160, 255, 0.5);
            }

            .stat-description {
                color: #8499c4;
                font-size: 11px;
                margin-top: 8px;
            }

            @media (max-width: 500px) {
                .stats-container {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>

    <body>

        <div class="stats-container">

            <div class="stat-card">
                <div class="stat-title">🌟 Gaia Stars</div>
                <div class="stat-number" data-target="__GAIA__">0</div>
                <div class="stat-description">Stars in dataset</div>
            </div>

            <div class="stat-card">
                <div class="stat-title">🪐 Exoplanet Records</div>
                <div class="stat-number" data-target="__EXOPLANETS__">0</div>
                <div class="stat-description">Planet records</div>
            </div>

            <div class="stat-card">
                <div class="stat-title">💥 Supernova Remnants</div>
                <div class="stat-number" data-target="__SNR__">0</div>
                <div class="stat-description">Remnants in dataset</div>
            </div>

        </div>

        <script>
            const counters = document.querySelectorAll(".stat-number");

            counters.forEach(counter => {
                const target = Number(counter.dataset.target);

                if (target < 0) {
                    counter.textContent = "Not loaded";
                    return;
                }

                const duration = 1800;
                const startTime = performance.now();

                function updateCounter(currentTime) {
                    const progress = Math.min(
                        (currentTime - startTime) / duration,
                        1
                    );

                    // Smooth count-up animation
                    const easedProgress = 1 - Math.pow(1 - progress, 3);

                    const currentValue = Math.floor(
                        easedProgress * target
                    );

                    counter.textContent = currentValue.toLocaleString();

                    if (progress < 1) {
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target.toLocaleString();
                    }
                }

                requestAnimationFrame(updateCounter);
            });
        </script>

    </body>
    </html>
    """

    counter_html = (
        counter_html
        .replace("__GAIA__", str(gaia_count))
        .replace("__EXOPLANETS__", str(exoplanet_count))
        .replace("__SNR__", str(snr_count))
    )

    components.html(
        counter_html,
        height=155,
        scrolling=False
    )


# =====================================
# 5. GAIA STAR EXPLORER
# =====================================

elif page == "Gaia Star Explorer":

    st.header("Gaia Stellar Properties")

    # Interactive Plotly chart settings
    chart_config = {
        "displayModeBar": True,
        "displaylogo": False,
        "scrollZoom": True,
        "modeBarButtonsToAdd": ["select2d", "lasso2d"]
    }

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
            use_container_width=True,
            config=chart_config
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
            use_container_width=True,
            config=chart_config
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

        # Divide stars into six age groups
        mass_age_data["age_group"] = pd.qcut(
            mass_age_data["st_age"],
            q=6,
            labels=False,
            duplicates="drop"
        )

        # Prepare cumulative animation frames
        animation_frames = []
        age_labels = []

        age_groups = sorted(mass_age_data["age_group"].dropna().unique())

        for group in age_groups:

            # Get the maximum age reached in this frame
            max_age = mass_age_data.loc[
                mass_age_data["age_group"] == group,
                "st_age"
            ].max()

            frame_label = f"Up to {max_age:.1f} Gyr"
            age_labels.append(frame_label)

            # Reveal all stars up to the current age group
            frame_data = mass_age_data[
                mass_age_data["age_group"] <= group
            ].copy()

            frame_data["age_progression"] = frame_label

            animation_frames.append(frame_data)

        animated_mass_age = pd.concat(
            animation_frames,
            ignore_index=True
        )

        fig_mass_age = px.scatter(
            animated_mass_age,
            x="st_mass",
            y="st_age",
            color="mh_gspphot",
            animation_frame="age_progression",
            animation_group="source_id",
            hover_data=[
                "source_id",
                "st_teff",
                "st_rad"
            ],
            color_continuous_scale="Plasma",
            category_orders={
                "age_progression": age_labels
            },
            range_x=[
                mass_age_data["st_mass"].min() * 0.95,
                mass_age_data["st_mass"].max() * 1.05
            ],
            range_y=[
                mass_age_data["st_age"].min() * 0.95,
                mass_age_data["st_age"].max() * 1.05
            ],
            labels={
                "st_mass": "Stellar Mass (Solar Masses)",
                "st_age": "Stellar Age (Gyr)",
                "mh_gspphot": "Metallicity (dex)",
                "source_id": "Gaia Source ID",
                "st_teff": "Effective Temperature (K)",
                "st_rad": "Stellar Radius (Solar Radii)",
                "age_progression": "Age Progression"
            },
            title="Stellar Mass vs. Stellar Age — Animated Age Progression"
        )

        fig_mass_age.update_layout(
            template="plotly_dark",
            height=600,
            transition=dict(
                duration=500,
                easing="cubic-in-out"
            ),
            margin=dict(l=40, r=40, t=70, b=40)
        )

        st.plotly_chart(
            fig_mass_age,
            use_container_width=True,
            config=chart_config
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
            use_container_width=True,
            config=chart_config
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

    st.header("Supernova Progenitor Screening")

    st.write(
        "Evaluate whether a star has characteristics "
        "associated with a potential core-collapse supernova progenitor."
    )

    st.info(
        "This is a rule-based screening tool using an approximate "
        "initial mass threshold of 8 solar masses."
    )

    # =====================================
    # MANUAL STAR EVALUATION
    # =====================================

    st.subheader("Manual Star Evaluation")

    st.write(
        "Enter the available stellar properties below."
    )

    with st.form("manual_star_form"):

        initial_mass = st.number_input(
            "Initial Stellar Mass (Solar Masses)",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=0.1,
            help="Enter 0 if the initial mass is unknown."
        )

        mass_uncertainty = st.number_input(
            "Mass Uncertainty (Solar Masses)",
            min_value=0.0,
            max_value=50.0,
            value=0.0,
            step=0.1
        )

        st.caption(
            "Optional properties for additional stellar context:"
        )

        current_mass = st.number_input(
            "Current Stellar Mass (Solar Masses)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        age = st.number_input(
            "Stellar Age (Gyr)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        temperature = st.number_input(
            "Stellar Temperature (K)",
            min_value=0.0,
            value=0.0,
            step=100.0
        )

        radius = st.number_input(
            "Stellar Radius (Solar Radii)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        luminosity = st.number_input(
            "Stellar Luminosity (Solar Luminosities)",
            min_value=0.0,
            value=0.0,
            step=0.1
        )

        metallicity = st.number_input(
            "Metallicity [Fe/H]",
            min_value=-5.0,
            max_value=2.0,
            value=0.0,
            step=0.1
        )

        submitted = st.form_submit_button(
            "Evaluate Star"
        )

    # Manual evaluation happens OUTSIDE the form

    if submitted:

        # Treat zero as unknown for initial mass
        evaluated_mass = (
            initial_mass if initial_mass > 0 else None
        )

        evaluated_uncertainty = (
            mass_uncertainty if mass_uncertainty > 0 else None
        )

        result = evaluate_supernova_candidate(
            initial_mass=evaluated_mass,
            mass_uncertainty=evaluated_uncertainty
        )

        st.divider()

        st.subheader("Screening Results")

        st.metric(
            "Evaluation",
            result["result"]
        )

        st.write("**Reason:**", result["reason"])

        st.caption(
            "This is an approximate screening result, "
            "not a prediction or guarantee of a supernova."
        )

    # =====================================
    # DATABASE MODE
    # =====================================

    st.divider()

    st.subheader("Database Mode")

    st.write(
        "Search for an existing star using its Gaia DR3 source ID."
    )

    gaia_id = st.text_input(
        "Gaia DR3 Source ID",
        placeholder="Enter a Gaia source ID..."
    )

    search_star = st.button("Search Star")

    if search_star:

        if gaia_id.strip() == "":
            st.warning("Please enter a Gaia source ID.")

        else:

            star_match = starsds[
                starsds["source_id"].astype(str).str.strip()
                == gaia_id.strip()
            ]

            if not star_match.empty:

                star = star_match.iloc[0]

                st.success("Star found in the Gaia dataset!")

                st.subheader("Retrieved Stellar Properties")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Temperature",
                        f"{star['teff_gspphot']:,.0f} K"
                        if pd.notna(star["teff_gspphot"])
                        else "Unavailable"
                    )

                with col2:
                    st.metric(
                        "Metallicity",
                        f"{star['mh_gspphot']:.2f} dex"
                        if pd.notna(star['mh_gspphot'])
                        else "Unavailable"
                    )

                with col3:
                    st.metric(
                        "Surface Gravity",
                        f"{star['logg_gspphot']:.2f}"
                        if pd.notna(star['logg_gspphot'])
                        else "Unavailable"
                    )

                st.write(
                    "**Gaia Source ID:**",
                    star["source_id"]
                )

                st.write(
                    "**Distance:**",
                    f"{star['distance_pc']:.2f} parsecs"
                    if pd.notna(star['distance_pc'])
                    else "Unavailable"
                )

                st.divider()

                st.subheader("Supernova Progenitor Screening")

                database_result = evaluate_supernova_candidate(
                    initial_mass=None
                )

                st.warning(database_result["result"])

                st.write(
                    "**Reason:**",
                    database_result["reason"]
                )

                st.caption(
                    "The Gaia dataset does not provide initial stellar "
                    "mass. Therefore, this star cannot be evaluated "
                    "against the 8-solar-mass screening threshold."
                )

            else:

                st.error(
                    "No star with that Gaia source ID was found."
                )
