import pandas as pd
from sklearn.ensemble import RandomForestRegressor


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATA_PATH = "data/demand.csv"

FEATURES = [
    "searches",
    "views",
    "favorites",
    "listings",
    "exam_days"
]

TARGET = "demand"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

def load_data():
    """Load demand dataset from CSV."""
    df = pd.read_csv(DATA_PATH)
    return df


# --------------------------------------------------
# Train demand prediction model
# --------------------------------------------------

def train_model():
    """
    Load the dataset, prepare features and target,
    and train the Random Forest regression model.

    Returns:
        trained model
    """

    df = load_data()

    X = df[FEATURES]
    y = df[TARGET]

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(X, y)

    return model


# --------------------------------------------------
# Convert demand score into a useful level
# --------------------------------------------------

def get_demand_level(score):
    """
    Convert numerical demand score into
    HIGH / MEDIUM / LOW.
    """

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MEDIUM"

    else:
        return "LOW"


# --------------------------------------------------
# Predict demand
# --------------------------------------------------

def predict_demand(
    model,
    searches,
    views,
    favorites,
    listings,
    exam_days
):
    """
    Predict demand using the trained model.

    Returns:
        {
            "demand_score": float,
            "demand_level": str
        }
    """

    new_data = pd.DataFrame([
        {
            "searches": searches,
            "views": views,
            "favorites": favorites,
            "listings": listings,
            "exam_days": exam_days
        }
    ])

    prediction = model.predict(new_data)

    score = float(prediction[0])

    return {
        "demand_score": round(score, 2),
        "demand_level": get_demand_level(score)
    }


# --------------------------------------------------
# Main - testing only
# --------------------------------------------------

if __name__ == "__main__":

    # Load dataset
    df = load_data()

    print("Dataset loaded successfully!")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # Category-wise average demand
    print("\nAverage demand by category:")
    print(
        df.groupby("category")["demand"].mean()
    )

    # Train model
    model = train_model()

    print("\nModel trained successfully!")

    # Test prediction
    result = predict_demand(
        model=model,
        searches=35,
        views=55,
        favorites=10,
        listings=4,
        exam_days=5
    )

    print("\nPrediction Result:")
    print("------------------")
    print("Demand Score :", result["demand_score"])
    print("Demand Level :", result["demand_level"])