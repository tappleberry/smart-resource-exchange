import database

from ai.matching import find_best_matches


def main():

    # ----------------------------------------------
    # Get active lost reports
    # ----------------------------------------------

    lost_reports = database.get_lost_found_reports(
        report_type="lost"
    )

    # ----------------------------------------------
    # Get active found reports
    # ----------------------------------------------

    found_reports = database.get_lost_found_reports(
        report_type="found"
    )

    # ----------------------------------------------
    # Validate test data
    # ----------------------------------------------

    if not lost_reports:
        print("No lost reports found.")
        return

    if not found_reports:
        print("No found reports found.")
        return

    # ----------------------------------------------
    # Verify report directions
    # ----------------------------------------------

    invalid_lost_reports = [
        report
        for report in lost_reports
        if report["report_type"] != "lost"
    ]

    invalid_found_reports = [
        report
        for report in found_reports
        if report["report_type"] != "found"
    ]

    if invalid_lost_reports:
        print("ERROR: Non-lost report found in lost_reports.")
        return

    if invalid_found_reports:
        print("ERROR: Non-found report found in found_reports.")
        return

    print("Report direction check: PASS")

    # ----------------------------------------------
    # Use the latest lost report
    # ----------------------------------------------

    lost_report = lost_reports[0]

    # ----------------------------------------------
    # Find all potential matches
    # ----------------------------------------------

    matches = find_best_matches(
        lost_report,
        found_reports,
        minimum_score=0
    )

    # ----------------------------------------------
    # Verify every candidate is a found report
    # ----------------------------------------------

    invalid_matches = [
        match
        for match in matches
        if match["report"]["report_type"] != "found"
    ]

    if invalid_matches:
        print(
            "ERROR: Matching returned a non-found report."
        )
        return

    print("Candidate direction check: PASS")

    # ----------------------------------------------
    # Display lost report
    # ----------------------------------------------

    print("\nLost Report:")
    print("------------------")

    print(
        "ID       :",
        lost_report["id"]
    )

    print(
        "Title    :",
        lost_report["title"]
    )

    print(
        "Category :",
        lost_report["category"]
    )

    print(
        "Location :",
        lost_report["location"]
    )

    # ----------------------------------------------
    # Display matches
    # ----------------------------------------------

    print("\nPotential Matches:")
    print("------------------")

    if not matches:
        print("No potential matches found.")
        return

    for match in matches:

        report = match["report"]
        details = match["details"]

        print(
            f"ID: {report['id']} | "
            f"Title: {report['title']} | "
            f"Type: {report['report_type']} | "
            f"Score: {match['score']}% | "
            f"Level: {match['match_level']}"
        )

        print(
            "  Category:",
            details["category_score"],
            "| Color:",
            details["color_score"],
            "| Description:",
            details["description_score"],
            "| Location:",
            details["location_score"],
            "| Time:",
            details["time_score"]
        )


if __name__ == "__main__":
    main()