import random

weather_states = [
    "dry",
    "cloudy",
    "light_rain",
    "heavy_rain"
]

def generate_weather():

    probabilities = {
        "dry": 0.60,
        "cloudy": 0.25,
        "light_rain": 0.10,
        "heavy_rain": 0.05
    }

    rand = random.random()
    cumulative = 0

    for weather, prob in probabilities.items():
        cumulative += prob

        if rand <= cumulative:
            return weather

    return "dry"


def weather_lap_time_penalty(weather):

    penalties = {
        "dry": 0,
        "cloudy": 0.2,
        "light_rain": 4,
        "heavy_rain": 8
    }

    return penalties[weather]