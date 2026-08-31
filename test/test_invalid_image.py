from ai.lost_found import analyze_lost_found_item


try:

    analyze_lost_found_item(
        "uploads/nonexistent_test_image.jpg"
    )

    print("ERROR: Expected FileNotFoundError")

except FileNotFoundError as e:

    print("Handled error:", type(e).__name__)
    print("Message:", str(e))

except Exception as e:

    print(
        "ERROR: Unexpected exception:",
        type(e).__name__
    )