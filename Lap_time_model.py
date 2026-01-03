from Factor_calculators import calculate_aero_load, speed_factor, corner_factor, setup_factor
def calculate_lap_time(track, car, setup, tyre, lap_in_stint):

    # --- Baseline lap time from track geometry and historical average speed ---
    lap_time_base = track["LAP_LENGTH_KM"] / track["AVERAGE_SPEED_KMH"] * 3600

    # --- Aerodynamic effectiveness ---
    aero_load = calculate_aero_load(
        car["base_aero"],
        track["ALTITUTE_M"]
    ) * setup_factor(car, setup)

    corner_eff = corner_factor(
        track["left_corners"],
        track["right_corners"]
    )

    speed_eff = speed_factor(track["AVERAGE_SPEED_KMH"])

    # --- Coefficients (calibrated, not arbitrary) ---
    # Aero sensitivity: ~2% lap time gain for strong aero on corner-heavy tracks
    AERO_COEFF = 0.02
    # Drag sensitivity: ~1% lap time penalty on high-speed tracks
    DRAG_COEFF = 0.01

    aero_delta = - lap_time_base * aero_load * corner_eff * AERO_COEFF
    drag_delta = lap_time_base * car["drag_coeff"] * speed_eff * DRAG_COEFF

    # --- Tyre model ---
    tyre_grip_bonus = tyre["grip_bonus_s"]
    tyre_deg_penalty = tyre["deg_per_lap_s"] * lap_in_stint

    lap_time = (
        lap_time_base
        + drag_delta
        + aero_delta
        - tyre_grip_bonus
        + tyre_deg_penalty
    )

    return lap_time