# --------------------------------------------------
# Reference prices for marketplace categories
# --------------------------------------------------

# --------------------------------------------------
# Category normalization / aliases
# --------------------------------------------------

CATEGORY_ALIASES = {
    "electronics": "electronics",
    "electronics accessories": "electronics",

    "vehicles & transport": "cycles",
    "bicycles & transport": "cycles",
    "bicycles": "cycles",
    "bicycle": "cycles",
    "cycle": "cycles",
    "cycles": "cycles",

    "books": "books",
    "furniture": "furniture",
    "clothing": "clothing",
    "other": "other"
}

REFERENCE_PRICES = {
    "electronics": 1000,
    "books": 300,
    "cycles": 2500,
    "furniture": 2000,
    "clothing": 500,
    "other": 500
}


# --------------------------------------------------
# Condition adjustment factors
# --------------------------------------------------

CONDITION_FACTORS = {
    "like new": 1.00,
    "good": 0.80,
    "used": 0.60
}

# --------------------------------------------------
# Condition normalization / aliases
# --------------------------------------------------

CONDITION_ALIASES = {
    "like new": "like new",
    "new": "like new",

    "good": "good",
    "used - good": "good",
    "used good": "good",

    "used": "used",
    "fair": "used",
    "average": "used"
}

# --------------------------------------------------
# Suggested price calculation
# --------------------------------------------------

def suggest_price(category, condition):
    """
    Suggest a price using category reference price
    and item condition.
    """

    # Handle missing values safely
    if not category:
        category = "other"

    if not condition:
        condition = "used"

    raw_category = str(category).strip().lower()

    category_key = CATEGORY_ALIASES.get(
    raw_category,
    "other"
)
    raw_condition = str(condition).strip().lower()

    condition_key = CONDITION_ALIASES.get(
    raw_condition,
    "used"
)

    # Get reference price
    base_price = REFERENCE_PRICES.get(
        category_key,
        REFERENCE_PRICES["other"]
    )

    # Get condition factor
    factor = CONDITION_FACTORS.get(
        condition_key,
        CONDITION_FACTORS["used"]
    )

    suggested_price = base_price * factor

    return round(suggested_price)

# --------------------------------------------------
# Generate pricing information from AI result
# --------------------------------------------------

def suggest_price_from_ai_result(ai_result):
    """
    Generate a suggested price using the category and
    condition returned by the AI image analysis.
    """

    if not ai_result:
        return None

    category = ai_result.get("category")
    condition = ai_result.get("condition")

    return suggest_price(category, condition)