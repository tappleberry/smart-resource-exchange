# from flask import Flask, render_template, redirect, url_for, request

# app = Flask(__name__)

# # 1. Render index.html
# @app.route("/")
# def serve_home():
#     return render_template("index.html")

# # 2. Handle button post & redirect
# @app.route("/navigate", methods=["POST"])
# def handle_navigation():
#     # Run any backend operations/validations here
#     return redirect(url_for("serve_dashboard"))

# # 3. Render marketplace.html
# @app.route("/marketplace")
# def serve_dashboard():
#     return render_template("templates/marketplace.html")


from flask import Flask, render_template, request
import database

app = Flask(__name__)

# homepage

@app.route("/")
def home_page():
    return render_template("index.html")



# marketplace

@app.route("/marketplace")
def marketplace():
    products = database.get_items()

    return render_template("marketplace.html", products=products)

@app.route("/marketplace/<int:product_id>")
def product(product_id):
    product = database.get_item(product_id)

    if not product:
        return "Product Not found"
    else:
        return render_template("product.html", product=product)


@app.route("/marketplace/search")
def search():
    query = request.args.get("q")
    category = request.args.get("category")

    items = database.search_items(query=query, category=category)

    return items

@app.route("/api/marketplace/trends")
def trends():
    return database.trend


# sell and rent site 
@app.route("/sell-rent")
def sell():
    return render_template("sell.html")

@app.route("/sell-rent/add", methods=["POST"])
def add_item():
    data = request.get_json() or {}

    seller_id = data.get("seller_id")
    title = data.get("title")
    category = data.get("category")
    listing_type = data.get("listing_type")
    price = data.get("price")

    item_id = database.create_item(seller_id, title, category, listing_type, price)

    if item_id :
        # {
        #     "Status": "success",
        #     "Item_id" : item_id
        # }
        return {"Status": "success", "Item_id": item_id}, 201
    else :
        # {
        #     "Status" : "failed, retry!"
        # }
        return {"Status": "failed, retry!"}, 400


# lost and found

@app.route("/lost_found")
def lost_found():
    return render_template("lost_found.html")



# testing

@app.route("/api/test")
def api_test():
    return {
        "message": "Backend is working",
        "status": "Success"
    }

@app.route("/api/products", methods=["POST"])
def create_products():
    result = request.get_json()

    return {
        "data" : result
    }

@app.route("/api/products")
def search_test():
    product = request.args.get("search")
    category = request.args.get("category")

    return {
        "product" : product,
        "category" : category
    }
if __name__ == "__main__":
    app.run(port=8000, debug=True)