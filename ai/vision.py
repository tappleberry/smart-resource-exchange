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
# 3. Analyze an item image
# --------------------------------------------------

def analyze_item(image_path):
    """
    Analyze an uploaded item image using Gemini.

    Returns:
        dict containing:
        - item_name
        - category
        - condition
        - color
        - tags
        - description
    """

    image = Image.open(image_path)

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                """
                Analyze this image as an item that could be listed
                on a college campus marketplace.

                Identify:
                1. item_name
                2. category
                3. condition
                4. color
                5. tags
                6. description

                Return only valid JSON.
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
                        }
                    },
                    "required": [
                        "item_name",
                        "category",
                        "condition",
                        "color",
                        "tags",
                        "description"
                    ]
                }
            }
        )

        # Convert JSON string returned by Gemini into Python dictionary
        result = json.loads(response.text)

        return result

    finally:
        image.close()


# --------------------------------------------------
# 4. Test the function directly
# --------------------------------------------------

if __name__ == "__main__":

    image_path = "uploads/calculator.png"

    try:
        result = analyze_item(image_path)

        print("\nAI ANALYSIS RESULT")
        print("------------------")

        print(json.dumps(result, indent=4))

    except FileNotFoundError:
        print(f"Image not found: {image_path}")

    except Exception as e:
        print("Error while analyzing image:")
        print(e)