import json


# --------------------------------------------------
# 1. Prompt for Lost & Found attribute extraction
# --------------------------------------------------

LOST_FOUND_PROMPT = """
Analyze this image for a college campus Lost & Found system.

Extract only attributes that are clearly visible or reasonably
identifiable from the image.

Return ONLY valid JSON with these fields:

{
    "object": "main object/item",
    "color": "main visible color",
    "type": "specific type of object",
    "features": [
        "visible feature 1",
        "visible feature 2"
    ]
}

Important rules:

1. Do NOT guess when the object is unclear.
2. If the image is blurry, empty, mostly a background, or the
   object cannot be identified reliably, use:
   - object = "Unknown"
   - color = "Unknown"
   - type = "Unknown"
   - features = []

3. Do not invent brand names or hidden features.
4. Only include features that are actually visible.
5. Return only valid JSON.
"""


# --------------------------------------------------
# 2. Convert AI response into safe structured data
# --------------------------------------------------

def parse_lost_found_result(response_text):
    """
    Convert Gemini's JSON response into a Python dictionary.

    Args:
        response_text (str): Raw JSON text returned by Gemini.

    Returns:
        dict: Structured Lost & Found attributes.
    """

    try:
        result = json.loads(response_text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid Lost & Found AI JSON: {e}"
        )

    # ----------------------------------------------
    # Ensure required fields exist
    # ----------------------------------------------

    result.setdefault("object", "Unknown")
    result.setdefault("color", "Unknown")
    result.setdefault("type", "Unknown")
    result.setdefault("features", [])

    # ----------------------------------------------
    # Ensure features is always a list
    # ----------------------------------------------

    if not isinstance(result["features"], list):
        result["features"] = []

    return result


# --------------------------------------------------
# 3. Local fallback for unclear results
# --------------------------------------------------

def get_unknown_lost_found_result():
    """
    Return a safe fallback when the image cannot be
    identified reliably.
    """

    return {
        "object": "Unknown",
        "color": "Unknown",
        "type": "Unknown",
        "features": []
    }


# --------------------------------------------------
# 4. Validate extracted attributes
# --------------------------------------------------

def validate_lost_found_result(result):
    """
    Validate and normalize a Lost & Found AI result.

    Args:
        result (dict): AI-generated attributes.

    Returns:
        dict: Safe normalized result.
    """

    if not isinstance(result, dict):
        return get_unknown_lost_found_result()

    object_name = result.get("object", "Unknown")
    color = result.get("color", "Unknown")
    item_type = result.get("type", "Unknown")
    features = result.get("features", [])

    if not object_name:
        object_name = "Unknown"

    if not color:
        color = "Unknown"

    if not item_type:
        item_type = "Unknown"

    if not isinstance(features, list):
        features = []

    # Keep only string features
    features = [
        str(feature).strip()
        for feature in features
        if str(feature).strip()
    ]

    return {
        "object": str(object_name).strip(),
        "color": str(color).strip(),
        "type": str(item_type).strip(),
        "features": features
    }


# --------------------------------------------------
# 5. Build a searchable description
# --------------------------------------------------

def build_search_text(result):
    """
    Build normalized text from extracted Lost & Found
    attributes for later matching.

    Args:
        result (dict): Validated AI result.

    Returns:
        str: Searchable text.
    """

    result = validate_lost_found_result(result)

    parts = [
        result["object"],
        result["color"],
        result["type"],
        *result["features"]
    ]

    return " ".join(
        part for part in parts
        if part and part.lower() != "unknown"
    ).strip()


# --------------------------------------------------
# 6. Local tests
# --------------------------------------------------

def main():

    print("Lost & Found AI module loaded successfully.")

    sample = {
        "object": "backpack",
        "color": "black",
        "type": "college backpack",
        "features": [
            "front pocket",
            "two shoulder straps",
            "zipper"
        ]
    }

    validated = validate_lost_found_result(sample)

    print("\nValidated Result:")
    print(json.dumps(validated, indent=4))

    print("\nSearch Text:")
    print(build_search_text(validated))

    print("\nUnknown Fallback:")
    print(
        json.dumps(
            get_unknown_lost_found_result(),
            indent=4
        )
    )


# --------------------------------------------------
# 7. Run local test only when executed directly
# --------------------------------------------------

if __name__ == "__main__":
    main()