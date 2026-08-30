import csv
import random
from datetime import date, timedelta


# ==================================================
# Configuration
# ==================================================

OUTPUT_PATH = "data/demand_synthetic.csv"

CATEGORIES = [
    "Electronics",
    "Books",
    "Cycles",
    "Hostel Essentials",
    "Lab Equipment",
    "Furniture",
    "Clothing",
    "Sports Equipment"
]

NUMBER_OF_DAYS = 15

START_DATE = date(
    2026,
    8,
    1
)


# ==================================================
# Category Profiles
# ==================================================

CATEGORY_PROFILES = {
    "Electronics": {
        "base_searches": 42,
        "base_views": 65,
        "base_favorites": 13,
        "base_listings": 5,
        "exam_effect": 1.15
    },

    "Books": {
        "base_searches": 30,
        "base_views": 50,
        "base_favorites": 10,
        "base_listings": 12,
        "exam_effect": 1.20
    },

    "Cycles": {
        "base_searches": 18,
        "base_views": 32,
        "base_favorites": 7,
        "base_listings": 6,
        "exam_effect": 0.85
    },

    "Hostel Essentials": {
        "base_searches": 35,
        "base_views": 55,
        "base_favorites": 11,
        "base_listings": 7,
        "exam_effect": 0.95
    },

    "Lab Equipment": {
        "base_searches": 22,
        "base_views": 38,
        "base_favorites": 8,
        "base_listings": 6,
        "exam_effect": 1.10
    },

    "Furniture": {
        "base_searches": 17,
        "base_views": 30,
        "base_favorites": 6,
        "base_listings": 8,
        "exam_effect": 0.90
    },

    "Clothing": {
        "base_searches": 28,
        "base_views": 45,
        "base_favorites": 9,
        "base_listings": 10,
        "exam_effect": 0.80
    },

    "Sports Equipment": {
        "base_searches": 24,
        "base_views": 40,
        "base_favorites": 8,
        "base_listings": 5,
        "exam_effect": 0.88
    }
}


# ==================================================
# Helpers
# ==================================================

def clamp(
    value,
    minimum,
    maximum
):
    """
    Keep value within a fixed range.
    """

    return max(
        minimum,
        min(value, maximum)
    )


def calculate_demand(
    searches,
    views,
    favorites,
    listings,
    exam_days,
    category_effect
):
    """
    Generate a realistic synthetic demand score.

    Higher searches/views/favorites increase demand.
    More listings reduce demand.
    Exam proximity affects categories differently.
    """

    engagement = (
        searches * 0.45
        + views * 0.25
        + favorites * 1.5
    )

    supply_penalty = listings * 1.8

    exam_bonus = (
        max(0, 30 - exam_days)
        * category_effect
    )

    noise = random.uniform(
        -5,
        5
    )

    demand = (
        engagement
        + exam_bonus
        - supply_penalty
        + noise
    )

    return round(
        clamp(
            demand,
            0,
            100
        ),
        2
    )


# ==================================================
# Generate One Row
# ==================================================

def generate_row(
    current_date,
    category
):
    """
    Generate one synthetic observation.
    """

    profile = CATEGORY_PROFILES[
        category
    ]

    # ----------------------------------------------
    # Weekly-style activity variation
    # ----------------------------------------------

    day_variation = random.uniform(
        0.80,
        1.20
    )

    searches = max(
        1,
        round(
            profile["base_searches"]
            * day_variation
            + random.randint(-5, 5)
        )
    )

    views = max(
        1,
        round(
            profile["base_views"]
            * day_variation
            + random.randint(-7, 7)
        )
    )

    favorites = max(
        0,
        round(
            profile["base_favorites"]
            * day_variation
            + random.randint(-2, 2)
        )
    )

    listings = max(
        1,
        round(
            profile["base_listings"]
            + random.randint(-2, 2)
        )
    )

    # ----------------------------------------------
    # Exam days
    # ----------------------------------------------

    exam_days = random.randint(
        0,
        30
    )

    # ----------------------------------------------
    # Demand target
    # ----------------------------------------------

    demand = calculate_demand(
        searches=searches,
        views=views,
        favorites=favorites,
        listings=listings,
        exam_days=exam_days,
        category_effect=profile["exam_effect"]
    )

    return {
        "date": current_date.isoformat(),
        "category": category,
        "searches": searches,
        "views": views,
        "favorites": favorites,
        "listings": listings,
        "exam_days": exam_days,
        "demand": demand
    }


# ==================================================
# Generate Dataset
# ==================================================

def generate_dataset():

    random.seed(
        42
    )

    rows = []

    for day_index in range(
        NUMBER_OF_DAYS
    ):

        current_date = (
            START_DATE
            + timedelta(
                days=day_index
            )
        )

        for category in CATEGORIES:

            rows.append(
                generate_row(
                    current_date,
                    category
                )
            )

    return rows


# ==================================================
# Save Dataset
# ==================================================

def save_dataset(rows):

    fieldnames = [
        "date",
        "category",
        "searches",
        "views",
        "favorites",
        "listings",
        "exam_days",
        "demand"
    ]

    with open(
        OUTPUT_PATH,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        writer.writerows(
            rows
        )


# ==================================================
# Main
# ==================================================

def main():

    rows = generate_dataset()

    save_dataset(
        rows
    )

    print(
        "Synthetic demand dataset generated successfully!"
    )

    print(
        "Rows:",
        len(rows)
    )

    print(
        "Output:",
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()
    