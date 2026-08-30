from pathlib import Path
import json
import uuid

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

import database

from ai.vision import analyze_item
from ai.lost_found import analyze_lost_found_item
from ai.matching import find_best_matches

from ml.pricing import suggest_price_from_ai_result
from ml.demand import predict_category_demand


# ==================================================
# Flask App
# ==================================================

app = Flask(__name__)


# ==================================================
# Upload Configuration
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent

UPLOAD_FOLDER = PROJECT_ROOT / "uploads"

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "webp"
}

UPLOAD_FOLDER.mkdir(
    exist_ok=True
)


# ==================================================
# Helper Function
# ==================================================

def is_allowed_file(filename):
    """
    Check whether uploaded file has
    an allowed extension.
    """

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[-1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==================================================
# Homepage
# ==================================================

@app.route("/")
def home_page():

    return render_template(
        "index.html"
    )


# ==================================================
# Marketplace
# ==================================================

@app.route("/marketplace/")
def marketplace():

    products = database.get_items()

    categories = database.get_categories()

    return render_template(
        "marketplace.html",
        products=products,
        categories=categories
    )


# ==================================================
# Product Details
# ==================================================

@app.route("/marketplace/item/<int:item_id>/")
def product(item_id):

    item = database.get_item(
        item_id
    )

    if not item:
        return "Product Not found"

    return render_template(
        "item.html",
        item=item
    )


# ==================================================
# Marketplace Search
# ==================================================

@app.route("/marketplace/search/")
def search():

    query = request.args.get("q")
    category = request.args.get("category")
    listing_type = request.args.get("listing_type")

    min_price = request.args.get(
        "min_price"
    )

    max_price = request.args.get(
        "max_price"
    )

    condition = request.args.get(
        "condition"
    )

    # ----------------------------------------------
    # Convert prices from strings to numbers
    # ----------------------------------------------

    if min_price:

        min_price = float(
            min_price
        )

    else:

        min_price = None

    if max_price:

        max_price = float(
            max_price
        )

    else:

        max_price = None

    user_id = None

    database.log_search(
        user_id=user_id,
        query=query,
        category=category
    )

    products = database.search_items(
        query=query,
        category=category,
        listing_type=listing_type,
        min_price=min_price,
        max_price=max_price,
        condition=condition
    )

    categories = database.get_categories()

    return render_template(
        "marketplace.html",
        products=products,
        categories=categories
    )


# ==================================================
# Marketplace Trends
# ==================================================

@app.route("/api/marketplace/trends/")
def trends():

    return database.get_search_demand()


# ==================================================
# Demand Prediction API
# ==================================================

@app.route(
    "/api/demand/<category>/"
)
def demand_prediction(category):

    try:

        result = predict_category_demand(
            category
        )

        # ------------------------------------------
        # Category not available
        # ------------------------------------------

        if result is None:

            return jsonify({
                "success": False,
                "error": (
                    f"No demand data available "
                    f"for category: {category}"
                )
            }), 404

        # ------------------------------------------
        # Return prediction
        # ------------------------------------------

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==================================================
# AI Image Recognition
# ==================================================

@app.route(
    "/api/analyze-item/",
    methods=["POST"]
)
def analyze_image():

    # ----------------------------------------------
    # Get uploaded image
    # ----------------------------------------------

    image = request.files.get(
        "image"
    )

    if image is None or image.filename == "":

        return jsonify({
            "success": False,
            "error": "No image uploaded"
        }), 400

    try:

        # ------------------------------------------
        # Make filename safe
        # ------------------------------------------

        filename = secure_filename(
            image.filename
        )

        if not filename:

            return jsonify({
                "success": False,
                "error": "Invalid filename"
            }), 400

        # ------------------------------------------
        # Validate file type
        # ------------------------------------------

        if not is_allowed_file(
            filename
        ):

            return jsonify({
                "success": False,
                "error": (
                    "Only PNG, JPG, JPEG and WEBP "
                    "images are allowed"
                )
            }), 400

        # ------------------------------------------
        # Generate unique filename
        # ------------------------------------------

        extension = filename.rsplit(
            ".",
            1
        )[-1].lower()

        unique_filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        image_path = (
            UPLOAD_FOLDER
            / unique_filename
        )

        # ------------------------------------------
        # Save uploaded image
        # ------------------------------------------

        image.save(
            image_path
        )

        # ------------------------------------------
        # Analyze image using Gemini
        # ------------------------------------------

        result = analyze_item(
            str(image_path)
        )

        # ------------------------------------------
        # Apply rule-based pricing
        # ------------------------------------------

        is_unclear_item = (
            result.get("item_name")
            == "Unclear Item"
            or (
                result.get("category")
                == "Other"
                and result.get("condition")
                == "Unknown"
            )
        )

        if is_unclear_item:

            result["suggested_price"] = 0

        else:

            final_price = (
                suggest_price_from_ai_result(
                    result
                )
            )

            if final_price is not None:

                result["suggested_price"] = (
                    final_price
                )

        # ------------------------------------------
        # Return result
        # ------------------------------------------

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        error_message = str(e)

        # ------------------------------------------
        # Handle Gemini quota errors
        # ------------------------------------------

        if (
            "quota exceeded"
            in error_message.lower()
            or "resource_exhausted"
            in error_message.lower()
            or "429"
            in error_message
        ):

            return jsonify({
                "success": False,
                "error": error_message
            }), 429

        # ------------------------------------------
        # Handle other errors
        # ------------------------------------------

        return jsonify({
            "success": False,
            "error": error_message
        }), 500


# ==================================================
# Sell / Rent Page
# ==================================================

@app.route("/sell-rent/")
def sell():

    return render_template(
        "sell.html"
    )


# ==================================================
# Add Item
# ==================================================

@app.route(
    "/sell-rent/add/",
    methods=["POST"]
)
def add_item():

    data = request.get_json()

    seller_id = data["seller_id"]
    title = data["title"]
    category = data["category"]
    listing_type = data["listing_type"]
    price = data["price"]

    item_id = database.create_item(
        seller_id,
        title,
        category,
        listing_type,
        price
    )

    if item_id:

        return {
            "status": "success",
            "item_id": item_id
        }

    return {
        "status": "failed",
        "message": "Could not create item"
    }


# ==================================================
# Lost and Found Page
# ==================================================

@app.route("/lost_found/")
def lost_found():

    return render_template(
        "lost_found.html"
    )


# ==================================================
# Add Lost / Found Report
# ==================================================

@app.route(
    "/lost_found/add/",
    methods=["POST"]
)
def add_lost_found_item():

    try:

        # ------------------------------------------
        # Read request data
        # ------------------------------------------

        if request.is_json:

            data = request.get_json()

            if not isinstance(
                data,
                dict
            ):

                data = {}

        else:

            data = request.form.to_dict()

        # ------------------------------------------
        # Required fields
        # ------------------------------------------

        user_id = data.get(
            "user_id"
        )

        report_type = data.get(
            "report_type"
        )

        title = data.get(
            "title"
        )

        description = data.get(
            "description"
        )

        category = data.get(
            "category"
        )

        location = data.get(
            "location"
        )

        # ------------------------------------------
        # Validate required values
        # ------------------------------------------

        if not user_id:

            return jsonify({
                "success": False,
                "error": "user_id is required"
            }), 400

        if report_type not in {
            "lost",
            "found"
        }:

            return jsonify({
                "success": False,
                "error": (
                    "report_type must be "
                    "'lost' or 'found'"
                )
            }), 400

        if not title:

            return jsonify({
                "success": False,
                "error": "title is required"
            }), 400

        # ------------------------------------------
        # Convert user_id to integer
        # ------------------------------------------

        try:

            user_id = int(
                user_id
            )

        except (
            TypeError,
            ValueError
        ):

            return jsonify({
                "success": False,
                "error": (
                    "user_id must be an integer"
                )
            }), 400

        # ------------------------------------------
        # Initialize AI fields
        # ------------------------------------------

        ai_object = None
        ai_color = None
        ai_type = None
        ai_features = None

        image_path = data.get(
            "image_path"
        )

        ai_result = None

        # ------------------------------------------
        # Get uploaded image
        # ------------------------------------------

        image = request.files.get(
            "image"
        )

        if (
            image is not None
            and image.filename
        ):

            # --------------------------------------
            # Secure filename
            # --------------------------------------

            filename = secure_filename(
                image.filename
            )

            if not filename:

                return jsonify({
                    "success": False,
                    "error": (
                        "Invalid image filename"
                    )
                }), 400

            # --------------------------------------
            # Validate extension
            # --------------------------------------

            if not is_allowed_file(
                filename
            ):

                return jsonify({
                    "success": False,
                    "error": (
                        "Only PNG, JPG, JPEG "
                        "and WEBP images "
                        "are allowed"
                    )
                }), 400

            # --------------------------------------
            # Generate unique filename
            # --------------------------------------

            extension = filename.rsplit(
                ".",
                1
            )[-1].lower()

            unique_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )

            saved_image_path = (
                UPLOAD_FOLDER
                / unique_filename
            )

            # --------------------------------------
            # Save image
            # --------------------------------------

            image.save(
                saved_image_path
            )

            image_path = str(
                saved_image_path
            )

            # --------------------------------------
            # Analyze Lost & Found image
            # --------------------------------------

            ai_result = (
                analyze_lost_found_item(
                    image_path
                )
            )

            # --------------------------------------
            # Extract AI fields
            # --------------------------------------

            ai_object = ai_result.get(
                "object"
            )

            ai_color = ai_result.get(
                "color"
            )

            ai_type = ai_result.get(
                "type"
            )

            ai_features = json.dumps(
                ai_result.get(
                    "features",
                    []
                )
            )

        # ------------------------------------------
        # Create database report
        # ------------------------------------------

        report_id = (
            database.create_lost_found_report(
                user_id=user_id,
                report_type=report_type,
                title=title,
                description=description,
                category=category,
                image_path=image_path,
                location=location,
                ai_object=ai_object,
                ai_color=ai_color,
                ai_type=ai_type,
                ai_features=ai_features
            )
        )

        # ------------------------------------------
        # Select opposite report type for matching
        # ------------------------------------------

        if report_type == "lost":

            candidate_reports = (
                database.get_lost_found_reports(
                    report_type="found"
                )
            )

        else:

            candidate_reports = (
                database.get_lost_found_reports(
                    report_type="lost"
                )
            )

        # ------------------------------------------
        # Get created report
        # ------------------------------------------

        all_reports = (
            database.get_lost_found_reports()
        )

        created_report = None

        for report in all_reports:

            if report["id"] == report_id:

                created_report = report
                break

        # ------------------------------------------
        # Calculate potential matches
        # ------------------------------------------

        matches = []

        if created_report is not None:

            matches = find_best_matches(
                created_report,
                candidate_reports,
                minimum_score=60
            )

        # ------------------------------------------
        # Format matches for JSON response
        # ------------------------------------------

        formatted_matches = []

        for match in matches:

            report = match["report"]

            formatted_matches.append({
                "report_id": report["id"],
                "report_type": (
                    report["report_type"]
                ),
                "title": report["title"],
                "description": (
                    report["description"]
                ),
                "category": report["category"],
                "location": report["location"],
                "score": match["score"],
                "match_level": (
                    match["match_level"]
                ),
                "details": match["details"]
            })

        # ------------------------------------------
        # Return complete response
        # ------------------------------------------

        return jsonify({
            "success": True,
            "report_id": report_id,
            "ai_analysis": ai_result,
            "matches": formatted_matches
        })

    except Exception as e:

        error_message = str(e)

        # ------------------------------------------
        # Handle Gemini quota errors
        # ------------------------------------------

        if (
            "quota exceeded"
            in error_message.lower()
            or "resource_exhausted"
            in error_message.lower()
            or "429"
            in error_message
        ):

            return jsonify({
                "success": False,
                "error": error_message
            }), 429

        # ------------------------------------------
        # Handle other errors
        # ------------------------------------------

        return jsonify({
            "success": False,
            "error": error_message
        }), 500


