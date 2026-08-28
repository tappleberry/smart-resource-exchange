import uuid
from pathlib import Path

from flask import Flask, jsonify, request, render_template_string
from werkzeug.utils import secure_filename

from ai.vision import analyze_item


app = Flask(__name__)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

UPLOAD_FOLDER = PROJECT_ROOT / "uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

UPLOAD_FOLDER.mkdir(exist_ok=True)


# --------------------------------------------------
# Test page + upload route
# --------------------------------------------------

@app.route("/test-ai", methods=["GET", "POST"])
def test_ai():

    # -------------------------------
    # GET request
    # Show upload form
    # -------------------------------

    if request.method == "GET":

        return render_template_string("""
        <!DOCTYPE html>
        <html>

        <head>
            <title>AI Image Test</title>
        </head>

        <body>

            <h2>Upload Item Image</h2>

            <form method="POST" enctype="multipart/form-data">

                <input
                    type="file"
                    name="image"
                    accept="image/*"
                    required
                >

                <br><br>

                <button type="submit">
                    Analyze Image
                </button>

            </form>

        </body>

        </html>
        """)

    # -------------------------------
    # POST request
    # Receive uploaded image
    # -------------------------------

    image = request.files.get("image")

    if image is None or image.filename == "":
        return jsonify({
            "success": False,
            "error": "No image uploaded"
        }), 400

    try:

        # -------------------------------
        # Make filename safe
        # -------------------------------

        filename = secure_filename(image.filename)

        # -------------------------------
        # Check file extension
        # -------------------------------

        extension = filename.rsplit(".", 1)[-1].lower()

        if extension not in ALLOWED_EXTENSIONS:
            return jsonify({
                "success": False,
                "error": "Only PNG, JPG, JPEG and WEBP images are allowed"
            }), 400

        # -------------------------------
        # Generate unique filename
        # -------------------------------

        unique_filename = f"{uuid.uuid4().hex}.{extension}"

        # -------------------------------
        # Save uploaded image
        # -------------------------------

        image_path = UPLOAD_FOLDER / unique_filename

        image.save(image_path)

        # -------------------------------
        # Send image to AI
        # -------------------------------

        result = analyze_item(str(image_path))

        # -------------------------------
        # Return AI result
        # -------------------------------

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# --------------------------------------------------
# Start server
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)