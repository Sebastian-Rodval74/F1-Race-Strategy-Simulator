import pandas as pd
import random

from models.lap_time_model import calculate_lap_time

from simulation.safety_car import check_safety_car
from simulation.overtakes import (
    overtake_probability,
    attempt_overtake
)
from simulation.weather import (
    generate_weather,
    weather_lap_time_penalty
)

# =========================
# LOAD DATA
# =========================

tracks = pd.read_csv("data/tracks.csv")
cars = pd.read_csv("data/cars.csv")
tyres = pd.read_csv("data/tyres.csv")

track = tracks.iloc[0].to_dict()
car = cars.iloc[0].to_dict()

tyre_dict = {
    row["compound"]: row.to_dict()
    for _, row in tyres.iterrows()
}

# =========================
# HELPERS
# =========================

def get_deg_rate(tyre):
    return tyre.get("deg_rate") or tyre.get("deg") or 0.03


def race_intro():
    position = random.randint(5, 15)

    print("\n🏁 GRAND PRIX START 🏁")
    print(f"Track: {track['TRACK']}")
    print(f"Laps: {track['LAPS']}")
    print(f"Starting Position: P{position}")
    print("Mission: fight through the field using strategy.\n")

    return position


def narrate_event(message, speaker="Crofty"):
    print(f"\n🎙️ {speaker}: {message}")


def print_status(
    lap,
    total_laps,
    tyre,
    deg,
    gap,
    position,
    weather
):
    print("\n==============================")
    print(f"Lap {lap}/{total_laps}")
    print(f"Position: P{position}")
    print(f"Tyre: {tyre}")
    print(f"Tyre Deg: {round(deg, 2)}")
    print(f"Gap Ahead: {round(gap, 2)}s")
    print(f"Weather: {weather}")
    print("==============================")


def compute_metrics(deg, gap, safety_car):
    undercut = "HIGH" if deg > 0.6 else "LOW"
    traffic = "HIGH" if gap < 1.5 else "LOW"
    sc = "YES" if safety_car else "NO"

    return undercut, traffic, sc


def recommend_action(deg, safety_car, gap):
    if safety_car:
        return "BOX NOW - FREE PIT STOP 🚨"

    if deg > 0.7:
        return "BOX NOW - TYRES GONE 🔥"

    if gap < 1.5:
        return "PUSH - OVERTAKE WINDOW OPEN"

    return "STAY OUT"


# =========================
# MAIN SIMULATION
# =========================

