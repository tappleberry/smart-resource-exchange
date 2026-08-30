from ai.matching import generate_match_result


def main():

    lost_report = {
        "category": "Backpack",
        "ai_color": "black",
        "ai_object": "backpack",
        "ai_type": "college backpack",
        "ai_features": [
            "front pocket"
        ],
        "location": "Library",
        "reported_at": "2026-08-29 10:00:00"
    }

    found_report = {
        "category": "Bottle",
        "ai_color": "blue",
        "ai_object": "water bottle",
        "ai_type": "plastic bottle",
        "ai_features": [
            "cap"
        ],
        "location": "Hostel",
        "reported_at": "2026-08-29 10:00:00"
    }

    result = generate_match_result(
        lost_report,
        found_report
    )

    print("Mismatch Test")
    print("-------------")
    print("Score :", result["score"])
    print("Level :", result["match_level"])

    print(
        "Category :",
        result["category_score"]
    )

    print(
        "Color    :",
        result["color_score"]
    )

    print(
        "Description :",
        result["description_score"]
    )

    print(
        "Location :",
        result["location_score"]
    )

    print(
        "Time     :",
        result["time_score"]
    )


if __name__ == "__main__":
    main()