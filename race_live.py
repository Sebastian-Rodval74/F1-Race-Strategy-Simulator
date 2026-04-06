import pandas as pd
import random

from Lap_time_model import calculate_lap_time

# Load data
tracks = pd.read_csv("tracks.csv")
cars = pd.read_csv("cars.csv")
tyres = pd.read_csv("tyres.csv")

track = tracks.iloc[0].to_dict()
car = cars.iloc[0].to_dict()

tyre_dict = {row["compound"]: row.to_dict() for _, row in tyres.iterrows()}

def get_deg_rate(tyre):
    return tyre.get("deg_rate") or tyre.get("deg") or tyre.get("deg_factor", 0.03)

def race_intro():
    position = random.randint(5, 15)
    print("\n🏁 GRAND PRIX START 🏁")
    print(f"Track: {track['TRACK']}")
    print(f"Laps: {track['LAPS']}")
    print(f"You start in P{position}")
    print("Your mission: climb positions using strategy.\n")
    return position

def narrate_event(message, speaker="Crofty"):
    print(f"\n🎙️ {speaker}: {message}")

def print_status(lap, total_laps, tyre, deg, gap, position):
    print(f"\nLap {lap}/{total_laps} | Position: P{position}")
    print(f"Tyre: {tyre} | Deg: {round(deg,2)} | Gap ahead: {round(gap,2)}s")

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
        return "CONSIDER PIT - UNDERCUT WINDOW"
    return "STAY OUT"

def simulate_race():
    total_laps = int(track["LAPS"])
    current_tyre = tyre_dict["MEDIUM"]
    tyre_name = "MEDIUM"
    lap_in_stint = 1

    total_time = 0.0
    gap_ahead = random.uniform(1, 5)
    position = race_intro()
    teammate_position = position - random.randint(1, 3)
    print(f"Your teammate starts P{teammate_position}")
    narrate_event("And it's lights out and away we go!")

    safety_car_lap = random.randint(10, total_laps - 10)
    safety_car_active = False

    decisions = []

    for lap in range(1, total_laps + 1):

        if lap == safety_car_lap:
            safety_car_active = True
            print("\n🚨 SAFETY CAR DEPLOYED 🚨")

        if safety_car_active and lap > safety_car_lap + 3:
            safety_car_active = False
            print("\n🟢 GREEN FLAG 🟢")

        # Random events
        if random.random() < 0.05:
            narrate_event("A mistake from a driver ahead! Opportunity here!", speaker="Crofty")
        if random.random() < 0.03:
            narrate_event("Clouds are forming... could rain become a factor?", speaker="Brundle")

        deg = get_deg_rate(current_tyre) * lap_in_stint

        lap_time = calculate_lap_time(
            track=track,
            car=car,
            setup="low",
            tyre=current_tyre,
            lap_in_stint=lap_in_stint
        )

        if safety_car_active:
            lap_time *= 1.4

        total_time += lap_time
        gap_ahead += random.uniform(-0.5, 0.5)

        # position change simulation
        if gap_ahead < 1:
            position -= 1
            narrate_event("What a move! Up the inside, brilliant overtake!")
            gap_ahead += 2

        print_status(lap, total_laps, tyre_name, deg, gap_ahead, position)

        undercut, traffic, sc = compute_metrics(deg, gap_ahead, safety_car_active)
        print(f"Undercut: {undercut} | Traffic: {traffic} | SC: {sc}")

        rec = recommend_action(deg, safety_car_active, gap_ahead)
        narrate_event(f"{rec}", speaker="Engineer")
        if deg > 0.6:
            narrate_event("Those tyres are starting to fall off the cliff now.", speaker="Brundle")
        elif gap_ahead < 1.5:
            narrate_event("He's right in the dirty air, this could be a passing opportunity.", speaker="Brundle")

        team_order = None
        if abs(position - teammate_position) <= 1 and random.random() < 0.3:
            team_order = random.choice(["hold_position", "let_teammate_pass"])
            if team_order == "let_teammate_pass":
                narrate_event("Team radio: Let your teammate through, he's on a different strategy.")
            else:
                narrate_event("Team radio: Hold position, manage the gap.")

        # Driving mode system
        driving_mode = "neutral"

        # Only ask decision every 3 laps or critical moments
        if lap % 3 == 0 or safety_car_active or deg > 0.7:
            if team_order == "let_teammate_pass":
                user_input = input("Decision? (pit/stay/let pass/push/conserve): ").strip().lower()
            else:
                user_input = input("Decision? (pit/stay/push/conserve): ").strip().lower()
        else:
            user_input = "stay"

        if user_input in ["push", "conserve"]:
            driving_mode = user_input
            decision = "stay"
        else:
            decision = user_input

        decisions.append(decision)

        if decision == "let pass" and team_order == "let_teammate_pass":
            position += 1
            narrate_event("You let your teammate through. Team strategy in play.")

        if decision == "pit":
            print("🔧 BOX BOX BOX 🔧")
            total_time += 12.0 if safety_car_active else 22.0

            new_tyre = input("Choose tyre (soft/medium/hard): ").strip().upper()
            current_tyre = tyre_dict[new_tyre]
            tyre_name = new_tyre
            lap_in_stint = 1
        else:
            lap_in_stint += 1

        # Driving mode effects
        if driving_mode == "push":
            lap_time *= 0.98
            deg += 0.02
            narrate_event("He's pushing hard now, extracting everything from the car!", speaker="Crofty")
        elif driving_mode == "conserve":
            lap_time *= 1.02
            deg -= 0.01
            narrate_event("Managing tyres carefully, thinking long-term strategy.", speaker="Brundle")

    narrate_event("And that’s the chequered flag! What a race!")
    print("\n🏁 RACE FINISHED 🏁")
    print(f"Final Position: P{position}")
    narrate_event(f"You finish P{position}. A race full of strategy and drama!")
    print(f"Total Time: {round(total_time,2)}s")

    # Scoring system
    score = 100
    score -= decisions.count("pit") * 2
    score -= position * 1.5

    print(f"\n📊 Strategy Score: {round(score,1)}/100")

if __name__ == "__main__":
    simulate_race()