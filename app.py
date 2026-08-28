from pathlib import Path
import uuid

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

import database
from ai.vision import analyze_item


# ==================================================
# Flask App
# ==================================================

app = Flask(__name__)


# ==================================================
# Upload Configuration
# ==================================================

PROJECT_ROOT = Path(__file__).resolve().parent

UPLOAD_FOLDER = PROJECT_ROOT / "uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

UPLOAD_FOLDER.mkdir(exist_ok=True)


# ==================================================
# Helper Function
# ==================================================

def is_allowed_file(filename):
    """Check whether uploaded file has an allowed extension."""

    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[-1].lower()

    return extension in ALLOWED_EXTENSIONS


# ==================================================
# Homepage
# ==================================================

@app.route("/")
def home_page():
    return render_template("index.html")


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

    item = database.get_item(item_id)

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
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")
    condition = request.args.get("condition")

    # Convert prices from strings to numbers
    if min_price:
        min_price = float(min_price)
    else:
        min_price = None

    if max_price:
        max_price = float(max_price)
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
# AI Image Recognition
# ==================================================

@app.route("/api/analyze-item/", methods=["POST"])
def analyze_image():

    # ----------------------------------------------
    # Get uploaded image
    # ----------------------------------------------

    image = request.files.get("image")

    if image is None or image.filename == "":
        return jsonify({
            "success": False,
            "error": "No image uploaded"
        }), 400

    try:

        # ------------------------------------------
        # Make filename safe
        # ------------------------------------------

        filename = secure_filename(image.filename)

        if not filename:
            return jsonify({
                "success": False,
                "error": "Invalid filename"
            }), 400

        # ------------------------------------------
        # Validate file type
        # ------------------------------------------

        if not is_allowed_file(filename):
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

        extension = filename.rsplit(".", 1)[-1].lower()

        unique_filename = (
            f"{uuid.uuid4().hex}.{extension}"
        )

        image_path = UPLOAD_FOLDER / unique_filename

        # ------------------------------------------
        # Save uploaded image
        # ------------------------------------------

        image.save(image_path)

        # ------------------------------------------
        # Send image to Gemini
        # ------------------------------------------

        result = analyze_item(str(image_path))

        # ------------------------------------------
        # Return AI result
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
# Sell / Rent Page
# ==================================================

@app.route("/sell-rent/")
def sell():
    return render_template("sell.html")


# ==================================================
# Add Item
# ==================================================

@app.route("/sell-rent/add/", methods=["POST"])
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
# Lost and Found
# ==================================================

@app.route("/lost_found/")
def lost_found():
    return render_template("lost_found.html")


@app.route("/lost_found/add/", methods=["POST"])
def add_lost_found_item():

    data = request.get_json()

    database.create_lost_found_report()

    return {
        "status": "success",
        "message": "Lost/Found report received"
    }


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

@app.route("/api/products/", methods=["POST"])
def create_products():

    result = request.get_json()

    return {
        "data": result
    }


@app.route("/api/products/")
def search_test():

    product = request.args.get("search")
    category = request.args.get("category")

    return {
        "product": product,
        "category": category
    }


# ==================================================
# Run Flask Application
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)