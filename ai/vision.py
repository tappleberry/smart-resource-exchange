import os
import json

from dotenv import load_dotenv
from google import genai
from PIL import Image


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# --------------------------------------------------
# 2. Create Gemini client
# --------------------------------------------------

client = genai.Client(api_key=api_key)


# --------------------------------------------------
# 3. Analyze item image
# --------------------------------------------------

def analyze_item(image_path):
    """
    Analyze an item image using Gemini.

    Args:
        image_path (str): Path to the image file.

    Returns:
        dict: Structured item information containing:
            - item_name
            - category
            - condition
            - color
            - tags
            - description
            - suggested_price
    """

    # ----------------------------------------------
    # Open and validate image safely
    # ----------------------------------------------

    try:
        image = Image.open(image_path)

        # Check whether the file is a valid image
        image.verify()

        # verify() closes the image internally, so reopen it
        image = Image.open(image_path)

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

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    """
                    Analyze this image for a college campus marketplace.

                    Important rules:

                    1. Identify an item ONLY if a distinct physical item is
                       clearly visible and recognizable.

                    2. If the image is blurry, mostly a background, empty scene,
                       or the item cannot be identified reliably, do NOT guess.

                    3. For an unclear image:
                       - item_name = "Unclear Item"
                       - category = "Other"
                       - condition = "Unknown"
                       - color = "Unknown"
                       - tags = []
                       - description = "The uploaded image does not clearly show a recognizable item."
                       - suggested_price = 0

                    4. Never invent a specific brand or product model when it
                       is not clearly visible.

                    5. Return only valid JSON.
                    """,
                    image
                ],
                config={
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "object",
                        "properties": {
                            "item_name": {
                                "type": "string"
                            },
                            "category": {
                                "type": "string"
                            },
                            "condition": {
                                "type": "string"
                            },
                            "color": {
                                "type": "string"
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            },
                            "description": {
                                "type": "string"
                            },
                            "suggested_price": {
                                "type": "number"
                            }
                        },
                        "required": [
                            "item_name",
                            "category",
                            "condition",
                            "color",
                            "tags",
                            "description",
                            "suggested_price"
                        ]
                    }
                }
            )

        except Exception as e:

            error_message = str(e)

            # --------------------------------------
            # Handle Gemini quota / rate limit
            # --------------------------------------

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "quota" in error_message.lower()
            ):
                raise RuntimeError(
                    "Gemini API quota exceeded. "
                    "Please try again later."
                )

            # --------------------------------------
            # Handle other Gemini/API errors
            # --------------------------------------

            raise RuntimeError(
                f"Gemini API error: {error_message}"
            )

        # ------------------------------------------
        # Convert Gemini JSON to Python dictionary
        # ------------------------------------------

        try:
            result = json.loads(response.text)

        except json.JSONDecodeError as e:
            raise ValueError(
                f"Gemini returned invalid JSON: {e}"
            )

        return result

    finally:

        # ------------------------------------------
        # Always close image
        # ------------------------------------------

        image.close()


# --------------------------------------------------
# 4. Local testing
# --------------------------------------------------

def main():

    image_path = "uploads/calculator.png"

    try:

        result = analyze_item(image_path)

        print("\nAI ANALYSIS RESULT")
        print("------------------")

        print(
            json.dumps(
                result,
                indent=4
            )
        )

    except FileNotFoundError as e:

        print(e)

    except Exception as e:

        print("Error while analyzing image:")
        print(e)


# --------------------------------------------------
# 5. Run test only when this file is executed directly
# --------------------------------------------------

if __name__ == "__main__":
    main()