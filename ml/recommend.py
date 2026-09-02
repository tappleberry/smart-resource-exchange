from ml.demand import predict_category_demand


# ==================================================
# Recommendation Rules
# ==================================================

def get_recommendation_level(
    demand_score,
    listings
):
    """
    Determine recommendation level using
    predicted demand and current supply.
    """

    if demand_score >= 70 and listings <= 5:
        return "HIGH PRIORITY"

    if demand_score >= 55 and listings <= 7:
        return "GOOD OPPORTUNITY"

    if demand_score >= 40:
        return "MODERATE"

    return "LOW"


# ==================================================
# Recommendation Message
# ==================================================

def get_recommendation_message(
    demand_score,
    listings,
    exam_days
):
    """
    Generate a human-readable recommendation.
    """

    level = get_recommendation_level(
        demand_score,
        listings
    )

    exam_message = ""

    if exam_days <= 7:
        exam_message = (
            "Exam period is approaching."
        )

    elif exam_days <= 14:
        exam_message = (
            "Exam period is near."
        )

    if level == "HIGH PRIORITY":

        message = (
            "High demand with limited supply. "
            "This is a strong category to list in."
        )

    elif level == "GOOD OPPORTUNITY":

        message = (
            "Demand is healthy and supply is "
            "still relatively limited."
        )

    elif level == "MODERATE":

        message = (
            "There is moderate demand for this "
            "category."
        )

    else:

        message = (
            "Current demand is relatively low."
        )

    if exam_message:
        message = (
            f"{message} {exam_message}"
        )

    return message


# ==================================================
# Generate Recommendation
# ==================================================

def generate_recommendation(
    category,
    demand_score,
    listings,
    exam_days,
    features
):
    """
    Generate a complete recommendation.
    """

    level = get_recommendation_level(
        demand_score,
        listings
    )

    recommended = level in {
        "HIGH PRIORITY",
        "GOOD OPPORTUNITY"
    }

    message = get_recommendation_message(
        demand_score,
        listings,
        exam_days
    )

    return {
        "category": category,
        "demand_score": round(
            float(demand_score),
            2
        ),
        # Keep the original features from demand.csv

    "features": {
        "searches": int(features.get("searches", 0) or 0),
        "views": int(features.get("views", 0) or 0),
        "favorites": int(features.get("favorites", 0) or 0),
        "listings": int(features.get("listings", 0) or 0),
        "exam_days": int(features.get("exam_days", 0) or 0)
    },
        "listings": int(
            listings
        ),
        "exam_days": int(
            exam_days
        ),
        "recommendation_level": level,
        "recommended": recommended,
        "message": message
    }


# ==================================================
# Rank Recommendations
# ==================================================

def rank_recommendations(
    recommendations
):
    """
    Sort recommendations from strongest
    opportunity to weakest.
    """

    priority = {
        "HIGH PRIORITY": 4,
        "GOOD OPPORTUNITY": 3,
        "MODERATE": 2,
        "LOW": 1
    }

    return sorted(
        recommendations,
        key=lambda item: (
            priority.get(
                item["recommendation_level"],
                0
            ),
            item["demand_score"],
            -item["listings"]
        ),
        reverse=True
    )


# ==================================================
# Generate Recommendations
# ==================================================

def generate_recommendations(
    demand_results
):
    """
    Convert multiple demand predictions into
    ranked seller recommendations.
    """

    recommendations = []

    for result in demand_results:

        if not result:
            continue

        category = result.get(
            "category"
        )

        demand_score = result.get(
            "demand_score",
            0
        )

        features = result.get(
            "features",
            {}
        )

        listings = features.get(
            "listings",
            0
        )

        exam_days = features.get(
            "exam_days",
            30
        )

        recommendation = generate_recommendation(
            category=category,
            demand_score=demand_score,
            listings=listings,
            exam_days=exam_days,
            features=features
        )

        recommendations.append(
            recommendation
        )

    return rank_recommendations(
        recommendations
    )


# ==================================================
# Predict + Recommend for All Categories
# ==================================================

def get_category_recommendations(
    categories
):
    """
    Get live demand predictions from the ML model
    and convert them into ranked recommendations.
    """

    demand_results = []

    for category in categories:

        result = predict_category_demand(
            category
        )

        if result is not None:

            demand_results.append(
                result
            )

    return generate_recommendations(
        demand_results
    )


# ==================================================
# Local Testing
# ==================================================

def main():

    categories = [
        "Electronics",
        "Books",
        "Cycles",
        "Hostel Essentials",
        "Lab Equipment",
        "Furniture",
        "Clothing",
        "Sports Equipment"
    ]

    recommendations = get_category_recommendations(
        categories
    )

    print(
        "Live Demand Recommendation Test"
    )

    print(
        "--------------------------------"
    )

    for recommendation in recommendations:

        print(
            f"\nCategory: "
            f"{recommendation['category']}"
        )

        print(
            f"Demand Score: "
            f"{recommendation['demand_score']}"
        )

        print(
            f"Listings: "
            f"{recommendation['listings']}"
        )

        print(
            f"Exam Days: "
            f"{recommendation['exam_days']}"
        )

        print(
            f"Recommendation Level: "
            f"{recommendation['recommendation_level']}"
        )

        print(
            f"Recommended: "
            f"{recommendation['recommended']}"
        )

        print(
            f"Message: "
            f"{recommendation['message']}"
        )


# ==================================================
# Run Local Test
# ==================================================

if __name__ == "__main__":
    main()