def simulate_race():

    total_laps = int(track["LAPS"])

    current_tyre = tyre_dict["MEDIUM"]
    tyre_name = "MEDIUM"

    lap_in_stint = 1

    total_time = 0.0

    position = race_intro()

    teammate_position = position - random.randint(1, 3)

    print(f"Your teammate starts P{teammate_position}")

    narrate_event(
        "And it's lights out and away we go!"
    )

    # WEATHER
    weather = generate_weather()

    if weather == "light_rain":
        narrate_event(
            "Light rain could become a factor later.",
            speaker="Brundle"
        )

    if weather == "heavy_rain":
        narrate_event(
            "Heavy rain conditions today. Strategy will be critical.",
            speaker="Brundle"
        )

    gap_ahead = random.uniform(1, 4)

    safety_car_active = False
    safety_car_remaining = 0

    decisions = []

    # =========================
    # RACE LOOP
    # =========================

    for lap in range(1, total_laps + 1):

        # =========================
        # SAFETY CAR CHECK
        # =========================

        if not safety_car_active:

            sc_event = check_safety_car(
                lap,
                total_laps
            )

            if sc_event["active"]:

                safety_car_active = True
                safety_car_remaining = sc_event["duration"]

                narrate_event(
                    "SAFETY CAR DEPLOYED!",
                    speaker="Crofty"
                )

        else:

            safety_car_remaining -= 1

            if safety_car_remaining <= 0:

                safety_car_active = False

                narrate_event(
                    "GREEN FLAG! Racing resumes!",
                    speaker="Crofty"
                )

        # =========================
        # RANDOM COMMENTARY
        # =========================

        if random.random() < 0.05:
            narrate_event(
                "A driver ahead has made a mistake!",
                speaker="Crofty"
            )

        if random.random() < 0.03:
            narrate_event(
                "Teams are watching the radar closely.",
                speaker="Brundle"
            )

        # =========================
        # TYRE DEGRADATION
        # =========================

        deg = get_deg_rate(current_tyre) * lap_in_stint

        # =========================
        # LAP TIME
        # =========================

        lap_time = calculate_lap_time(
            track=track,
            car=car,
            setup="low",
            tyre=current_tyre,
            lap_in_stint=lap_in_stint
        )

        # WEATHER EFFECT
        lap_time += weather_lap_time_penalty(weather)

        # SAFETY CAR EFFECT
        if safety_car_active:
            lap_time *= 1.4

        # =========================
        # DRIVING MODE
        # =========================

        driving_mode = "neutral"

        # =========================
        # METRICS
        # =========================

        undercut, traffic, sc = compute_metrics(
            deg,
            gap_ahead,
            safety_car_active
        )

        print_status(
            lap,
            total_laps,
            tyre_name,
            deg,
            gap_ahead,
            position,
            weather
        )

        print(
            f"Undercut: {undercut} | "
            f"Traffic: {traffic} | "
            f"SC: {sc}"
        )

        # =========================
        # ENGINEER
        # =========================

        recommendation = recommend_action(
            deg,
            safety_car_active,
            gap_ahead
        )

        narrate_event(
            recommendation,
            speaker="Engineer"
        )

        # =========================
        # BRUNDLE ANALYSIS
        # =========================

        if deg > 0.6:

            narrate_event(
                "Those tyres are starting to fall off the cliff.",
                speaker="Brundle"
            )

        elif gap_ahead < 1.5:

            narrate_event(
                "He's right in the dirty air now.",
                speaker="Brundle"
            )

        # =========================
        # TEAM ORDERS
        # =========================

        team_order = None

        if abs(position - teammate_position) <= 1:

            if random.random() < 0.25:

                team_order = random.choice([
                    "hold_position",
                    "let_teammate_pass"
                ])

                if team_order == "let_teammate_pass":

                    narrate_event(
                        "Team radio: let your teammate through.",
                        speaker="Engineer"
                    )

                else:

                    narrate_event(
                        "Hold position and manage the gap.",
                        speaker="Engineer"
                    )

        # =========================
        # PLAYER DECISION
        # =========================

        if (
            lap % 3 == 0
            or safety_car_active
            or deg > 0.7
        ):

            if team_order == "let_teammate_pass":

                user_input = input(
                    "\nDecision "
                    "(pit/stay/push/conserve/let pass): "
                ).strip().lower()

            else:

                user_input = input(
                    "\nDecision "
                    "(pit/stay/push/conserve): "
                ).strip().lower()

        else:

            user_input = "stay"

        if user_input in ["push", "conserve"]:

            driving_mode = user_input
            decision = "stay"

        else:

            decision = user_input

        decisions.append(decision)

        # =========================
        # TEAM ORDER EFFECT
        # =========================

        if (
            decision == "let pass"
            and team_order == "let_teammate_pass"
        ):

            position += 1

            narrate_event(
                "You let your teammate through.",
                speaker="Crofty"
            )

        # =========================
        # DRIVING MODE EFFECTS
        # =========================

        if driving_mode == "push":

            lap_time *= 0.98
            deg += 0.03

            narrate_event(
                "He's absolutely pushing now!",
                speaker="Crofty"
            )

        elif driving_mode == "conserve":

            lap_time *= 1.02
            deg -= 0.01

            narrate_event(
                "Managing tyres carefully.",
                speaker="Brundle"
            )

        # =========================
        # OVERTAKE SYSTEM
        # =========================

        tyre_advantage = max(0, 0.8 - deg)

        probability = overtake_probability(
            gap=gap_ahead,
            tyre_advantage=tyre_advantage,
            drs=(gap_ahead < 1),
            push_mode=(driving_mode == "push"),
            dirty_air=(gap_ahead < 2)
        )

        if attempt_overtake(probability):

            position -= 1

            narrate_event(
                "WHAT A MOVE! CLEAN OVERTAKE!",
                speaker="Crofty"
            )

            gap_ahead += 2

        else:

            gap_ahead += random.uniform(-0.4, 0.4)

        # =========================
        # PIT STOP
        # =========================

        if decision == "pit":

            narrate_event(
                "BOX BOX BOX!",
                speaker="Engineer"
            )

            total_time += (
                12.0
                if safety_car_active
                else 22.0
            )

            new_tyre = input(
                "Choose tyre "
                "(SOFT/MEDIUM/HARD): "
            ).strip().upper()

            current_tyre = tyre_dict[new_tyre]
            tyre_name = new_tyre

            lap_in_stint = 1

        else:

            lap_in_stint += 1

        # =========================
        # TOTAL TIME
        # =========================

        total_time += lap_time

    # =========================
    # RACE END
    # =========================

    narrate_event(
        "And that's the chequered flag!",
        speaker="Crofty"
    )

    print("\n🏁 RACE FINISHED 🏁")

    print(f"Final Position: P{position}")
    print(f"Total Time: {round(total_time, 2)}s")

    narrate_event(
        f"You finish P{position}. "
        "A dramatic race!",
        speaker="Crofty"
    )

    # =========================
    # SCORING
    # =========================

    score = 100

    score -= decisions.count("pit") * 2
    score -= position * 1.5

    print(
        f"\n📊 Strategy Score: "
        f"{round(score, 1)}/100"
    )


if __name__ == "__main__":
    simulate_race()