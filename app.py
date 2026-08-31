from flask import Flask, render_template, request, redirect , url_for
import database
import os
import uuid

from werkzeug.utils import secure_filename
# from ai import vision, matching  

app = Flask(__name__)

# homepage ----------------------------------------------------------------------------------------

@app.route("/")
def home_page():
    return render_template("index.html")



# marketplace -------------------------------------------------------------------------------------

@app.route("/marketplace/")
def marketplace():
    products = database.get_items()
    categories = database.get_categories()
    return render_template("marketplace.html", products=products,categories=categories)


@app.route("/marketplace/item/<int:item_id>/")
def product(item_id):
    item = database.get_item(item_id)

    if not item:
        return "Product Not found"
    else:
        return render_template("item.html", item=item)


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

@app.route("/api/marketplace/trends/")
def trends():
    return database.get_search_demand()



# interaction -------------------------------------------------------------------------------------
# maybe not required
'''
@app.route("/api/activity/search/") 
def log_search():
    data = request.get_json();

    if not data:
        return {
            "status" : "Failed",
            "message" : "Data required"
        }

    user_id = data["user_id"]
    query = data["query"]
    category = data["category"]

    database.log_search(user_id, query, category)

    return {
        "status" : "Success",
        "message" : "Interaction logged"
    }

@app.route("/api/activity/interaction/")
def log_interaction():
    data = request.get_json();
    
    if not data:
        return {
            "status" : "Failed",
            "message" : "Data required"
        }

    user_id = data["user_id"]
    item_id = data["item_id"]
    action = data["action"]

    database.log_interaction(user_id, item_id, action)

    return {
        "status" : "Success",
        "message" : "Interaction logged"
    }
'''


# image recognition -------------------------------------------------------------------------------
'''
@app.route("/api/image/recognize", methods=['POST'])
def image_recognition():
    if image not in request.files:
        return {
            "status" : "Failed",
            "message" : "Image required"
        }


    image = request.files("image")

    result = vision.analyze_item(image)

    return {
        "status" : "Success",
        "data" : result
    }
'''

# sell and rent site ------------------------------------------------------------------------------

@app.route("/sell-rent/")
def sell():
    return render_template("sell.html")

@app.route("/sell-rent/add/", methods=["POST"])
def add_item():

    title = request.form.get("title")
    description = request.form.get("description")
    category = request.form.get("category")
    listing_type = request.form.get("listing_type")
    price = request.form.get("price")
    condition = request.form.get("condition")

    image = request.files.get("image")


    # -----------------------------
    # Basic validation
    # -----------------------------

    if not title or not description or not category:
        return {
            "status": "failed",
            "message": "Title, description and category are required"
        }, 400

    if not listing_type or not price or not condition:
        return {
            "status": "failed",
            "message": "Listing type, price and condition are required"
        }, 400


    # -----------------------------
    # Seller ID
    # -----------------------------
    # PLACEHOLDER:
    # Replace this with the ID of the
    # currently logged-in user later.

    seller_id = 1


    # -----------------------------
    # Save image
    # -----------------------------

    image_path = None

    if image and image.filename:

        upload_folder = os.path.join(
            app.root_path,
            "static",
            "uploads"
        )

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        filename = secure_filename(image.filename)
        extension = os.path.splitext(filename)[1]
        filename = str(uuid.uuid4()) + extension

        image.save(
            os.path.join(
                upload_folder,
                filename
            )
        )

        # Path stored in database
        image_path = "uploads/" + filename


    # -----------------------------
    # Create database item
    # -----------------------------

    item_id = database.create_item(

        seller_id=seller_id,

        title=title,

        description=description,

        category=category,

        listing_type=listing_type,

        price=float(price),

        image_path=image_path,

        condition=condition
    )


    # -----------------------------
    # Response
    # -----------------------------

    if item_id:
        return redirect(url_for("marketplace"))

    return {
        "status": "failed",
        "message": "Could not create item"
    }, 500



# lost and found ----------------------------------------------------------------------------------

@app.route("/lost_found/")
def lost_found():
    reports = database.get_lost_found_reports()

    lost_reports = database.get_lost_found_reports("lost")
    found_reports = database.get_lost_found_reports("found")

    lost_count = len(lost_reports)
    found_count = len(found_reports)

    # PLACEHOLDER: matching system not implemented yet
    match_count = 0

    return render_template(
        "lost_found.html",
        reports=reports,
        lost_count=lost_count,
        found_count=found_count,
        match_count=match_count
    )

@app.route("/lost_found/add/", methods=["POST"])
def add_lost_found_item():
    data = request.get_json()

    if not data:
        return {
            "status": "failed",
            "message": "Data required"
        }, 400

    report_type = data.get("report_type")
    title = data.get("title")
    description = data.get("description")
    category = data.get("category")
    location = data.get("location")
    image_path = data.get("image_path")
    user_id = data.get("user_id")

    report_id = database.create_lost_found_report(
        report_type=report_type,
        title=title,
        description=description,
        category=category,
        location=location,
        image_path=image_path,
        user_id=user_id
    )

    if report_id:
        return {
            "status": "success",
            "report_id": report_id
        }

    return {
        "status": "failed",
        "message": "Could not create lost/found report"
    }, 500

@app.route("/lost_found/report/lost")
def report_lost():
    return "Report Lost Item page - placeholder"


@app.route("/lost_found/report/found")
def report_found():
    return "Report Found Item page - placeholder"


@app.route("/lost_found/<int:report_id>")
def lost_found_details(report_id):
    return f"Lost & Found details page - placeholder for report {report_id}"


# testing -----------------------------------------------------------------------------------------

@app.route("/api/test/")
def api_test():
    return {
        "message": "Backend is working",
        "status": "Success"
    }

@app.route("/api/products/", methods=["POST"])
def create_products():
    result = request.get_json()

    return {
        "data" : result
    }

@app.route("/api/products/")
def search_test():
    product = request.args.get("search")
    category = request.args.get("category")

    return {
        "product" : product,
        "category" : category
    }



if __name__ == '__main__':
    app.run(debug = True)