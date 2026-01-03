import pandas as pd
from Lap_time_model import calculate_lap_time

tracks = pd.read_csv("tracks.csv")
cars = pd.read_csv("cars.csv")
tyres = pd.read_csv("tyres.csv")

# Select tracks for comparison (ensure these exist in tracks.csv)
track_names = ["Monza", "Interlagos"]
selected_tracks = tracks[tracks["TRACK"].isin(track_names)]

car = cars[cars["team"] == "RedBull"].iloc[0].to_dict()
setups = ["low"]
laps_to_test = [1, 10, 20]

results = []

for _, track_row in selected_tracks.iterrows():
    track = track_row.to_dict()

    for _, tyre_row in tyres.iterrows():
        tyre = tyre_row.to_dict()

        for lap in laps_to_test:
            lap_time = calculate_lap_time(
                track=track,
                car=car,
                setup="low",
                tyre=tyre,
                lap_in_stint=lap
            )

            results.append({
                "track": track["TRACK"],
                "team": car["team"],
                "setup": "low",
                "tyre": tyre["compound"],
                "lap_in_stint": lap,
                "lap_time_s": round(lap_time, 3)
            })
        
results_df = pd.DataFrame(results)
print(results_df)
results_df.to_csv(
    "experiment_multitrack_tyre_sensitivity.csv",
    index=False
)