# ==================================================
# Lost & Found Matches API
# ==================================================

@app.route(
    "/api/lost-found/matches/<int:report_id>/"
)
def lost_found_matches(report_id):

    # ----------------------------------------------
    # Get requested report
    # ----------------------------------------------

    reports = (
        database.get_lost_found_reports()
    )

    target_report = None

    for report in reports:

        if report["id"] == report_id:

            target_report = report
            break

    if target_report is None:

        return jsonify({
            "success": False,
            "error": (
                "Lost & Found report not found"
            )
        }), 404

    # ----------------------------------------------
    # Select opposite report type
    # ----------------------------------------------

    if (
        target_report["report_type"]
        == "lost"
    ):

        candidate_reports = (
            database.get_lost_found_reports(
                report_type="found"
            )
        )

    else:

        candidate_reports = (
            database.get_lost_found_reports(
                report_type="lost"
            )
        )

    # ----------------------------------------------
    # Calculate matches
    # ----------------------------------------------

    matches = find_best_matches(
        target_report,
        candidate_reports,
        minimum_score=60
    )

    # ----------------------------------------------
    # Format response
    # ----------------------------------------------

    formatted_matches = []

    for match in matches:

        report = match["report"]

        formatted_matches.append({
            "report_id": report["id"],
            "report_type": (
                report["report_type"]
            ),
            "title": report["title"],
            "description": (
                report["description"]
            ),
            "category": report["category"],
            "location": report["location"],
            "score": match["score"],
            "match_level": (
                match["match_level"]
            ),
            "details": match["details"]
        })

    return jsonify({
        "success": True,
        "report_id": report_id,
        "matches": formatted_matches
    })


