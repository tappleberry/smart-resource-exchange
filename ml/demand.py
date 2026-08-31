import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score


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
    """
    Load demand dataset from CSV.
    """

    df = pd.read_csv(
        DATA_PATH
    )

    return df


# --------------------------------------------------
# Get exam days for category
# --------------------------------------------------

def get_exam_days(category):
    """
    Get exam_days for a given category
    from the demand dataset.
    """

    df = load_data()

    matching_rows = df[
        df["category"].str.lower()
        == category.lower()
    ]

    if matching_rows.empty:
        return None

    return int(
        matching_rows.iloc[-1]["exam_days"]
    )


# --------------------------------------------------
# Get category features
# --------------------------------------------------

def get_category_features(category):
    """
    Get all ML features for a category.

    Returns:
        {
            "searches": int,
            "views": int,
            "favorites": int,
            "listings": int,
            "exam_days": int
        }
    """

    import database

    category_features = (
        database.get_category_feature_data()
    )

    for row in category_features:

        if row["category"].lower() == category.lower():

            exam_days = get_exam_days(
                category
            )

            if exam_days is None:
                return None

            return {
                "searches": row["searches"],
                "views": row["views"],
                "favorites": row["favorites"],
                "listings": row["listings"],
                "exam_days": exam_days
            }

    return None


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

    model.fit(
        X,
        y
    )

    return model


# --------------------------------------------------
# Evaluate demand prediction model
# --------------------------------------------------

def evaluate_model(test_size=0.2):
    """
    Evaluate the Random Forest model using a
    train/test split.

    Returns:
        {
            "mae": float,
            "r2": float,
            "train_rows": int,
            "test_rows": int
        }

    Note:
        The evaluation becomes meaningful only when
        the dataset contains enough historical rows.
    """

    df = load_data()

    # ----------------------------------------------
    # Basic dataset validation
    # ----------------------------------------------

    required_columns = FEATURES + [
        TARGET
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing_columns)
        )

    if len(df) < 10:

        raise ValueError(
            "Dataset is too small for reliable "
            "train/test evaluation. "
            f"Only {len(df)} rows available."
        )

    # ----------------------------------------------
    # Prepare features and target
    # ----------------------------------------------

    X = df[FEATURES]
    y = df[TARGET]

    # ----------------------------------------------
    # Train/test split
    # ----------------------------------------------

    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=test_size,
            random_state=42
        )
    )

    # ----------------------------------------------
    # Train model
    # ----------------------------------------------

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    # ----------------------------------------------
    # Predictions
    # ----------------------------------------------

    predictions = model.predict(
        X_test
    )

    # ----------------------------------------------
    # Metrics
    # ----------------------------------------------

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    return {
        "mae": round(
            float(mae),
            2
        ),
        "r2": round(
            float(r2),
            4
        ),
        "train_rows": len(X_train),
        "test_rows": len(X_test)
    }


# --------------------------------------------------
# Feature importance
# --------------------------------------------------

def get_feature_importance(model=None):
    """
    Get feature importance from the trained
    Random Forest model.

    Returns:
        Dictionary:
            {
                feature_name: importance
            }
    """

    if model is None:

        model = train_model()

    importance = {}

    for feature, value in zip(
        FEATURES,
        model.feature_importances_
    ):

        importance[feature] = round(
            float(value),
            4
        )

    return importance


# --------------------------------------------------
# Convert demand score into useful level
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

    prediction = model.predict(
        new_data
    )

    score = float(
        prediction[0]
    )

    return {
        "demand_score": round(
            score,
            2
        ),
        "demand_level": get_demand_level(
            score
        )
    }


# --------------------------------------------------
# Predict category demand
# --------------------------------------------------

def predict_category_demand(category):
    """
    Predict demand for a category using
    current database features.

    Returns:
        {
            "category": str,
            "demand_score": float,
            "demand_level": str,
            "features": dict
        }

    If no data is available for the category,
    returns None.
    """

    features = get_category_features(
        category
    )

    if features is None:
        return None

    model = train_model()

    result = predict_demand(
        model=model,
        searches=features["searches"],
        views=features["views"],
        favorites=features["favorites"],
        listings=features["listings"],
        exam_days=features["exam_days"]
    )

    return {
        "category": category,
        "demand_score": result["demand_score"],
        "demand_level": result["demand_level"],
        "features": features
    }


# --------------------------------------------------
# Main - testing only
# --------------------------------------------------

if __name__ == "__main__":

    # ----------------------------------------------
    # Load dataset
    # ----------------------------------------------

    df = load_data()

    print(
        "Dataset loaded successfully!"
    )

    print(
        f"Rows: {df.shape[0]}"
    )

    print(
        f"Columns: {df.shape[1]}"
    )

    # ----------------------------------------------
    # Category-wise average demand
    # ----------------------------------------------

    print(
        "\nAverage demand by category:"
    )

    print(
        df.groupby(
            "category"
        )["demand"].mean()
    )

    # ----------------------------------------------
    # Train model
    # ----------------------------------------------

    model = train_model()

    print(
        "\nModel trained successfully!"
    )

    # ----------------------------------------------
    # Feature importance
    # ----------------------------------------------

    print(
        "\nFeature Importance:"
    )

    importance = get_feature_importance(
        model
    )

    for feature, value in importance.items():

        print(
            f"{feature}: {value}"
        )

    # ----------------------------------------------
    # Test prediction
    # ----------------------------------------------

    result = predict_demand(
        model=model,
        searches=35,
        views=55,
        favorites=10,
        listings=4,
        exam_days=5
    )

    print(
        "\nPrediction Result:"
    )

    print(
        "------------------"
    )

    print(
        "Demand Score :",
        result["demand_score"]
    )

    print(
        "Demand Level :",
        result["demand_level"]
    )

    # ----------------------------------------------
    # Model evaluation
    # ----------------------------------------------

    try:

        evaluation = evaluate_model()

        print(
            "\nModel Evaluation:"
        )

        print(
            "------------------"
        )

        print(
            "MAE        :",
            evaluation["mae"]
        )

        print(
            "R2 Score   :",
            evaluation["r2"]
        )

        print(
            "Train Rows :",
            evaluation["train_rows"]
        )

        print(
            "Test Rows  :",
            evaluation["test_rows"]
        )

    except ValueError as e:

        print(
            "\nModel Evaluation skipped:"
        )

        print(e)