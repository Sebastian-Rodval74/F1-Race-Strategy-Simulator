import random

def update_gap(current_gap, pace_delta):

    noise = random.uniform(-0.3, 0.3)

    new_gap = current_gap - pace_delta + noise

    return max(0.2, new_gap)


def rival_pace():

    return random.uniform(79.5, 81.5)


def traffic_penalty(gap):

    if gap < 1:
        return 0.5

    if gap < 2:
        return 0.2

    return 0