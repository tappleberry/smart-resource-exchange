from ml.recommend import generate_recommendation


# ==================================================
# Test 1 - No data
# ==================================================

def test_no_data():

    result = generate_recommendation(
        category="Books",
        demand_score=0,
        listings=0,
        exam_days=30
    )

    assert result["recommendation_level"] == "LOW"
    assert result["recommended"] is False

    print("No data: PASS")


# ==================================================
# Test 2 - High demand + low supply
# ==================================================

def test_high_demand_low_supply():

    result = generate_recommendation(
        category="Electronics",
        demand_score=75,
        listings=4,
        exam_days=5
    )

    assert result["recommendation_level"] == "HIGH PRIORITY"
    assert result["recommended"] is True

    print(
        "High demand + low supply: PASS"
    )


# ==================================================
# Test 3 - High demand + high supply
# ==================================================

def test_high_demand_high_supply():

    result = generate_recommendation(
        category="Furniture",
        demand_score=80,
        listings=10,
        exam_days=20
    )

    assert result["recommendation_level"] == "MODERATE"
    assert result["recommended"] is False

    print(
        "High demand + high supply: PASS"
    )


# ==================================================
# Test 4 - Low demand
# ==================================================

def test_low_demand():

    result = generate_recommendation(
        category="Cycles",
        demand_score=25,
        listings=8,
        exam_days=20
    )

    assert result["recommendation_level"] == "LOW"
    assert result["recommended"] is False

    print("Low demand: PASS")


# ==================================================
# Test 5 - Borderline demand
# ==================================================

def test_borderline_demand():

    result = generate_recommendation(
        category="Lab Equipment",
        demand_score=42,
        listings=3,
        exam_days=12
    )

    assert result["recommendation_level"] == "MODERATE"
    assert result["recommended"] is False

    print("Borderline demand: PASS")


# ==================================================
# Test 6 - Exam proximity
# ==================================================

def test_exam_proximity():

    result = generate_recommendation(
        category="Hostel Essentials",
        demand_score=65,
        listings=3,
        exam_days=6
    )

    assert (
        "Exam period is approaching."
        in result["message"]
    )

    print("Exam proximity: PASS")


# ==================================================
# Run all tests
# ==================================================

def main():

    print(
        "Recommendation Reliability Tests"
    )

    print(
        "================================="
    )

    test_no_data()

    test_high_demand_low_supply()

    test_high_demand_high_supply()

    test_low_demand()

    test_borderline_demand()

    test_exam_proximity()

    print(
        "\nAll recommendation reliability "
        "tests passed!"
    )


if __name__ == "__main__":
    main()