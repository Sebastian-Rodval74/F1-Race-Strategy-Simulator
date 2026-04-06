import pandas as pd
from Lap_time_model import calculate_lap_time
from race_simulation import simulate_strategy
import matplotlib.pyplot as plt

def main():
    print("Running strategy experiments...")
    tracks =pd.read_csv("tracks.csv")
    cars = pd.read_csv("cars.csv")
    tyres = pd.read_csv("tyres.csv")

    track = tracks[tracks["TRACK"] == "Monza"].iloc[0].to_dict()
    car = cars[cars["team"] == "RedBull"].iloc[0].to_dict()

    tyre_dict = {
        row["compound"]: row.to_dict()
        for _, row in tyres.iterrows()
    }

    soft = tyre_dict["SOFT"]
    medium = tyre_dict["MEDIUM"]
    hard = tyre_dict["HARD"]

    strategies = {
        "S-M-H": [
            {"tyre": soft, "laps": 15},
            {"tyre": medium, "laps": 25},
            {"tyre": hard, "laps": 13}
        ],
        "M-H": [
            {"tyre": medium, "laps": 30},
            {"tyre": hard, "laps": 23}
        ],
        "S-H": [
            {"tyre": soft, "laps": 20},
            {"tyre": hard, "laps": 33}
        ]
    }

    results = []

    for name, strategy in strategies.items():
        total_time = simulate_strategy(
            track=track,
            car=car,
            setup="low",
            strategy=strategy,
            lap_time_func=calculate_lap_time
        )

        results.append({
            "strategy": name,
            "track": track["TRACK"],
            "total_time_s": round(total_time, 2),
            "num_pits": len(strategy) - 1
        })

    results_df = pd.DataFrame(results)
    best_time = results_df["total_time_s"].min()
    results_df["gap_to_best"] = (results_df["total_time_s"] - best_time).round(2)
    print(results_df)

    results_df.to_csv("strategy_comparison.csv", index=False)

    # Detect best strategy automatically
    best_strategy_name = results_df.loc[
        results_df["total_time_s"].idxmin(),
        "strategy"
    ]

    best_strategy = strategies[best_strategy_name]

    print(f"\n--- OPTIMIZING BEST STRATEGY: {best_strategy_name} ---")

    # Only optimize if it has 2 stints (1 pit stop)
    if len(best_strategy) == 2:

        total_laps = track["LAPS"]
        optimization_results = []

        for first_stint in range(10, total_laps - 10):
            second_stint = total_laps - first_stint

            strategy = [
                {"tyre": best_strategy[0]["tyre"], "laps": first_stint},
                {"tyre": best_strategy[1]["tyre"], "laps": second_stint}
            ]

            import random

            simulations = 50
            sim_times = []

            for _ in range(simulations):

                total_time = 0.0
                safety_car_lap = random.randint(5, total_laps - 5)
                safety_car_duration = 3

                current_lap = 0

                for stint_idx, stint in enumerate(strategy):
                    for lap in range(1, stint["laps"] + 1):
                        current_lap += 1

                        lap_time = calculate_lap_time(
                            track=track,
                            car=car,
                            setup="low",
                            tyre=stint["tyre"],
                            lap_in_stint=lap
                        )

                        if safety_car_lap <= current_lap < safety_car_lap + safety_car_duration:
                            lap_time *= 1.4

                        total_time += lap_time

                    if stint_idx < len(strategy) - 1:
                        if safety_car_lap <= current_lap < safety_car_lap + safety_car_duration:
                            total_time += 12.0
                        else:
                            total_time += 22.0

                sim_times.append(total_time)

            import numpy as np

            total_time = sum(sim_times) / len(sim_times)
            std_dev = np.std(sim_times)

            optimization_results.append({
                "pit_lap": first_stint,
                "avg_time_s": round(total_time, 2),
                "min_time_s": round(min(sim_times), 2),
                "max_time_s": round(max(sim_times), 2),
                "std_dev": round(std_dev, 2)
            })

        opt_df = pd.DataFrame(optimization_results)
        best_time_opt = opt_df["avg_time_s"].min()
        opt_df["gap_to_best"] = (opt_df["avg_time_s"] - best_time_opt).round(2)

        print(opt_df.sort_values("avg_time_s").head(10))

        plt.figure()

        # Mean curve
        plt.plot(opt_df["pit_lap"], opt_df["avg_time_s"])

        # Uncertainty band (min-max)
        plt.fill_between(
            opt_df["pit_lap"],
            opt_df["min_time_s"],
            opt_df["max_time_s"],
            alpha=0.2
        )

        # Encontrar el punto óptimo
        min_idx = opt_df["avg_time_s"].idxmin()
        min_pit = opt_df.loc[min_idx, "pit_lap"]
        min_time = opt_df.loc[min_idx, "avg_time_s"]

        # Marcar el punto óptimo
        plt.scatter(min_pit, min_time)
        plt.text(min_pit, min_time, f"  Opt: Lap {int(min_pit)}")

        plt.xlabel("Pit Lap")
        plt.ylabel("Total Race Time (s)")
        plt.title(f"Monte Carlo Pit Optimization - {best_strategy_name} ({track['TRACK']})")
        plt.tight_layout()
        plt.savefig(f"{best_strategy_name}_pit_uncertainty.png", dpi=150)
        plt.close()

        opt_df.to_csv(f"{best_strategy_name}_pit_optimization.csv", index=False)

    else:
        print("Optimization currently only supported for 2-stint strategies.")

if __name__ == "__main__":
    main()