
def calculate_aero_load(base_aero, altitude_meters):
    alt_factor = 1 - (altitude_meters / 10000)
    return base_aero * alt_factor

def speed_factor(speed_kmh):
    speed_f = speed_kmh / 100
    return speed_f

def corner_factor(left, right):
    total_corners = left + right
    corner_bias = abs(left - right) / total_corners
    return corner_bias

def setup_factor(car, setup):
    if setup == "high":
        return car["high_df_eff"]
    elif setup == "low":
        return car["low_df_eff"]
    return 1.0