from flask import Flask, render_template, request
import database
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
    data = request.get_json()

    seller_id = data["seller_id"]
    title = data["title"]
    category = data["category"]
    listing_type = data["listing_type"]
    price = data["price"]

    item_id = database.create_item(seller_id, title, category, listing_type, price)

    if item_id:
        return {
            "status": "success",
            "item_id": item_id
        }
    else:
        return {
            "status": "failed",
            "message": "Could not create item"
        }



# lost and found ----------------------------------------------------------------------------------

@app.route("/lost_found/")
def lost_found():
    return render_template("lost_found.html")

@app.route("/lost_found/add/", methods=["POST"])
def add_lost_found_item():
    data = request.get_json()

    database.create_lost_found_report()




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