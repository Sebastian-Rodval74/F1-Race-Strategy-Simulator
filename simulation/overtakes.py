import random

def overtake_probability(
    gap,
    tyre_advantage,
    drs=True,
    push_mode=False,
    dirty_air=True
):

    probability = 0.0

    # Gap effect
    if gap < 1:
        probability += 0.35
    elif gap < 2:
        probability += 0.15

    # Tyre advantage
    probability += tyre_advantage * 0.2

    # DRS
    if drs:
        probability += 0.10

    # Push mode
    if push_mode:
        probability += 0.10

    # Dirty air penalty
    if dirty_air:
        probability -= 0.05

    return max(0, min(probability, 0.95))


def attempt_overtake(probability):

    return random.random() < probability