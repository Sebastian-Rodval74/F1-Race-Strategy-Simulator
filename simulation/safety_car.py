import random

def check_safety_car(lap, total_laps):
    probability = 0.03

    if lap < 5:
        probability += 0.05

    if random.random() < probability:
        duration = random.randint(2, 5)

        return {
            "active": True,
            "duration": duration
        }

    return {
        "active": False,
        "duration": 0
    }