from difflib import SequenceMatcher
from datetime import datetime
import json


# ==================================================
# Matching Weights
# ==================================================

CATEGORY_WEIGHT = 30
COLOR_WEIGHT = 20
DESCRIPTION_WEIGHT = 30
LOCATION_WEIGHT = 10
TIME_WEIGHT = 10


# ==================================================
# Text Normalization
# ==================================================

def normalize_text(value):
    """
    Convert a value into normalized lowercase text.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


# ==================================================
# Text Similarity
# ==================================================

def text_similarity(text1, text2):
    """
    Calculate similarity between two text values.

    Returns:
        float:
            Value between 0.0 and 1.0
    """

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    if text1 == text2:
        return 1.0

    return SequenceMatcher(
        None,
        text1,
        text2
    ).ratio()


# ==================================================
# Category Matching
# ==================================================

def category_similarity(category1, category2):
    """
    Compare report categories.

    Returns:
        float:
            1.0 if categories match,
            0.0 otherwise.
    """

    category1 = normalize_text(category1)
    category2 = normalize_text(category2)

    if not category1 or not category2:
        return 0.0

    return 1.0 if category1 == category2 else 0.0


# ==================================================
# Color Matching
# ==================================================

def color_similarity(color1, color2):
    """
    Compare item colors.

    Supports:
        - exact matches
        - combined colors such as red/black
        - partial textual similarity
    """

    color1 = normalize_text(color1)
    color2 = normalize_text(color2)

    if not color1 or not color2:
        return 0.0

    if color1 == color2:
        return 1.0

    colors1 = {
        part.strip()
        for part in color1.replace(",", "/").split("/")
        if part.strip()
    }

    colors2 = {
        part.strip()
        for part in color2.replace(",", "/").split("/")
        if part.strip()
    }

    if colors1.intersection(colors2):
        return 0.7

    return text_similarity(
        color1,
        color2
    )


# ==================================================
# Description Matching
# ==================================================

def description_similarity(description1, description2):
    """
    Compare two descriptions using text similarity.
    """

    return text_similarity(
        description1,
        description2
    )


# ==================================================
# Location Matching
# ==================================================

def location_similarity(location1, location2):
    """
    Compare lost/found report locations.
    """

    location1 = normalize_text(location1)
    location2 = normalize_text(location2)

    if not location1 or not location2:
        return 0.0

    if location1 == location2:
        return 1.0

    return text_similarity(
        location1,
        location2
    )


# ==================================================
# Time Parsing
# ==================================================

def parse_datetime(value):
    """
    Convert a datetime value into a datetime object.

    Supports:
        - datetime objects
        - SQLite timestamp strings
        - ISO-like timestamp strings
    """

    if isinstance(value, datetime):
        return value

    if not value:
        return None

    value = str(value).strip()

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%Y-%m-%dT%H:%M:%S"
    ]

    for fmt in formats:

        try:
            return datetime.strptime(
                value,
                fmt
            )
        except ValueError:
            continue

    return None


# ==================================================
# Time Matching
# ==================================================

def time_similarity(time1, time2):
    """
    Compare report timestamps.

    Returns:
        float:
            Value between 0.0 and 1.0
    """

    dt1 = parse_datetime(time1)
    dt2 = parse_datetime(time2)

    if dt1 is None or dt2 is None:
        return 0.0

    difference_days = abs(
        (dt1 - dt2).total_seconds()
    ) / 86400

    if difference_days <= 1:
        return 1.0

    if difference_days <= 3:
        return 0.8

    if difference_days <= 7:
        return 0.5

    if difference_days <= 14:
        return 0.2

    return 0.0


# ==================================================
# Safe Value Extraction
# ==================================================

def get_value(report, *keys):
    """
    Safely retrieve the first available value from:

        - dictionaries
        - sqlite3.Row objects
        - normal Python objects

    Returns:
        The value if found, otherwise None.
    """

    if report is None:
        return None

    for key in keys:

        # ------------------------------------------
        # sqlite3.Row / dictionary with keys()
        # ------------------------------------------

        try:
            if hasattr(report, "keys"):

                available_keys = report.keys()

                if key in available_keys:
                    return report[key]

        except (TypeError, AttributeError, KeyError):
            pass

        # ------------------------------------------
        # Dictionary-like access
        # ------------------------------------------

        try:
            return report[key]

        except (TypeError, KeyError, IndexError):
            pass

        # ------------------------------------------
        # Normal object attribute access
        # ------------------------------------------

        try:
            value = getattr(
                report,
                key
            )

            if value is not None:
                return value

        except AttributeError:
            pass

    return None


# ==================================================
# AI Features Parsing
# ==================================================

def parse_ai_features(value):
    """
    Convert stored AI features into a Python list.

    Database stores ai_features as JSON text.
    """

    if not value:
        return []

    # Already a list
    if isinstance(value, list):
        return [
            str(feature).strip()
            for feature in value
            if str(feature).strip()
        ]

    # JSON string
    if isinstance(value, str):

        try:
            parsed = json.loads(value)

            if isinstance(parsed, list):
                return [
                    str(feature).strip()
                    for feature in parsed
                    if str(feature).strip()
                ]

        except json.JSONDecodeError:
            pass

    return [str(value).strip()]


# ==================================================
# Build Searchable Description
# ==================================================

def build_report_description(report):
    """
    Build a searchable text representation from
    normal report fields and AI-extracted fields.

    AI fields supported:

        ai_object
        ai_type
        ai_features
    """

    parts = []

    # ----------------------------------------------
    # Existing database fields
    # ----------------------------------------------

    title = get_value(
        report,
        "title"
    )

    description = get_value(
        report,
        "description"
    )

    parts.append(title)
    parts.append(description)

    # ----------------------------------------------
    # AI object
    # ----------------------------------------------

    object_name = get_value(
        report,
        "ai_object",
        "object"
    )

    # ----------------------------------------------
    # AI type
    # ----------------------------------------------

    item_type = get_value(
        report,
        "ai_type",
        "type"
    )

    parts.append(object_name)
    parts.append(item_type)

    # ----------------------------------------------
    # AI features
    # ----------------------------------------------

    features = get_value(
        report,
        "ai_features",
        "features"
    )

    features = parse_ai_features(features)

    parts.extend(features)

    # ----------------------------------------------
    # Clean and combine
    # ----------------------------------------------

    return " ".join(
        str(part)
        for part in parts
        if part and normalize_text(part) != "unknown"
    ).strip()


# ==================================================
# Get Report Color
# ==================================================

def get_report_color(report):
    """
    Get color from AI-extracted database field.

    Falls back to normal 'color' field for
    backward compatibility.
    """

    return get_value(
        report,
        "ai_color",
        "color"
    )


# ==================================================
# Calculate Match Score
# ==================================================

def calculate_match_score(lost_report, found_report):
    """
    Calculate similarity between a lost report
    and a found report.

    Weight distribution:

        Category     -> 30%
        Color        -> 20%
        Description  -> 30%
        Location     -> 10%
        Time         -> 10%

    Returns:
        Dictionary containing final score and
        individual component scores.
    """

    # ----------------------------------------------
    # Category
    # ----------------------------------------------

    lost_category = get_value(
        lost_report,
        "category"
    )

    found_category = get_value(
        found_report,
        "category"
    )

    category_score = category_similarity(
        lost_category,
        found_category
    )

    # ----------------------------------------------
    # Color
    # ----------------------------------------------

    lost_color = get_report_color(
        lost_report
    )

    found_color = get_report_color(
        found_report
    )

    color_score = color_similarity(
        lost_color,
        found_color
    )

    # ----------------------------------------------
    # Description + AI attributes
    # ----------------------------------------------

    lost_description = build_report_description(
        lost_report
    )

    found_description = build_report_description(
        found_report
    )

    description_score = description_similarity(
        lost_description,
        found_description
    )

    # ----------------------------------------------
    # Location
    # ----------------------------------------------

    lost_location = get_value(
        lost_report,
        "location"
    )

    found_location = get_value(
        found_report,
        "location"
    )

    location_score = location_similarity(
        lost_location,
        found_location
    )

    # ----------------------------------------------
    # Time
    # ----------------------------------------------

    lost_time = get_value(
        lost_report,
        "reported_at",
        "created_at"
    )

    found_time = get_value(
        found_report,
        "reported_at",
        "created_at"
    )

    time_score = time_similarity(
        lost_time,
        found_time
    )

    # ----------------------------------------------
    # Weighted total
    # ----------------------------------------------

    total_score = (
        category_score * CATEGORY_WEIGHT
        + color_score * COLOR_WEIGHT
        + description_score * DESCRIPTION_WEIGHT
        + location_score * LOCATION_WEIGHT
        + time_score * TIME_WEIGHT
    )

    return {
        "score": round(
            total_score,
            2
        ),
        "category_score": round(
            category_score * 100,
            2
        ),
        "color_score": round(
            color_score * 100,
            2
        ),
        "description_score": round(
            description_score * 100,
            2
        ),
        "location_score": round(
            location_score * 100,
            2
        ),
        "time_score": round(
            time_score * 100,
            2
        )
    }


# ==================================================
# Match Level
# ==================================================

def get_match_level(score):
    """
    Convert numerical score into a match level.
    """

    if score >= 80:
        return "HIGH"

    if score >= 60:
        return "MEDIUM"

    return "LOW"


# ==================================================
# Generate Complete Match Result
# ==================================================

def generate_match_result(lost_report, found_report):
    """
    Generate complete matching information.
    """

    result = calculate_match_score(
        lost_report,
        found_report
    )

    result["match_level"] = get_match_level(
        result["score"]
    )

    return result


# ==================================================
# Find Best Matches
# ==================================================

def find_best_matches(
    lost_report,
    found_reports,
    minimum_score=60
):
    """
    Compare one lost report against multiple
    found reports.

    Returns:
        List of potential matches sorted by score.
    """

    matches = []

    for found_report in found_reports:

        result = generate_match_result(
            lost_report,
            found_report
        )

        if result["score"] >= minimum_score:

            matches.append({
                "report": found_report,
                "score": result["score"],
                "match_level": result["match_level"],
                "details": result
            })

    matches.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return matches


# ==================================================
# Local Testing
# ==================================================

def main():

    # ----------------------------------------------
    # Test reports
    # ----------------------------------------------

    lost_report = {
        "category": "Backpack",
        "ai_color": "black",
        "ai_object": "backpack",
        "ai_type": "college backpack",
        "ai_features": json.dumps([
            "front pocket",
            "two shoulder straps",
            "zipper"
        ]),
        "title": "Black Backpack Lost",
        "description": (
            "Black college backpack with front pocket "
            "and zipper."
        ),
        "location": "Library",
        "reported_at": "2026-08-29 18:14:48"
    }

    found_report = {
        "category": "Backpack",
        "ai_color": "black",
        "ai_object": "backpack",
        "ai_type": "college backpack",
        "ai_features": json.dumps([
            "front pocket",
            "two shoulder straps",
            "zipper"
        ]),
        "title": "Black Backpack Found",
        "description": (
            "Black backpack with front pocket "
            "and zipper."
        ),
        "location": "Library",
        "reported_at": "2026-08-29 18:14:48"
    }

    other_report = {
        "category": "Bottle",
        "ai_color": "blue",
        "ai_object": "water bottle",
        "ai_type": "plastic water bottle",
        "ai_features": json.dumps([
            "plastic",
            "blue"
        ]),
        "title": "Blue Water Bottle Found",
        "description": (
            "Blue plastic water bottle."
        ),
        "location": "Hostel",
        "reported_at": "2026-08-29 18:14:48"
    }

    # ----------------------------------------------
    # Same-item test
    # ----------------------------------------------

    result = generate_match_result(
        lost_report,
        found_report
    )

    print("Same Item Test")
    print("--------------")

    print(
        "Match Score   :",
        f"{result['score']}%"
    )

    print(
        "Match Level   :",
        result["match_level"]
    )

    print(
        "Category      :",
        f"{result['category_score']}%"
    )

    print(
        "Color         :",
        f"{result['color_score']}%"
    )

    print(
        "Description   :",
        f"{result['description_score']}%"
    )

    print(
        "Location      :",
        f"{result['location_score']}%"
    )

    print(
        "Time          :",
        f"{result['time_score']}%"
    )

    # ----------------------------------------------
    # Multi-match test
    # ----------------------------------------------

    matches = find_best_matches(
        lost_report,
        [
            found_report,
            other_report
        ],
        minimum_score=0
    )

    print("\nPotential Matches")
    print("-----------------")

    for match in matches:

        report = match["report"]

        report_id = get_value(
            report,
            "id"
        )

        print(
            f"ID: {report_id if report_id is not None else 'N/A'} | "
            f"Title: {report['title']} | "
            f"Score: {match['score']}% | "
            f"Level: {match['match_level']}"
        )


# ==================================================
# Run local test
# ==================================================

if __name__ == "__main__":
    main()