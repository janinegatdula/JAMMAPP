from astroquery.gaia import Gaia
import pandas as pd

job = Gaia.launch_job_async("""
    SELECT gs.source_id, gs.ra, gs.dec, gs.parallax,
           gs.phot_g_mean_mag, gs.bp_rp,
           ap.distance_gspphot, ap.teff_gspphot,
           ap.mass_flame, ap.age_flame, ap.evolstage_flame
    FROM gaiadr3.gaia_source AS gs
    JOIN gaiadr3.astrophysical_parameters AS ap
      ON gs.source_id = ap.source_id
    WHERE gs.parallax > 3.2663
""")
df = job.get_results().to_pandas()
df.to_csv("gaia_1000ly.csv", index=False)