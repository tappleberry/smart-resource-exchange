import os
import json

from dotenv import load_dotenv
from google import genai
from PIL import Image


# ==================================================
# 1. Load environment variables
# ==================================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in .env file"
    )


# ==================================================
# 2. Create Gemini client
# ==================================================

client = genai.Client(
    api_key=api_key
)


# ==================================================
# 3. Lost & Found AI Prompt
# ==================================================

LOST_FOUND_PROMPT = """
Analyze this image for a college campus Lost & Found system.

Identify the main physical object visible in the image.

Return ONLY valid JSON.

Required fields:

{
    "object": "main object/item",
    "color": "main visible color",
    "type": "specific type of object",
    "features": [
        "visible feature 1",
        "visible feature 2"
    ]
}

Important rules:

1. Identify an object ONLY if a distinct physical object is clearly
   visible and recognizable.

2. If the image is blurry, empty, mostly a background, or the object
   cannot be identified reliably, do NOT guess.

3. For an unclear image return:

   {
       "object": "Unknown",
       "color": "Unknown",
       "type": "Unknown",
       "features": []
   }

4. Never invent a brand, model, or feature that is not clearly visible.

5. Only include features that can actually be observed in the image.

6. Keep the response focused on the object useful for a Lost & Found
   system.

7. Return only JSON.
"""


# ==================================================
# 4. Unknown fallback
# ==================================================

def get_unknown_lost_found_result():
    """
    Return a safe fallback for unclear images.
    """

    return {
        "object": "Unknown",
        "color": "Unknown",
        "type": "Unknown",
        "features": []
    }


# ==================================================
# 5. Parse AI response
# ==================================================

def parse_lost_found_result(response_text):
    """
    Convert Gemini JSON response into a Python dictionary.
    """

    try:
        result = json.loads(response_text)

    except json.JSONDecodeError as e:
        raise ValueError(
            f"Invalid Lost & Found AI JSON: {e}"
        )

    result.setdefault(
        "object",
        "Unknown"
    )

    result.setdefault(
        "color",
        "Unknown"
    )

    result.setdefault(
        "type",
        "Unknown"
    )

    result.setdefault(
        "features",
        []
    )

    if not isinstance(
        result["features"],
        list
    ):
        result["features"] = []

    return result


# ==================================================
# 6. Validate AI result
# ==================================================

def validate_lost_found_result(result):
    """
    Validate and normalize AI-generated attributes.
    """

    if not isinstance(result, dict):
        return get_unknown_lost_found_result()

    object_name = result.get(
        "object",
        "Unknown"
    )

    color = result.get(
        "color",
        "Unknown"
    )

    item_type = result.get(
        "type",
        "Unknown"
    )

    features = result.get(
        "features",
        []
    )

    if not object_name:
        object_name = "Unknown"

    if not color:
        color = "Unknown"

    if not item_type:
        item_type = "Unknown"

    if not isinstance(features, list):
        features = []

    clean_features = []

    for feature in features:

        feature = str(
            feature
        ).strip()

        if feature:
            clean_features.append(
                feature
            )

    return {
        "object": str(
            object_name
        ).strip(),

        "color": str(
            color
        ).strip(),

        "type": str(
            item_type
        ).strip(),

        "features": clean_features
    }


# ==================================================
# 7. Analyze Lost & Found image
# ==================================================

def analyze_lost_found_item(image_path):
    """
    Analyze a Lost & Found image using Gemini.

    Args:
        image_path (str):
            Path to uploaded image.

    Returns:
        dict:
            object
            color
            type
            features
    """

    # ----------------------------------------------
    # Open and validate image
    # ----------------------------------------------

    try:
        image = Image.open(
            image_path
        )

    except FileNotFoundError:
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    except Exception as e:
        raise ValueError(
            f"Unable to open or validate image: {e}"
        )

    try:

        # ------------------------------------------
        # Send image to Gemini
        # ------------------------------------------

        response = client.models.generate_content(
            model="gemini-3.6-flash",

            contents=[
                LOST_FOUND_PROMPT,
                image
            ],

            config={
                "response_mime_type": "application/json",

                "response_schema": {
                    "type": "object",

                    "properties": {

                        "object": {
                            "type": "string"
                        },

                        "color": {
                            "type": "string"
                        },

                        "type": {
                            "type": "string"
                        },

                        "features": {
                            "type": "array",

                            "items": {
                                "type": "string"
                            }
                        }
                    },

                    "required": [
                        "object",
                        "color",
                        "type",
                        "features"
                    ]
                }
            }
        )

        # ------------------------------------------
        # Parse JSON response
        # ------------------------------------------

        result = parse_lost_found_result(
            response.text
        )

        # ------------------------------------------
        # Validate result
        # ------------------------------------------

        return validate_lost_found_result(
            result
        )

    finally:

        # ------------------------------------------
        # Always close image
        # ------------------------------------------

        image.close()


# ==================================================
# 8. Build searchable text
# ==================================================

def build_search_text(result):
    """
    Build searchable text from AI attributes.
    """

    result = validate_lost_found_result(
        result
    )

    parts = [
        result["object"],
        result["color"],
        result["type"]
    ]

    parts.extend(
        result["features"]
    )

    clean_parts = [
        part
        for part in parts
        if part
        and part.lower() != "unknown"
    ]

    return " ".join(
        clean_parts
    ).strip()


# ==================================================
# 9. Local helper test
# ==================================================

def main():

    sample = {
        "object": "backpack",
        "color": "black",
        "type": "college backpack",
        "features": [
            "front pocket",
            "two shoulder straps",
            "zipper"
        ]
    }

    validated = validate_lost_found_result(
        sample
    )

    print(
        "Lost & Found AI module loaded successfully."
    )

    print("\nValidated Result:")
    print(
        json.dumps(
            validated,
            indent=4
        )
    )

    print("\nSearch Text:")
    print(
        build_search_text(
            validated
        )
    )

    print("\nUnknown Fallback:")
    print(
        json.dumps(
            get_unknown_lost_found_result(),
            indent=4
        )
    )


# ==================================================
# 10. Run local test
# ==================================================

if __name__ == "__main__":
    main()