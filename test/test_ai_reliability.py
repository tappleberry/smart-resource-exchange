import json

from ai.lost_found import (
    get_unknown_lost_found_result,
    validate_lost_found_result,
    build_search_text,
)


# ==================================================
# Test 1 - Unknown fallback
# ==================================================

def test_unknown_fallback():

    result = get_unknown_lost_found_result()

    assert result["object"] == "Unknown"
    assert result["color"] == "Unknown"
    assert result["type"] == "Unknown"
    assert result["features"] == []

    print("Unknown fallback: PASS")


# ==================================================
# Test 2 - Empty / incomplete result
# ==================================================

def test_incomplete_result():

    result = validate_lost_found_result({})

    assert result["object"] == "Unknown"
    assert result["color"] == "Unknown"
    assert result["type"] == "Unknown"
    assert result["features"] == []

    print("Incomplete AI result: PASS")


# ==================================================
# Test 3 - Invalid feature format
# ==================================================

def test_invalid_features():

    result = validate_lost_found_result({
        "object": "Backpack",
        "color": "Black",
        "type": "College Backpack",
        "features": "front pocket"
    })

    assert result["object"] == "Backpack"
    assert result["color"] == "Black"
    assert result["type"] == "College Backpack"

    assert result["features"] == []

    print("Invalid feature format: PASS")


# ==================================================
# Test 4 - Empty feature values
# ==================================================

def test_empty_features():

    result = validate_lost_found_result({
        "object": "",
        "color": "",
        "type": "",
        "features": [
            "",
            "   ",
            "zipper"
        ]
    })

    assert result["object"] == "Unknown"
    assert result["color"] == "Unknown"
    assert result["type"] == "Unknown"

    assert result["features"] == [
        "zipper"
    ]

    print("Empty values: PASS")


# ==================================================
# Test 5 - Search text generation
# ==================================================

def test_search_text():

    result = {
        "object": "Backpack",
        "color": "Black",
        "type": "College Backpack",
        "features": [
            "front pocket",
            "zipper"
        ]
    }

    search_text = build_search_text(
        result
    )

    expected_words = [
        "Backpack",
        "Black",
        "College Backpack",
        "front pocket",
        "zipper"
    ]

    for word in expected_words:

        assert word in search_text

    print("Search text generation: PASS")


# ==================================================
# Run all tests
# ==================================================

def main():

    print(
        "AI Reliability Tests"
    )

    print(
        "===================="
    )

    test_unknown_fallback()
    test_incomplete_result()
    test_invalid_features()
    test_empty_features()
    test_search_text()

    print(
        "\nAll AI reliability tests passed!"
    )


if __name__ == "__main__":
    main()