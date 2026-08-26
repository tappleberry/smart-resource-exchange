from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

# 1. Render index.html
@app.route("/")
def serve_home():
    return render_template("index.html")

# 2. Handle button post & redirect
@app.route("/navigate", methods=["POST"])
def handle_navigation():
    # Run any backend operations/validations here
    return redirect(url_for("serve_dashboard"))

# 3. Render dashboard.html
@app.route("/dashboard")
def serve_dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(port=8000, debug=True)