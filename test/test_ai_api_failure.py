import ai.lost_found as lost_found


class FakeModels:

    def generate_content(
        self,
        **kwargs
    ):
        raise RuntimeError(
            "Simulated Gemini API failure"
        )


class FakeClient:

    def __init__(self):
        self.models = FakeModels()


def main():

    original_client = lost_found.client

    try:

        lost_found.client = FakeClient()

        try:

            lost_found.analyze_lost_found_item(
                "uploads/Cycle_1.png"
            )

            print(
                "ERROR: Expected simulated API failure"
            )

        except RuntimeError as e:

            print(
                "Handled API error:",
                str(e)
            )

    finally:

        lost_found.client = original_client


if __name__ == "__main__":
    main()