# ==================================================
# Lost & Found Reports API
# ==================================================

@app.route("/api/lost-found/")
def lost_found_reports():

    reports = (
        database.get_lost_found_reports()
    )

    result = []

    for report in reports:

        result.append({
            "id": report["id"],
            "user_id": report["user_id"],
            "report_type": (
                report["report_type"]
            ),
            "title": report["title"],
            "description": (
                report["description"]
            ),
            "category": report["category"],
            "image_path": report["image_path"],
            "location": report["location"],
            "reported_at": (
                report["reported_at"]
            ),
            "status": report["status"],
            "ai_object": (
                report["ai_object"]
            ),
            "ai_color": (
                report["ai_color"]
            ),
            "ai_type": (
                report["ai_type"]
            ),
            "ai_features": (
                report["ai_features"]
            )
        })

    return jsonify({
        "success": True,
        "reports": result
    })


# ==================================================
# Backend Test
# ==================================================

@app.route("/api/test/")
def api_test():

    return {
        "message": "Backend is working",
        "status": "Success"
    }


# ==================================================
# Products API Test
# ==================================================

@app.route(
    "/api/products/",
    methods=["POST"]
)
def create_products():

    result = request.get_json()

    return {
        "data": result
    }


@app.route(
    "/api/products/"
)
def search_test():

    product = request.args.get(
        "search"
    )

    category = request.args.get(
        "category"
    )

    return {
        "product": product,
        "category": category
    }


# ==================================================
# Run Flask Application
# ==================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )