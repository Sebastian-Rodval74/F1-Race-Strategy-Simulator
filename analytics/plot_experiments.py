PIT_TIME_BASE = 22.0  # seconds, average pit stop loss


def simulate_stint(track, car, setup, tyre, stint_length, lap_time_func):
    """
    Simulates a single stint with a given tyre.
    Returns total stint time in seconds.
    """
    stint_time = 0.0

    for lap in range(1, stint_length + 1):
        lap_time = lap_time_func(
            track=track,
            car=car,
            setup=setup,
            tyre=tyre,
            lap_in_stint=lap
        )
        stint_time += lap_time

    return stint_time


def simulate_strategy(track, car, setup, strategy, lap_time_func):
    """
    Simulates a full race strategy composed of multiple stints.
    Strategy format:
    [
        {"tyre": tyre_dict, "laps": int},
        ...
    ]
    """
    total_time = 0.0

    for i, stint in enumerate(strategy):
        total_time += simulate_stint(
            track=track,
            car=car,
            setup=setup,
            tyre=stint["tyre"],
            stint_length=stint["laps"],
            lap_time_func=lap_time_func
        )

        # Add pit stop time after every stint except the last
        if i < len(strategy) - 1:
            total_time += PIT_TIME_BASE

    return total_time