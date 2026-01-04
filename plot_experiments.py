import pandas as pd
import matplotlib.pyplot as plt

# Load experiment results
df = pd.read_csv("experiment_multitrack_tyre_sensitivity.csv")

# Separate by track
tracks = df["track"].unique()
tyres = df["tyre"].unique()

for tyre in tyres:
    plt.figure()

    for track in tracks:
        subset = df[
            (df["tyre"] == tyre) &
            (df["track"] == track)
        ].sort_values("lap_in_stint")

        plt.plot(
            subset["lap_in_stint"],
            subset["lap_time_s"],
            marker="o",
            label=track
        )

    plt.xlabel("Lap in stint")
    plt.ylabel("Lap time (s)")
    plt.title(f"Tyre degradation comparison – {tyre}")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"tyre_degradation_{tyre}.png", dpi=150)
    plt.close()